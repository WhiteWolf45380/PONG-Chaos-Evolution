# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame
from .._objects import Ball, Paddle

# ======================================== MODE DE JEU ========================================
class Local(pm.states.State):
    """Mode de jeu : 2 Joueurs"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("local", layer=1)

        # Panel de vue
        self.view = pm.panels["game_view"]
        
        # Objets
        self.ball = None
        self.paddle_0 = None
        self.paddle_1 = None

        # Paramètres dynamiques
        self.winner = None

    # ======================================== LANCEMENT ========================================
    def on_enter(self):
        """Lancement d'une partie"""
        # Balle
        self.ball = Ball(self.is_end)

        # Raquettes
        self.paddle_0 = Paddle(Paddle.OFFSET, self.view.centery, up=pygame.K_z, down=pygame.K_s)
        self.paddle_1 = Paddle(self.view.width - Paddle.OFFSET, self.view.centery, up=pygame.K_UP, down=pygame.K_DOWN)

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        if self.winner is not None:
            self.end()

    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie"""
        self.winner = 0 if side == 1 else 1
        return True

    def end(self):
        """
        Fint de partie

        Args:
            winner (int) : joueur gagnant (1 pour gauche et 2 pour droit)
        """
        print(f"La partie est terminée !\nLe gagnant est le joueur {self.winner}")
        pm.stop()