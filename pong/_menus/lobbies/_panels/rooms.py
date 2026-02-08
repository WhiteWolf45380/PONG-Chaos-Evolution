# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class LobbiesMenuRooms(pm.panels.Panel):
    """
    Panel de la liste des salons du menu des lobbies
    """
    def __init__(self, width : int = 1080, height : int = 700):
        super().__init__('lobbies_menu_rooms', predecessor='lobbies_menu_view', rect=(0, 0, width, height), centered=True, border_width=3, border_color=(50, 40, 30), border_around=True)

        # Fond
        self.background_color = (55, 50, 45)

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)