# ======================================== IMPORTS ========================================
from ..._core import pm

# ======================================== MODE DE JEU ========================================
class Local:
    """Mode de jeu : 2 Joueurs"""
    def __init__(self):
        pass

    # ======================================== ACTUALISATION ======================================== 
    def update(self):
        """Actualisation par frame"""

    def end(self, winner: int = 0):
        """
        Fint de partie

        Args:
            winner (int) : joueur gagnant (1 pour gauche et 2 pour droit)
        """
        print(f"La partie est terminée !\nLe gagnant est le joueur {winner}")
        pm.stop()