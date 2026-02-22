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
        pm.settings.create("p1_up", pygame.K_z, category="inputs", widget="inputbutton")
        pm.settings.create("p1_down", pygame.K_s, category="inputs", widget="inputbutton")
        pm.settings.create("p2_up", pygame.K_UP, category="inputs", widget="inputbutton")
        pm.settings.create("p2_down", pygame.K_DOWN, category="inputs", widget="inputbutton")

        # Panel déroulant des paramètres
        self.parameters = pm.settings.Panel(
            name="settings_menu_parameters",
            predecessor=str(self.view),
            x=self.view.centerx,
            y=self.view.centery,
            width=1080,
            height=700,
            centered=True,
        )
        self.bind_panel(self.parameters.panel)
        self.parameters.activate()