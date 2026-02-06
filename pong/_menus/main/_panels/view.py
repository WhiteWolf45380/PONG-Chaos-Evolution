# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class MainMenuView(pm.panels.Panel):
    """
    Panel de vue du menu principal
    """
    def __init__(self, width : int = 1920, height : int = 1080):
        super().__init__('main_menu_view', rect=(0, 0, width, height), centered=True)

        # Fond
        self.background_color = (0, 0, 15)

        # Titre
        self.title = pm.ui.Text(
            x=self.centerx,
            y=self.height * 0.18,
            text="PONG : Chaos Evolution",
            font_color=(0, 255, 255),
            font_size=124,
            gradient=True,
            gradient_color=(255, 0, 255),
            gradient_direction="horizontal",
            gradient_fluctuation="sides",
            anchor="center",
            panel="main_menu_view"
            )

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)