# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame
from .._objects import Ball, Paddle

# ======================================== MODE DE JEU ========================================
class Solo(pm.states.State):
    """Mode de jeu : Seul contre un IA"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("solo", layer=1)
    
        # Pannel de vue
        self.view = pm.panels["game_view"]

        # Objets
        self.ball: Ball = None
        self.paddle_0: Paddle = None
        self.paddle_1: Paddle = None

        # Paramètres dynamiques
        self.winner = None
    
    # ======================================== LANCEMENT ========================================
    def on_enter(self):
        """Lancement d'une partie"""
        # Balle
        self.ball = Ball(self.is_end)

        # Raquette
        if ctx.paddle_side == 1:
            self.paddle_0 = None
            self.paddle_1 = Paddle(self.view.width - Paddle.OFFSET, self.view.centery, up=pygame.K_z, down=pygame.K_s)
        else:
            self.paddle_0 = Paddle(Paddle.OFFSET, self.view.centery, up=pygame.K_z, down=pygame.K_s)
            self.paddle_1 = None

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
            won (int) : joueur gagnant (0 pour robot et 1 pour joueur)
        """
        print(f"La partie est terminée !\nVous avez {'gagné' if self.winner == ctx.modifiers.paddle_side else 'perdu'}")
        pm.stop()