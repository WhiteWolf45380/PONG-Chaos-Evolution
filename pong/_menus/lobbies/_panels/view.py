# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class LobbiesMenuView(pm.panels.Panel):
    """
    Panel de vue du menu des lobbies
    """
    def __init__(self, width : int = 1920, height : int = 1080):
        super().__init__('lobbies_menu_view', rect=(0, 0, width, height), centered=True)

        # Fond
        self.background_color = (40, 40, 60)

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)