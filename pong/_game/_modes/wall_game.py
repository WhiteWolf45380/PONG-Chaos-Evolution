# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame
from .._objects import Ball
from .._objects import Paddle

# ======================================== MODE DE JEU ========================================
class WallGame(pm.states.State):
    """Mode de jeu : Wall Game"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("wall_game", layer=1)

        # Pannel de vue
        self.view = pm.panels["game_view"]

        # Objets
        self.ball: Ball = None
        self.paddle_0: Paddle = None
        self.paddle_1: Paddle = None

        # Paramètres dynamiques
        self.score = 0
        
    def init(self):
        """Lancement d'une partie"""
        # Balle
        self.ball = Ball()

        # Raquettes
        if ctx.modifiers.paddle_side == 1:
            self.paddle_0 = None
            self.paddle_1 = Paddle(self.view.width - Paddle.OFFSET, self.view.centery, up=pygame.K_z, down=pygame.K_s)
        else:
            self.paddle_0 = Paddle(Paddle.OFFSET, self.view.centery, up=pygame.K_z, down=pygame.K_s)
            self.paddle_1 = None

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        pass

    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie"""
        if side != ctx.modifiers.paddle_side:
            self.score += 1
            return False
        return True

    def end(self):
        """
        Fin de partie

        Args:
            score (int) : le score du joueur
        """
        print(f"La partie est terminée !\n Score : {self.score}")
        pm.stop()