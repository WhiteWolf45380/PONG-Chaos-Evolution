# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class LobbiesMenuView(pm.panels.Panel):
    """
    Panel de vue du menu des lobbies
    """
    def __init__(self, width : int = 1280, height : int = 1080):
        super().__init__('lobbies_menu_view', rect=(0, 0, width, height), centered=True, border_width=3, border_color=(40, 45, 50), border_around=True)

        # Fond
        self.background_color = (50, 55, 60)

        # Titre
        self.title = pm.ui.Text(
            x=self.centerx,
            y=self.height * 0.04,
            anchor="midtop",
            text=pm.languages("lobbies_title"),
            font="davidclmmedium",
            font_size=96,
            font_color=(210, 225, 230),
            shadow=True,
            underline=True,
            panel=str(self),
        )

    # ======================================== FOND ========================================
    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)