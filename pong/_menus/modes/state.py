# ======================================== IMPORTS ========================================
from ..._core import pm

# ======================================== ETAT ========================================
class Modes(pm.states.State):
    """
    Modification du mode de jeu
    """
    def __init__(self):
        super().__init__('modes_menu')

        self.selected = "wall_game"

    def init(self):
        """Chargement de l'état"""

    def update(self):
        """Actualisation par frame"""