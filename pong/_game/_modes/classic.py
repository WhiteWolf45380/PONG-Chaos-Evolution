# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame
from .._objects import Ball, Paddle
from ._mode import Mode

# ======================================== MODE DE JEU ========================================
class Classic(Mode):
    """
    Mode de jeu : Classique

    Jeu de PONG basique
    """
    def __init__(self):
        # Initialisation du mode
        super().__init__("classic")

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