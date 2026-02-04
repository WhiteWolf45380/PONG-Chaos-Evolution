# ======================================== IMPORTS ========================================
from ..._core import ctx, pm

# ======================================== ETAT ========================================
class Modes(pm.states.State):
    """
    Modification du mode de jeu
    """
    def __init__(self):
        super().__init__('modes_menu')

        self.all = ctx.game.modes.keys()
        self.selected = "wall_game"

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""