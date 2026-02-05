# ======================================== IMPORTS ========================================
from ..._core import pm, pygame

# ======================================== MENU ========================================
class GameView(pm.panels.Panel):
    """
    Menu de vue du jeu
    """
    def __init__(self, width : int = 1440, height : int = 1080):
        super().__init__('game_view', rect=(0, 0, width, height), centered=True, border_width=3, border_color=(230, 230, 230), border_around=True)

        # fond
        self.background_color = (0, 0, 15)

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)