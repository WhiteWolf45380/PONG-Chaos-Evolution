# ======================================== IMPORTS ========================================
from ..._core import pm, pygame
from ._panels import SettingsMenuView

# ======================================== ETAT ========================================
class Settings(pm.states.State):
    """
    Menu des paramètres
    """
    def __init__(self):
        # Initialisation de l'état
        super().__init__('settings_menu')

        # Panel de vue
        self.view = SettingsMenuView()
        self.bind_panel(self.view)

        # Paramètres
        pm.settings.create("p1_up", pygame.K_z)
        pm.settings.create("p1_down", pygame.K_s)
        pm.settings.create("p2_up", pygame.K_UP)
        pm.settings.create("p2_down", pygame.K_DOWN)