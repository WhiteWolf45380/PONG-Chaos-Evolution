from __future__ import annotations
from numbers import Real
import torch
import torch.nn as nn
import random
import math
import collections
import numpy as np
import matplotlib.pyplot as plt


class ReplayBuffer:
    def __init__(self, capacity: int = 10_000):
        self.buffer = collections.deque(maxlen=capacity)

    def push(self, state: np.ndarray, target_y: float):
        self.buffer.append((state, target_y))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        states, targets = zip(*batch)
        return np.array(states, dtype=np.float32), np.array(targets, dtype=np.float32)

    def __len__(self):
        return len(self.buffer)


class RegressionNet(nn.Module):
    def __init__(self, input_dim: int = 4, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden),   nn.ReLU(),
            nn.Linear(hidden, 64),       nn.ReLU(),
            nn.Linear(64, 1),            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class Bot(nn.Module):
    HEIGHT        = 1080.0
    CENTER        = HEIGHT / 2
    DEAD_ZONE     = 25.0
    DIR_THRESHOLD = 0.001
    STATE_SCALE   = np.array([1440.0, 1080.0, 1.0, 1.0], dtype=np.float32)

    def __init__(
        self,
        lr: float            = 3e-4,
        batch_size: int      = 64,
        buffer_capacity: int = 10_000,
        min_buffer_size: int = 50,
        grad_steps: int      = 5,
        plateau_window: int      = 100,
        plateau_threshold: float = 1.5,
    ):
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device : {self.device}")

        self.net       = RegressionNet().to(self.device)
        self.loss_fn   = nn.MSELoss()
        self.optimiser = torch.optim.Adam(self.net.parameters(), lr=lr)

        self.batch_size       = batch_size
        self.min_buffer_size  = min_buffer_size
        self.grad_steps       = grad_steps
        self.buffer           = ReplayBuffer(buffer_capacity)
        self.plateau_window    = plateau_window
        self.plateau_threshold = plateau_threshold

        self.prev_dx:  float      = 0.0
        self.prev_dy:  float      = 0.0
        self.target_y: float|None = None

        self.is_training:  bool = True
        self.converged_ep: int  = 0

        self.episode_count: int       = 0
        self.total_samples: int       = 0
        self.all_losses: list[float]  = []
        self.all_errors: list[float]  = []
        self.all_scores: list[int]    = []

        self.load()

    def _normalize(self, ball_x, ball_y, ball_dx, ball_dy) -> np.ndarray:
        return np.array([ball_x, ball_y, ball_dx, ball_dy], dtype=np.float32) / self.STATE_SCALE

    def _predict(self, ball_x, ball_y, ball_dx, ball_dy) -> float:
        t = torch.tensor(self._normalize(ball_x, ball_y, ball_dx, ball_dy),
                         dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            return self.net(t).item() * self.HEIGHT

    def _direction_changed(self, ball_dx: float, ball_dy: float) -> bool:
        return (abs(ball_dx - self.prev_dx) > self.DIR_THRESHOLD or
                abs(ball_dy - self.prev_dy) > self.DIR_THRESHOLD)

    def _check_plateau(self) -> bool:
        w = self.plateau_window
        if len(self.all_errors) < 2 * w:
            return False
        recent = float(np.mean(self.all_errors[-w:]))
        before = float(np.mean(self.all_errors[-2*w:-w]))
        return (before - recent) < self.plateau_threshold

    def get_move(self, p2_y: Real, ball_x: Real, ball_y: Real,
                 ball_dx: Real, ball_dy: Real) -> int:
        if self._direction_changed(ball_dx, ball_dy):
            self.prev_dx  = ball_dx
            self.prev_dy  = ball_dy
            if ball_dx > 0:
                self.target_y = self._predict(ball_x, ball_y, ball_dx, ball_dy)
            else:
                self.target_y = self.CENTER

        goal = self.target_y if self.target_y is not None else self.CENTER
        if p2_y < goal - self.DEAD_ZONE:   return 1
        if p2_y > goal + self.DEAD_ZONE:   return -1
        return 0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def _learn_steps(self) -> float | None:
        if not self.is_training or len(self.buffer) < self.min_buffer_size:
            return None
        losses = []
        for _ in range(self.grad_steps):
            bs = min(self.batch_size, len(self.buffer))
            states, targets = self.buffer.sample(bs)
            states  = torch.tensor(states,  device=self.device)
            targets = torch.tensor(targets, device=self.device).unsqueeze(1)
            loss = self.loss_fn(self.net(states), targets)
            self.optimiser.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.net.parameters(), max_norm=5.0)
            self.optimiser.step()
            losses.append(loss.item())
        return float(np.mean(losses))

    def train_agent(self, env, n_episodes: int = 500):
        window = 50

        for ep in range(n_episodes):
            self.episode_count += 1
            raw  = env.reset()
            done = False
            score            = 0
            ep_losses:  list[float] = []
            ep_errors:  list[float] = []
            prev_dx, prev_dy = raw[3], raw[4]
            pending_state    = None
            pending_pred     = self.CENTER

            while not done:
                _, ball_x, ball_y, ball_dx, ball_dy = raw

                if (ball_dx, ball_dy) != (prev_dx, prev_dy):
                    prev_dx, prev_dy = ball_dx, ball_dy
                    if ball_dx > 0:
                        pending_state = self._normalize(ball_x, ball_y, ball_dx, ball_dy)
                        pending_pred  = self._predict(ball_x, ball_y, ball_dx, ball_dy)

                p2_y = raw[0]
                if p2_y < pending_pred - self.DEAD_ZONE:   action = 1
                elif p2_y > pending_pred + self.DEAD_ZONE: action = -1
                else:                                       action = 0

                raw_next, reward, done = env.step(action)

                if reward >= 1.0 or (done and reward <= -1.0):
                    if reward >= 1.0:
                        score += 1
                    if pending_state is not None:
                        actual_y = raw_next[2]
                        ep_errors.append(abs(actual_y - pending_pred))
                        if self.is_training:
                            self.buffer.push(pending_state, actual_y / self.HEIGHT)
                            self.total_samples += 1
                        pending_state = None
                        loss = self._learn_steps()
                        if loss is not None:
                            ep_losses.append(loss)

                raw = raw_next

            mean_loss  = float(np.mean(ep_losses)) if ep_losses else 0.0
            mean_error = float(np.mean(ep_errors)) if ep_errors else 0.0
            self.all_losses.append(mean_loss)
            self.all_errors.append(mean_error)
            self.all_scores.append(score)

            avg_error = float(np.mean(self.all_errors[-window:]))
            avg_score = float(np.mean(self.all_scores[-window:]))

            if self.is_training and self._check_plateau():
                self.is_training  = False
                self.converged_ep = self.episode_count
                print(f"\n>>> Convergence ep {self.converged_ep} "
                      f"— score moy: {avg_score:.1f} | err: {avg_error:.1f}px <<<\n")

            status = "~" if self.is_training else "✓"
            print(f"[{status}] {ep+1:>5}/{n_episodes} | "
                  f"Score: {score:>4} (moy {avg_score:>4.1f}) | "
                  f"Loss: {mean_loss:.5f} | Err: {avg_error:>5.1f}px")

    def save(self, path: str = "data/bot.pth"):
        try:
            torch.save({
                "net":           self.net.state_dict(),
                "optimiser":     self.optimiser.state_dict(),
                "episode_count": self.episode_count,
                "total_samples": self.total_samples,
                "is_training":   self.is_training,
                "converged_ep":  self.converged_ep,
            }, path)
            print(f"Sauvegarde -> {path}")
        except Exception as e:
            print(f"[Bot] Save error: {e}")

    def load(self, path: str = "data/bot.pth"):
        try:
            ckpt = torch.load(path, map_location=self.device)
            self.net.load_state_dict(ckpt["net"])
            self.optimiser.load_state_dict(ckpt["optimiser"])
            self.episode_count = ckpt.get("episode_count", 0)
            self.total_samples = ckpt.get("total_samples", 0)
            self.is_training   = ckpt.get("is_training",   True)
            self.converged_ep  = ckpt.get("converged_ep",  0)
            status = "TRAIN" if self.is_training else f"PLAY (converge ep {self.converged_ep})"
            print(f"Charge <- {path} [{status}]")
        except FileNotFoundError:
            print(f"[Bot] No save found at {path}")


class PongEnv:
    WIDTH  = 1440
    HEIGHT = 1080
    PADDLE_H     = 85
    PADDLE_SPEED = 500 / 60
    PADDLE_X     = WIDTH - 50
    BALL_RADIUS           = 15
    BALL_SPEED_MIN        = 600  / 60
    BALL_SPEED_MAX        = 2400 / 60
    BALL_ACCEL_FRAMES     = 64   * 60
    BALL_ANGLE_MIN        = 15
    BALL_ANGLE_MAX        = 30
    BALL_BOUNCING_EPSILON = 5
    MAX_FRAMES            = 3000

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
        angle           = self._random_angle_rad()
        direction       = random.choice([-1, 1])
        sign_y          = random.choice([-1, 1])
        self.ball_dx    = direction * math.cos(angle)
        self.ball_dy    = sign_y    * math.sin(angle)
        self.done       = False
        return self._state()

    def _state(self) -> list[float]:
        return [self.p2_y, self.ball_x, self.ball_y, self.ball_dx, self.ball_dy]

    def step(self, action: int) -> tuple[list[float], float, bool]:
        if self.done:
            raise RuntimeError("Episode termine. Appelez reset().")
        self.frame += 1
        t = min(self.frame / self.BALL_ACCEL_FRAMES, 1.0)
        self.ball_speed = self.BALL_SPEED_MIN + t * (self.BALL_SPEED_MAX - self.BALL_SPEED_MIN)

        self.p2_y += action * self.PADDLE_SPEED
        self.p2_y  = max(self.PADDLE_H / 2, min(self.HEIGHT - self.PADDLE_H / 2, self.p2_y))
        self.ball_x += self.ball_dx * self.ball_speed
        self.ball_y += self.ball_dy * self.ball_speed

        reward = 0.0
        if self.ball_y <= self.BALL_RADIUS:
            self.ball_y  = self.BALL_RADIUS
            self.ball_dy = self._add_epsilon(abs(self.ball_dy))
        elif self.ball_y >= self.HEIGHT - self.BALL_RADIUS:
            self.ball_y  = self.HEIGHT - self.BALL_RADIUS
            self.ball_dy = -self._add_epsilon(abs(self.ball_dy))

        if self.ball_x <= self.BALL_RADIUS:
            self.ball_x  = self.BALL_RADIUS
            self.ball_dx = abs(self.ball_dx)

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

        if self.ball_x > self.WIDTH + self.BALL_RADIUS:
            self.done = True
            reward    = -1.0
        elif self.frame >= self.MAX_FRAMES:
            self.done = True

        return self._state(), reward, self.done

    def _add_epsilon(self, dy: float) -> float:
        eps_rad   = math.radians(random.uniform(-self.BALL_BOUNCING_EPSILON,
                                                 self.BALL_BOUNCING_EPSILON))
        sign      = math.copysign(1, dy)
        angle     = math.asin(max(-1.0, min(1.0, abs(dy))))
        new_angle = max(0.0, angle + eps_rad)
        return sign * math.sin(new_angle)


def plot_training(bot: Bot, window: int = 50):
    scores = np.array(bot.all_scores, dtype=float)
    losses = np.array(bot.all_losses)
    errors = np.array(bot.all_errors)
    eps    = np.arange(1, len(scores) + 1)

    def rolling(arr, w):
        return np.convolve(arr, np.ones(w) / w, mode="valid")

    fig, axs = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle("Pong — Regression v7", fontsize=14)

    axs[0].plot(eps, scores, alpha=0.25, color="steelblue")
    if len(scores) >= window:
        axs[0].plot(eps[window-1:], rolling(scores, window), color="steelblue", lw=2)
    axs[0].set_ylabel("Renvois"); axs[0].set_title("Score par episode")
    axs[0].grid(True, alpha=0.4)

    axs[1].plot(eps, losses, alpha=0.25, color="crimson")
    if len(losses) >= window:
        axs[1].plot(eps[window-1:], rolling(losses, window), color="crimson", lw=2)
    axs[1].set_ylabel("MSE Loss"); axs[1].set_title("Loss")
    axs[1].grid(True, alpha=0.4)

    axs[2].plot(eps, errors, alpha=0.25, color="darkorange")
    if len(errors) >= window:
        axs[2].plot(eps[window-1:], rolling(errors, window), color="darkorange", lw=2)
    axs[2].axhline(42, color="green",  linestyle="--", lw=1, label="PADDLE_H/2 = 42px")
    axs[2].axhline(25, color="purple", linestyle="--", lw=1, label="DEAD_ZONE = 25px")
    axs[2].set_ylabel("Erreur px"); axs[2].set_title("Precision")
    axs[2].legend(); axs[2].grid(True, alpha=0.4)

    if bot.converged_ep > 0:
        for ax in axs:
            ax.axvline(bot.converged_ep, color="black", linestyle="--", lw=1.2,
                       label=f"Convergence ep {bot.converged_ep}")
        axs[0].legend()

    for ax in axs:
        ax.set_xlabel("Episode")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    try:
        bot = Bot(
            lr=3e-4,
            batch_size=64,
            buffer_capacity=10_000,
            min_buffer_size=50,
            grad_steps=5,
            plateau_window=100,
            plateau_threshold=1.5,
        )
        env = PongEnv()
        n_episodes = int(input("Episodes (arret auto si convergence) : "))
        bot.train_agent(env, n_episodes)
    finally:
        try:
            bot.save()
            plot_training(bot)
        except Exception:
            pass