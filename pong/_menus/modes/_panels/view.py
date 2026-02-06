# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class ModesMenuView(pm.panels.Panel):
    """
    Panel de vue du menu de choix du mode de jeu
    """
    def __init__(self, width : int = 1440, height : int = 1080):
        super().__init__('modes_menu_view', rect=(0, 0, width, height), centered=True)

        # Fond
        self.background_color = (0, 0, 15)

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)