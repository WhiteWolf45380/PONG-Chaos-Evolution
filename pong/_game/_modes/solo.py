# ======================================== IMPORTS ========================================
from ..._core import pm

# ======================================== MODE DE JEU ========================================
class Solo:
    """Mode de jeu : Seul contre un IA"""
    def __init__(self):
        pass
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    def end(self, won: int = 0):
        """
        Fint de partie

        Args:
            won (int) : joueur gagnant (0 pour robot et 1 pour joueur)
        """
        print(f"La partie est terminée !\nVous avez {'gagné' if won == 1 else 'perdu'}")
        pm.stop()