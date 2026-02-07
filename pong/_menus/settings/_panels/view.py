# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class SettingsMenuView(pm.panels.Panel):
    """
    Panel de vue du menu des paramètres
    """
    def __init__(self, width : int = 1920, height : int = 1080):
        super().__init__('settings_menu_view', rect=(0, 0, width, height), centered=True)

        # Fond
        self.background_color = (20, 20, 30)

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)