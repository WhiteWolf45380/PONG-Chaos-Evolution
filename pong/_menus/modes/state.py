# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from ._panels import ModesMenuView

# ======================================== ETAT ========================================
class Modes(pm.states.State):
    """
    Modification du mode de jeu
    """
    def __init__(self):
        # Initialisation de l'entité
        super().__init__('modes_menu')

        # Panel de vue
        self.view = ModesMenuView
        self.bind_panel(self.view)

        # Modes de jeu
        self.all = ctx.game.modes.keys()
        self.selected = "wall_game"

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""