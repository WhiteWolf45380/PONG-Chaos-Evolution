# ======================================== IMPORTS ========================================
from __future__ import annotations
from numbers import Real
import torch
import torch.nn as nn
import random
import math
import collections
import numpy as np
import matplotlib.pyplot as plt

# ======================================== REPLAY BUFFER ========================================
class ReplayBuffer:
    def __init__(self, capacity: int = 50_000):
        self.buffer = collections.deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states,      dtype=np.float32),
            np.array(actions,     dtype=np.int64),
            np.array(rewards,     dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones,       dtype=np.float32),
        )

    def __len__(self):
        return len(self.buffer)


# ======================================== RÉSEAU ========================================
class DQNNet(nn.Module):
    """Dueling DQN — 3 actions : monter / rester / descendre."""
    def __init__(self, input_dim: int = 6, output_dim: int = 3, hidden: int = 128):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.value_stream = nn.Sequential(
            nn.Linear(hidden, 64), nn.ReLU(), nn.Linear(64, 1),
        )
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden, 64), nn.ReLU(), nn.Linear(64, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        shared    = self.shared(x)
        value     = self.value_stream(shared)
        advantage = self.advantage_stream(shared)
        return value + advantage - advantage.mean(dim=1, keepdim=True)


# ======================================== AGENT ========================================
class Bot(nn.Module):
    """
    Agent DQN — 3 actions avec pénalité d'oscillation
    """
    # [p2_y, ball_x, ball_y, ball_dx, ball_dy, delta_y]
    STATE_SCALE = np.array([1080.0, 1440.0, 1080.0, 1.0, 1.0, 1080.0], dtype=np.float32)
    ALIGNED_THRESHOLD = 30.0
    def __init__(
        self,
        lr: float               = 1e-3,
        gamma: float            = 0.99,
        epsilon_max: float      = 1.0,
        epsilon_min: float      = 0.05,
        epsilon_decay: float    = 0.995,
        batch_size: int         = 64,
        target_update_freq: int = 500,
        buffer_capacity: int    = 50_000,
        min_buffer_size: int    = 1_000,
        oscillation_penalty: float = 0.02,
        alignment_bonus:     float = 0.01,
    ):
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device : {self.device}")

        self.net        = DQNNet().to(self.device)
        self.target_net = DQNNet().to(self.device)
        self.target_net.load_state_dict(self.net.state_dict())
        self.target_net.eval()

        self.loss_fn   = nn.SmoothL1Loss()
        self.optimiser = torch.optim.Adam(self.net.parameters(), lr=lr)

        self.gamma               = gamma
        self.epsilon             = epsilon_max
        self.epsilon_min         = epsilon_min
        self.epsilon_decay       = epsilon_decay
        self.batch_size          = batch_size
        self.target_update_freq  = target_update_freq
        self.min_buffer_size     = min_buffer_size
        self.oscillation_penalty = oscillation_penalty
        self.alignment_bonus     = alignment_bonus

        self.buffer = ReplayBuffer(buffer_capacity)

        self.is_training   = False
        self.total_steps   = 0
        self.episode_count = 0
        self.all_losses:   list[float] = []
        self.all_scores:   list[float] = []

        self.load()

    # ------------------------------------------------------------------
    def _normalize(self, state: list | np.ndarray) -> np.ndarray:
        return np.array(state, dtype=np.float32) / self.STATE_SCALE

    def _build_state(self, p2_y, ball_x, ball_y, ball_dx, ball_dy) -> np.ndarray:
        delta_y = ball_y - p2_y
        return self._normalize([p2_y, ball_x, ball_y, ball_dx, ball_dy, delta_y])

    def get_move(self, p2_y: Real, ball_x: Real, ball_y: Real,
                 ball_dx: Real, ball_dy: Real) -> int:
        """Retourne -1 (monter), 0 (rester), +1 (descendre)"""
        state = self._build_state(p2_y, ball_x, ball_y, ball_dx, ball_dy)
        if self.is_training and random.random() < self.epsilon:
            action = random.randint(0, 2)
        else:
            t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            with torch.no_grad():
                action = int(torch.argmax(self.net(t)).item())
        return action - 1   # {0,1,2} → {-1,0,+1}

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    # ------------------------------------------------------------------
    def _learn_step(self):
        if len(self.buffer) < self.min_buffer_size:
            return None

        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)

        states      = torch.tensor(states,      device=self.device)
        next_states = torch.tensor(next_states, device=self.device)
        actions     = torch.tensor(actions,     device=self.device)
        rewards     = torch.tensor(rewards,     device=self.device)
        dones       = torch.tensor(dones,       device=self.device)

        q_values = self.net(states)
        q_value  = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            best_actions = self.net(next_states).argmax(dim=1, keepdim=True)
            next_q       = self.target_net(next_states).gather(1, best_actions).squeeze(1)
            target       = rewards + self.gamma * next_q * (1 - dones)

        loss = self.loss_fn(q_value, target)
        self.optimiser.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.net.parameters(), max_norm=10.0)
        self.optimiser.step()
        return loss.item()

    # ------------------------------------------------------------------
    def train_agent(self, env: "PongEnv", n_episodes: int = 1000):
        self.is_training = True
        window = 50

        for ep in range(n_episodes):
            self.episode_count += 1
            raw_state = env.reset()
            state     = self._build_state(*raw_state)
            done      = False
            total_reward  = 0.0
            ep_losses:    list[float] = []
            prev_move     = 0

            while not done:
                p2_y, ball_x, ball_y, ball_dx, ball_dy = raw_state
                action_move = self.get_move(p2_y, ball_x, ball_y, ball_dx, ball_dy)
                action_idx  = action_move + 1   # {-1,0,+1} → {0,1,2}

                raw_next, reward, done = env.step(action_move)
                next_state = self._build_state(*raw_next)
                _, _, ball_y_next, _, _ = raw_next

                # --- Pénalité d'oscillation ---
                if prev_move != 0 and action_move != 0 and action_move != prev_move:
                    reward -= self.oscillation_penalty

                # --- Bonus d'alignement ---
                delta_y = abs(ball_y - p2_y)
                if action_move == 0 and delta_y < self.ALIGNED_THRESHOLD:
                    reward += self.alignment_bonus

                prev_move = action_move

                self.buffer.push(state, action_idx, reward, next_state, done)
                self.total_steps += 1

                loss = self._learn_step()
                if loss is not None:
                    ep_losses.append(loss)

                if self.total_steps % self.target_update_freq == 0:
                    self.target_net.load_state_dict(self.net.state_dict())

                total_reward += reward
                state        = next_state
                raw_state    = raw_next

            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

            mean_loss = float(np.mean(ep_losses)) if ep_losses else 0.0
            self.all_scores.append(total_reward)
            self.all_losses.append(mean_loss)

            avg_score = float(np.mean(self.all_scores[-window:]))
            print(
                f"Ep {ep+1:>5}/{n_episodes} | "
                f"Score: {total_reward:>6.1f} | Avg({window}): {avg_score:>6.1f} | "
                f"ε: {self.epsilon:.4f} | Loss: {mean_loss:.4f} | "
                f"Buffer: {len(self.buffer):>6}"
            )

        self.is_training = False

    # ------------------------------------------------------------------
    def save(self, path: str = "data/bot.pth"):
        try:
            torch.save({
                "net":           self.net.state_dict(),
                "target_net":    self.target_net.state_dict(),
                "optimiser":     self.optimiser.state_dict(),
                "epsilon":       self.epsilon,
                "episode_count": self.episode_count,
                "total_steps":   self.total_steps,
            }, path)
            print(f"Modèle sauvegardé → {path}")
        except Exception as e:
            print(f"[Bot] Save error: {e}")

    def load(self, path: str = "data/bot.pth"):
        try:
            ckpt = torch.load(path, map_location=self.device)
            self.net.load_state_dict(ckpt["net"])
            self.target_net.load_state_dict(ckpt["target_net"])
            self.optimiser.load_state_dict(ckpt["optimiser"])
            self.epsilon        = ckpt["epsilon"]
            self.episode_count  = ckpt["episode_count"]
            self.total_steps    = ckpt["total_steps"]
            print(f"Modèle chargé ← {path}")
        except FileNotFoundError:
            print(f"[Bot] No save found at {path}")


# ======================================== ENVIRONNEMENT ========================================
class PongEnv:
    WIDTH  = 1440
    HEIGHT = 1080

    PADDLE_W     = 20
    PADDLE_H     = 120
    PADDLE_SPEED = 500 / 60
    PADDLE_X     = WIDTH - 50

    BALL_RADIUS           = 15
    BALL_SPEED_MIN        = 600  / 60
    BALL_SPEED_MAX        = 2400 / 60
    BALL_ACCEL_FRAMES     = 64   * 60
    BALL_ANGLE_MIN        = 15
    BALL_ANGLE_MAX        = 30
    BALL_BOUNCING_EPSILON = 5

    MAX_FRAMES = 3000

    def __init__(self):
        self.reset()

    def _random_angle_rad(self) -> float:
        return math.radians(random.uniform(self.BALL_ANGLE_MIN, self.BALL_ANGLE_MAX))

    def reset(self) -> list[float]:
        self.p2_y       = self.HEIGHT / 2
        self.ball_x     = self.WIDTH  / 2
        self.ball_y     = self.HEIGHT / 2
        self.ball_speed = float(self.BALL_SPEED_MIN)
        self.frame      = 0

        angle     = self._random_angle_rad()
        direction = random.choice([-1, 1])
        sign_y    = random.choice([-1, 1])
        self.ball_dx = direction * math.cos(angle)
        self.ball_dy = sign_y    * math.sin(angle)
        self.done = False
        return self._state()

    def _state(self) -> list[float]:
        return [self.p2_y, self.ball_x, self.ball_y, self.ball_dx, self.ball_dy]

    def step(self, action: int) -> tuple[list[float], float, bool]:
        """action ∈ {-1, 0, +1}"""
        if self.done:
            raise RuntimeError("Episode terminé. Appelez reset().")

        self.frame += 1
        t = min(self.frame / self.BALL_ACCEL_FRAMES, 1.0)
        self.ball_speed = self.BALL_SPEED_MIN + t * (self.BALL_SPEED_MAX - self.BALL_SPEED_MIN)

        # Paddle
        prev_dist = abs(self.ball_y - self.p2_y)
        self.p2_y += action * self.PADDLE_SPEED
        self.p2_y  = max(self.PADDLE_H / 2,
                         min(self.HEIGHT - self.PADDLE_H / 2, self.p2_y))
        new_dist = abs(self.ball_y - self.p2_y)

        # Balle
        self.ball_x += self.ball_dx * self.ball_speed
        self.ball_y += self.ball_dy * self.ball_speed

        reward = 0.0

        # Murs haut / bas
        if self.ball_y <= self.BALL_RADIUS:
            self.ball_y  = self.BALL_RADIUS
            self.ball_dy = abs(self.ball_dy)
            self.ball_dy = self._add_epsilon(self.ball_dy)
        elif self.ball_y >= self.HEIGHT - self.BALL_RADIUS:
            self.ball_y  = self.HEIGHT - self.BALL_RADIUS
            self.ball_dy = -abs(self.ball_dy)
            self.ball_dy = self._add_epsilon(self.ball_dy)

        # Mur gauche
        if self.ball_x <= self.BALL_RADIUS:
            self.ball_x  = self.BALL_RADIUS
            self.ball_dx = abs(self.ball_dx)

        # Collision paddle
        hitting_paddle = (
            self.ball_x + self.BALL_RADIUS >= self.PADDLE_X
            and self.ball_dx > 0
            and abs(self.ball_y - self.p2_y) <= self.PADDLE_H / 2
        )
        if hitting_paddle:
            self.ball_x  = self.PADDLE_X - self.BALL_RADIUS
            self.ball_dx = -abs(self.ball_dx)
            impact_ratio = (self.ball_y - self.p2_y) / (self.PADDLE_H / 2)
            self.ball_dy += impact_ratio * math.sin(math.radians(self.BALL_ANGLE_MAX))
            self.ball_dy  = self._add_epsilon(self.ball_dy)
            norm = math.hypot(self.ball_dx, self.ball_dy)
            if norm > 0:
                self.ball_dx /= norm
                self.ball_dy /= norm
            reward = 1.0

        # Balle perdue ou timeout
        if self.ball_x > self.WIDTH + self.BALL_RADIUS:
            self.done = True
            reward    = -1.0
        elif self.frame >= self.MAX_FRAMES:
            self.done = True

        # Récompense de proximité + bonus rapprochement
        if not self.done:
            dist_norm = abs(self.ball_y - self.p2_y) / (self.HEIGHT / 2)
            reward   += 0.02 * (1.0 - dist_norm)
            if new_dist < prev_dist:
                reward += 0.005

        return self._state(), reward, self.done

    def _add_epsilon(self, dy: float) -> float:
        eps_rad   = math.radians(random.uniform(-self.BALL_BOUNCING_EPSILON,
                                                 self.BALL_BOUNCING_EPSILON))
        sign      = math.copysign(1, dy)
        angle     = math.asin(max(-1.0, min(1.0, abs(dy))))
        new_angle = max(0.0, angle + eps_rad)
        return sign * math.sin(new_angle)


# ======================================== VISUALISATION ========================================
def plot_training(bot: Bot, window: int = 50):
    scores = np.array(bot.all_scores)
    losses = np.array(bot.all_losses)
    eps    = np.arange(1, len(scores) + 1)

    def rolling(arr, w):
        return np.convolve(arr, np.ones(w) / w, mode="valid")

    fig, axs = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("Entraînement DQN – Pong v3", fontsize=14)

    axs[0].plot(eps, scores, alpha=0.3, color="steelblue", label="Score brut")
    if len(scores) >= window:
        axs[0].plot(eps[window - 1:], rolling(scores, window),
                    color="steelblue", lw=2, label=f"Moyenne ({window} ep.)")
    axs[0].axhline(0, color="gray", linestyle="--", lw=0.8)
    axs[0].set_ylabel("Score"); axs[0].set_xlabel("Épisode")
    axs[0].set_title("Score par épisode"); axs[0].legend(); axs[0].grid(True, alpha=0.4)

    axs[1].plot(eps, losses, alpha=0.3, color="crimson", label="Loss brute")
    if len(losses) >= window:
        axs[1].plot(eps[window - 1:], rolling(losses, window),
                    color="crimson", lw=2, label=f"Moyenne ({window} ep.)")
    axs[1].set_ylabel("Huber Loss"); axs[1].set_xlabel("Épisode")
    axs[1].set_title("Loss moyenne par épisode"); axs[1].legend(); axs[1].grid(True, alpha=0.4)

    plt.tight_layout()
    plt.show()


# ======================================== MAIN ========================================
if __name__ == "__main__":
    try:
        bot = Bot(
            lr=1e-3,
            gamma=0.99,
            epsilon_max=1.0,
            epsilon_min=0.05,
            epsilon_decay=0.997,
            batch_size=64,
            target_update_freq=500,
            buffer_capacity=100_000,
            min_buffer_size=1_000,
            oscillation_penalty=0.02,
            alignment_bonus=0.01,
        )
        env = PongEnv()
        n_episodes = int(input("Nombre d'épisodes : "))
        bot.train_agent(env, n_episodes)
    finally:
        try:
            bot.save()
            plot_training(bot)
        except Exception:
            pass