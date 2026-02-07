# ======================================== IMPORTS ========================================
from ..._core import pm
from .._objects import Ball, Paddle

# ======================================== MODE DE JEU ========================================
class Mode(pm.states.State):
    """Mode de jeu"""
    def __init__(self, name: str):
        # Initialisation de l'état
        super().__init__(f"{name}_mode", layer=1)
    
        # Pannel de vue
        self.view: pm.types.Panel = pm.panels["game_view"]

        # Objets
        self.ball: Ball = None
        self.paddle_0: Paddle = None
        self.paddle_1: Paddle = None

        # Paramètres dynamiques
        self.ended = False
        self.winner: int = None
        self.score: int = 0
    
    # ======================================== LANCEMENT ========================================
    def on_enter(self):
        """Lancement d'une partie"""
        # Balle
        self.ball = Ball(self.is_end)

        # Raquettes
        self.paddle_0 = Paddle(Paddle.OFFSET, self.view.centery)
        self.paddle_1 = Paddle(self.view.width - Paddle.OFFSET, self.view.centery)
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        if self.ended:
            self.end()
    
    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie après la collision d'un mur vertical"""
        return False

    def end(self):
        """Fin de partie"""
        print(f"La partie est terminée !")
        pm.stop()