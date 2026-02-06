# ======================================== IMPORTS ========================================
from ..._core import pm, pygame, get_path

# ======================================== PANEL ========================================
class GameView(pm.panels.Panel):
    """
    Panel de vue du jeu
    """
    def __init__(self, width : int = 1440, height : int = 1080):
        super().__init__('game_view', rect=(0, 0, width, height), centered=True, border_width=3, border_color=(200, 200, 200), border_around=False)
        print(self._surface_rect)
        # Fond
        self.background_color = (0, 0, 15)

        # Décor
        self.art_color = (200, 200, 200)

        self.art_line = pm.entities.LineEntity(self.center, (0, 1), auto=False)
        self.art_line.width = 10
        self.art_line.color = self.art_color
        self.art_line.dashed = True
        self.art_line.dash *= 3
        self.art_line.gap *= 6
        self.art_line.freeze()

        self.art_text = pm.ui.Text(0, 0, "PONG", font_path=get_path("_assets/fonts/arcade.ttf"), font_size=124, font_color=self.art_color, background=self.background_color, anchor="center", auto=False)
        self.art_text.set_position(self.centerx + 9, self.centery)

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)
        self.art_line.draw(surface)
        surface.blit(self.art_text.surface, self.art_text.rect)