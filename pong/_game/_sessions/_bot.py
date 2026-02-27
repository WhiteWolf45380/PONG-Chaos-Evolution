# ======================================== IMPORTS ========================================
from __future__ import annotations
from numbers import Real
import torch
import torch.nn as nn
import random
import math
import collections
import numpy as np

# ======================================== REPLAY BUFFER ========================================
class ReplayBuffer:
    """
    Mémoire de rejeu pour l'entraînement par batch
    """
    def __init__(self, capacity: int = 10_000):
        self.buffer = collections.deque(maxlen=capacity)

    def push(self, state: np.ndarray, target_y: float):
        """
        Ajoute une transition dans le buffer

        Args:
            state (np.ndarray): état normalisé [ball_x, ball_y, ball_dx, ball_dy]
            target_y (float): position Y cible normalisée (entre 0 et 1)
        """
        self.buffer.append((state, target_y))

    def sample(self, batch_size: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Tire un batch aléatoire depuis le buffer

        Args:
            batch_size (int): nombre d'échantillons à tirer

        Returns:
            Tuple (states, targets) sous forme de tableaux numpy float32
        """
        batch = random.sample(self.buffer, batch_size)
        states, targets = zip(*batch)
        return np.array(states, dtype=np.float32), np.array(targets, dtype=np.float32)

    def __len__(self) -> int:
        """Renvoie la taille du buffer"""
        return len(self.buffer)

# ======================================== RESEAU ========================================
class RegressionNet(nn.Module):
    """
    Réseau de régression : prédit la position Y d'arrivée de la balle (normalisée entre 0 et 1)
    """
    def __init__(self, input_dim: int = 4, hidden: int = 128):
        """
        Args:
            input_dim (int): dimension de l'entrée (4 : ball_x, ball_y, ball_dx, ball_dy)
            hidden (int): taille des couches cachées
        """
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden), nn.ReLU(),
            nn.Linear(hidden, hidden), nn.ReLU(),
            nn.Linear(hidden, 64), nn.ReLU(),
            nn.Linear(64, 1), nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Passage à travers le réseau"""
        return self.net(x)

# ======================================== BOT ========================================
class Bot(nn.Module):
    """
    Agent pong basé sur un réseau de régression
    Prédit la position Y d'arrivée de la balle et déplace la raquette en conséquence
    """
    HEIGHT = 1080.0                                                         # (float): hauteur du terrain en pixels
    CENTER = HEIGHT / 2                                                     # (float): centre vertical du terrain
    DEAD_ZONE = 25.0                                                        # (float): marge d'immobilité autour de la cible en pixels
    DIR_THRESHOLD = 0.001                                                   # (float): seuil de détection de changement de direction
    STATE_SCALE = np.array([1440.0, 1080.0, 1.0, 1.0], dtype=np.float32)    # (array): facteurs de normalisation de l'état

    def __init__(
        self,
        lr: float = 3e-4,
        batch_size: int = 64,
        buffer_capacity: int = 10_000,
        min_buffer_size: int = 50,
        grad_steps: int = 5,
        plateau_window: int = 100,
        plateau_threshold: float = 1.5,
        lr_decay: float = 0.1,
        lr_min: float = 1e-6,
    ):
        """
        Args:
            lr (float): taux d'apprentissage initial Adam
            batch_size (int): taille des batchs d'entraînement
            buffer_capacity (int): capacité maximale du replay buffer
            min_buffer_size (int): taille minimale du buffer avant d'apprendre
            grad_steps (int): nombre de passes de gradient par mise à jour
            plateau_window (int): fenêtre glissante pour la détection de plateau
            plateau_threshold (float): amélioration minimale pour ne pas déclencher le decay
            lr_decay (float): facteur multiplicatif appliqué au LR à chaque plateau (ex: 0.1 → ÷10)
            lr_min (float): LR plancher en dessous duquel on arrête d'apprendre
        """
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device : {self.device}")

        # Réseau et optimisation
        self.net = RegressionNet().to(self.device)
        self.loss_fn = nn.MSELoss()
        self.optimiser = torch.optim.Adam(self.net.parameters(), lr=lr)

        # Hyperparamètres
        self.lr_init = lr
        self.lr_decay = lr_decay
        self.lr_min = lr_min
        self.batch_size = batch_size
        self.min_buffer_size = min_buffer_size
        self.grad_steps = grad_steps
        self.buffer = ReplayBuffer(buffer_capacity)
        self.plateau_window = plateau_window
        self.plateau_threshold = plateau_threshold

        # État interne de jeu
        self.prev_dx: float = 0.0
        self.prev_dy: float = 0.0
        self.target_y: float|None = None

        # Suivi de l'entraînement
        self.converged_ep: int = 0
        self._decay_cooldown: int = 0
        self.episode_count: int = 0
        self.total_samples: int = 0
        self.all_losses: list[float] = []
        self.all_errors: list[float] = []
        self.all_scores: list[int] = []

        # Chargement si sauvegarde existante
        self.load()

    # ======================================== UTILITAIRES ========================================
    def _normalize(self, ball_x: float, ball_y: float, ball_dx: float, ball_dy: float) -> np.ndarray:
        """
        Normalise l'état brut de la balle

        Args:
            ball_x (float): position X de la balle
            ball_y (float): position Y de la balle
            ball_dx (float): direction X normalisée
            ball_dy (float): direction Y normalisée

        Returns:
            Tableau numpy float32 normalisé
        """
        return np.array([ball_x, ball_y, ball_dx, ball_dy], dtype=np.float32) / self.STATE_SCALE

    def _predict(self, ball_x: float, ball_y: float, ball_dx: float, ball_dy: float) -> float:
        """
        Prédit la position Y d'arrivée de la balle via le réseau

        Args:
            ball_x (float): position X de la balle
            ball_y (float): position Y de la balle
            ball_dx (float): direction X normalisée
            ball_dy (float): direction Y normalisée

        Returns:
            Position Y prédite en pixels
        """
        t = torch.tensor(
            self._normalize(ball_x, ball_y, ball_dx, ball_dy),
            dtype=torch.float32, device=self.device
        ).unsqueeze(0)
        with torch.no_grad():
            return self.net(t).item() * self.HEIGHT

    def _direction_changed(self, ball_dx: float, ball_dy: float) -> bool:
        """
        Détecte un changement de direction de la balle

        Args:
            ball_dx (float): direction X courante
            ball_dy (float): direction Y courante

        Returns:
            True si la direction a changé au-delà du seuil DIR_THRESHOLD
        """
        return (abs(ball_dx - self.prev_dx) > self.DIR_THRESHOLD or abs(ball_dy - self.prev_dy) > self.DIR_THRESHOLD)

    def _get_lr(self) -> float:
        """Renvoie le taux d'apprentissage courant de l'optimiseur"""
        return self.optimiser.param_groups[0]["lr"]

    def _check_plateau(self) -> bool:
        """
        Vérifie si l'erreur moyenne a atteint un plateau

        Returns:
            True si l'amélioration est inférieure à plateau_threshold
        """
        w = self.plateau_window
        if len(self.all_errors) < 2 * w:
            return False
        recent = float(np.mean(self.all_errors[-w:]))
        before = float(np.mean(self.all_errors[-2*w:-w]))
        return (before - recent) < self.plateau_threshold

    def _apply_lr_decay(self) -> float | None:
        """
        Réduit le taux d'apprentissage par lr_decay

        Returns:
            Nouveau taux d'apprentissage si un decay a été appliqué, None sinon
        """
        if self._decay_cooldown > 0:
            self._decay_cooldown -= 1
            return None
        if not self._check_plateau():
            return None
        current_lr = self._get_lr()
        new_lr = max(current_lr * self.lr_decay, self.lr_min)
        if new_lr == current_lr:
            return None
        for g in self.optimiser.param_groups:
            g["lr"] = new_lr
        self._decay_cooldown = self.plateau_window  # attend une fenêtre entière avant le prochain decay
        return new_lr

    # ======================================== DEPLACEMENT ========================================
    def reset(self):
        """Réinitialise l'état interne entre deux épisodes"""
        self.prev_dx  = 0.0
        self.prev_dy  = 0.0
        self.target_y = None

    def get_move(self, p2_y: Real, ball_x: Real, ball_y: Real, ball_dx: Real, ball_dy: Real) -> int:
        """
        Calcule le mouvement de la raquette pour un frame donné

        Args:
            p2_y (Real): position Y actuelle de la raquette
            ball_x (Real): position X de la balle
            ball_y (Real): position Y de la balle
            ball_dx (Real): direction X de la balle
            ball_dy (Real): direction Y de la balle

        Returns:
            -1 (monter) | 0 (immobile) | 1 (descendre)
        """
        if ball_dx < 0:
            goal = self.CENTER
        else:
            if self._direction_changed(ball_dx, ball_dy):
                self.prev_dx = ball_dx
                self.prev_dy = ball_dy
                if ball_dx > 0:
                    self.target_y = self._predict(ball_x, ball_y, ball_dx, ball_dy)
            goal = self.target_y if self.target_y is not None else self.CENTER
        if p2_y < goal - self.DEAD_ZONE:  return  1
        if p2_y > goal + self.DEAD_ZONE:  return -1
        return 0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Passage à travers le réseau"""
        return self.net(x)

    # ======================================== APPRENTISSAGE ========================================
    def _learn_steps(self) -> float | None:
        """
        Effectue `grad_steps` passes de gradient sur un batch aléatoire du buffer

        Returns:
            Perte MSE moyenne sur les passes effectuées, ou None si entraînement désactivé
        """
        if self._get_lr() < self.lr_min or len(self.buffer) < self.min_buffer_size:
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
        """
        Boucle d'entraînement principale

        Args:
            env (PongEnv): environnement de jeu
            n_episodes (int) : nombre maximum d'épisodes
        """
        window = 50

        for ep in range(n_episodes):
            self.episode_count += 1
            raw  = env.reset()
            done = False
            score = 0
            ep_losses: list[float] = []
            ep_errors: list[float] = []

            prev_dx, prev_dy = 0.0, 0.0
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
                if p2_y < pending_pred - self.DEAD_ZONE:    action =  1
                elif p2_y > pending_pred + self.DEAD_ZONE:  action = -1
                else:                                        action =  0

                raw_next, reward, done = env.step(action)

                if reward >= 1.0 or (done and reward <= -1.0):
                    if reward >= 1.0:
                        score += 1
                    if pending_state is not None:
                        actual_y = raw_next[2]
                        ep_errors.append(abs(actual_y - pending_pred))
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

            new_lr = self._apply_lr_decay()
            if new_lr is not None:
                if self.converged_ep == 0:
                    self.converged_ep = self.episode_count
                print(f"\n>>> Plateau ep {self.episode_count} "
                      f"- LR : {self._get_lr() / self.lr_decay:.2e} → {new_lr:.2e} "
                      f"| score moy: {avg_score:.1f} | err: {avg_error:.1f}px <<<\n")

            lr_str = f"{self._get_lr():.1e}"
            status = "✓" if self.converged_ep > 0 else "~"
            print(f"[{status}] {ep+1:>5}/{n_episodes} | "
                  f"Score: {score:>4} (moy {avg_score:>4.1f}) | "
                  f"Loss: {mean_loss:.5f} | Err: {avg_error:>5.1f}px | LR: {lr_str}")

    # ======================================== SAUVEGARDE ========================================
    def save(self, path: str = "_data/bot.pth"):
        """
        Sauvegarde le modèle et les métadonnées d'entraînement

        Args:
            path (str): chemin de destination du fichier
        """
        try:
            if __name__ == "__main__":
                path = f"pong/{path}"
            else:
                from ..._core import get_path
                path = get_path(path)
            torch.save({
                "net":           self.net.state_dict(),
                "optimiser":     self.optimiser.state_dict(),
                "episode_count": self.episode_count,
                "total_samples": self.total_samples,
                "converged_ep":  self.converged_ep,
            }, path)
            print(f"Sauvegarde -> {path}")
        except Exception as e:
            print(f"[Bot] Save error: {e}")

    def load(self, path: str = "_data/bot.pth"):
        """
        Charge le modèle et les métadonnées depuis un fichier .pth

        Args:
            path (str): chemin du fichier de sauvegarde
        """
        try:
            if __name__ == "__main__":
                path = f"pong/{path}"
            else:
                from ..._core import get_path
                path = get_path(path)
            ckpt = torch.load(path, map_location=self.device)
            self.net.load_state_dict(ckpt["net"])
            self.optimiser.load_state_dict(ckpt["optimiser"])
            self.episode_count = ckpt.get("episode_count", 0)
            self.total_samples = ckpt.get("total_samples", 0)
            self.converged_ep  = ckpt.get("converged_ep",  0)
            status = f"PLAY (premier plateau ep {self.converged_ep})" if self.converged_ep else "TRAIN"
            print(f"Charge <- {path} [{status}] | LR: {self._get_lr():.2e}")
        except FileNotFoundError:
            print(f"[Bot] No save found at {path}")


# ======================================== ENVIRONNEMENT ========================================
class PongEnv:
    """
    Environnement de pong simplifié pour l'entraînement de l'agent
    """
    WIDTH  = 1440                                                           # (int)  : largeur du terrain en pixels
    HEIGHT = 1080                                                           # (int)  : hauteur du terrain en pixels
    PADDLE_H = 110                                                          # (int)  : hauteur de la raquette en pixels
    PADDLE_SPEED = 700 / 60                                                 # (float): vitesse de la raquette en pixels/frame
    PADDLE_X = WIDTH - 50                                                   # (int)  : position X fixe de la raquette
    BALL_RADIUS = 15                                                        # (int)  : rayon de la balle en pixels
    BALL_SPEED_MIN = 600  / 60                                              # (float): vitesse initiale de la balle en pixels/frame
    BALL_SPEED_MAX = 2400 / 60                                              # (float): vitesse maximale de la balle en pixels/frame
    BALL_ACCEL_FRAMES = 64   * 60                                           # (int)  : durée de l'accélération en frames
    BALL_ANGLE_MIN = 15                                                     # (int)  : angle minimal de départ en degrés
    BALL_ANGLE_MAX = 30                                                     # (int)  : angle maximal de départ en degrés
    BALL_BOUNCING_EPSILON = 5                                               # (int)  : variation angulaire aléatoire sur les rebonds
    MAX_FRAMES = 3000                                                       # (int)  : durée maximale d'un épisode en frames

    def __init__(self):
        self.reset()

    def _random_angle_rad(self) -> float:
        """Tire un angle de départ aléatoire entre BALL_ANGLE_MIN et BALL_ANGLE_MAX"""
        return math.radians(random.uniform(self.BALL_ANGLE_MIN, self.BALL_ANGLE_MAX))

    def reset(self) -> list[float]:
        """
        Réinitialise l'environnement pour un nouvel épisode

        Returns:
            État initial [p2_y, ball_x, ball_y, ball_dx, ball_dy]
        """
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
        """Renvoie l'état courant de l'environnement"""
        return [self.p2_y, self.ball_x, self.ball_y, self.ball_dx, self.ball_dy]

    def step(self, action: int) -> tuple[list[float], float, bool]:
        """
        Avance d'un frame et applique l'action

        Args:
            action (int): -1 (monter) | 0 (immobile) | 1 (descendre)

        Returns:
            Tuple (state, reward, done)
            - reward = +1.0 si renvoi réussi, -1.0 si balle perdue, 0.0 sinon
            - done = True si l'épisode est terminé
        """
        if self.done:
            raise RuntimeError("Episode terminé")

        self.frame += 1
        t = min(self.frame / self.BALL_ACCEL_FRAMES, 1.0)
        self.ball_speed = self.BALL_SPEED_MIN + t * (self.BALL_SPEED_MAX - self.BALL_SPEED_MIN)

        # Déplacement raquette et balle
        self.p2_y += action * self.PADDLE_SPEED
        self.p2_y  = max(self.PADDLE_H / 2, min(self.HEIGHT - self.PADDLE_H / 2, self.p2_y))
        self.ball_x += self.ball_dx * self.ball_speed
        self.ball_y += self.ball_dy * self.ball_speed

        reward = 0.0

        # Rebonds haut / bas
        if self.ball_y <= self.BALL_RADIUS:
            self.ball_y  = self.BALL_RADIUS
            self.ball_dy = self._add_epsilon(abs(self.ball_dy))
        elif self.ball_y >= self.HEIGHT - self.BALL_RADIUS:
            self.ball_y  = self.HEIGHT - self.BALL_RADIUS
            self.ball_dy = -self._add_epsilon(abs(self.ball_dy))

        # Rebond gauche
        if self.ball_x <= self.BALL_RADIUS:
            self.ball_x  = self.BALL_RADIUS
            self.ball_dx = abs(self.ball_dx)

        # Collision avec la raquette avec anti-tunneling
        x0 = self.ball_x - self.ball_dx * self.ball_speed
        x1 = self.ball_x
        crossed_paddle = (
            self.ball_dx > 0
            and x0 + self.BALL_RADIUS < self.PADDLE_X
            and x1 + self.BALL_RADIUS >= self.PADDLE_X
        )
        if crossed_paddle:
            # Interpolation
            t = (self.PADDLE_X - self.BALL_RADIUS - (x0)) / (x1 - x0) if x1 != x0 else 1.0
            y_at_impact = self.ball_y - self.ball_dy * self.ball_speed * (1 - t)
            y_at_impact = max(self.BALL_RADIUS, min(self.HEIGHT - self.BALL_RADIUS, y_at_impact))
            if abs(y_at_impact - self.p2_y) <= self.PADDLE_H / 2:
                self.ball_x  = self.PADDLE_X - self.BALL_RADIUS
                self.ball_y  = y_at_impact
                self.ball_dx = -abs(self.ball_dx)

                impact_ratio = (self.ball_y - self.p2_y) / (self.PADDLE_H / 2)
                self.ball_dy += impact_ratio * math.sin(math.radians(self.BALL_ANGLE_MAX))
                self.ball_dy  = self._add_epsilon(self.ball_dy)

                norm = math.hypot(self.ball_dx, self.ball_dy)
                if norm > 0:
                    self.ball_dx /= norm
                    self.ball_dy /= norm

                # Clamp de l'angle
                angle     = math.asin(max(-1.0, min(1.0, abs(self.ball_dy))))
                angle_min = math.radians(self.BALL_ANGLE_MIN)
                angle_max = math.radians(self.BALL_ANGLE_MAX)
                angle     = max(angle_min, min(angle_max, angle))
                self.ball_dy = math.copysign(math.sin(angle), self.ball_dy)
                self.ball_dx = math.copysign(math.cos(angle), self.ball_dx)
                reward = 1.0

        # Fin d'épisode
        if self.ball_x > self.WIDTH + self.BALL_RADIUS:
            self.done = True
            reward    = -1.0
        elif self.frame >= self.MAX_FRAMES:
            self.done = True

        return self._state(), reward, self.done

    def _add_epsilon(self, dy: float) -> float:
        """
        Ajoute une perturbation angulaire aléatoire lors d'un rebond

        Args:
            dy (float): composante Y de la direction courante

        Returns:
            Nouvelle composante Y perturbée
        """
        eps_rad = math.radians(random.uniform(-self.BALL_BOUNCING_EPSILON, self.BALL_BOUNCING_EPSILON))
        sign = math.copysign(1, dy)
        angle = math.asin(max(-1.0, min(1.0, abs(dy))))
        new_angle = max(0.0, angle + eps_rad)
        return sign * math.sin(new_angle)

# ======================================== VISUALISATION ========================================
def plot_training(bot: Bot, window: int = 50):
    """
    Affiche les courbes de score, de loss et de précision sur l'ensemble de l'entraînement

    Args:
        bot (Bot): agent entraîné contenant les historiques
        window (int): taille de la fenêtre de moyenne glissante
    """
    scores = np.array(bot.all_scores, dtype=float)
    losses = np.array(bot.all_losses)
    errors = np.array(bot.all_errors)
    eps = np.arange(1, len(scores) + 1)

    def rolling(arr, w):
        return np.convolve(arr, np.ones(w) / w, mode="valid")

    fig, axs = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle("Pong — Regression v7", fontsize=14)

    axs[0].plot(eps, scores, alpha=0.25, color="steelblue")
    if len(scores) >= window:
        axs[0].plot(eps[window-1:], rolling(scores, window), color="steelblue", lw=2)
    axs[0].set_ylabel("Renvois"); axs[0].set_title("Score par épisode")
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
    axs[2].set_ylabel("Erreur px"); axs[2].set_title("Précision")
    axs[2].legend(); axs[2].grid(True, alpha=0.4)

    if bot.converged_ep > 0:
        for ax in axs:
            ax.axvline(bot.converged_ep, color="black", linestyle="--", lw=1.2,
                       label=f"Convergence ep {bot.converged_ep}")
        axs[0].legend()

    for ax in axs:
        ax.set_xlabel("Épisode")
    plt.tight_layout()
    plt.show()

# ======================================== ACTIVATION DIRECTE POUR ENTRAINEMENT ========================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
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
        n_episodes = int(input("Nombre d'épisodes : "))
        bot.train_agent(env, n_episodes)
    finally:
        try:
            bot.save()
            plot_training(bot)
        except Exception:
            pass