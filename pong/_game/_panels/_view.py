# ======================================== IMPORTS ========================================
from ..._core import pm, pygame

# ======================================== MENU ========================================
class GameView(pm.panels.Panel):
    """
    Menu de vue du jeu
    """
    def __init__(self):
        super().__init__('game_view', rect=(0, 0, 1440, 1080), centered=True, border_width=3, border_color=(230, 230, 230))

        # fond
        self.background_color = (0, 0, 15)

    def draw(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)