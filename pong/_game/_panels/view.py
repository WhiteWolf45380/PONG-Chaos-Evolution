# ======================================== IMPORTS ========================================
from ..._core import pm, pygame, get_path

# ======================================== PANEL ========================================
class GameView(pm.panels.Panel):
    """
    Panel de vue du jeu
    """
    def __init__(self, width : int = 1440, height : int = 1080):
        # Initialisation du panel
        super().__init__('game_view', rect=(0, 0, width, height), centered=True, border_width=3, border_color=(200, 200, 200), border_around=False)

        # Fond
        self.background_color = (0, 0, 15)

        # Décor
        self.art_color = (180, 185, 190)

        # line de séparation
        self.art_line = pm.entities.LineEntity(self.center, (0, 1), auto=False)
        self.art_line.width = 10
        self.art_line.color = self.art_color
        self.art_line.dashed = True
        self.art_line.dash *= 3
        self.art_line.gap *= 6
        self.art_line.freeze()

        # titre du jeu
        self.art_text = pm.ui.Text(
            x=self.centerx + 9,
            y=self.centery,
            text="PONG",
            anchor="center",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=124, font_color=self.art_color,
            background=self.background_color,
            auto=False
        )

        # scores
        self.s0 = 0
        self.s0_text = pm.ui.Text(
            x=self.width * 0.25,
            y=self.height * 0.15,
            text=str(self.s0),
            anchor="center",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=96,
            font_color=(200, 200, 200),
            auto=False,
        )

        self.s1 = 0
        self.s1_text = pm.ui.Text(
            x=self.width * 0.75,
            y=self.height * 0.15,
            text=str(self.s1),
            anchor="center",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=96,
            font_color=(200, 200, 200),
            auto=False,
        )

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        # Fond
        surface.fill(self.background_color)

        # Ligne de séparation
        self.art_line.draw(surface)

        # Titre du jeu
        surface.blit(self.art_text.surface, self.art_text.rect)

        # Scores
        s0 = getattr(pm.states.get_object(pm.states.get_active_by_layer(2)), 'score_0', 0)
        if self.s0 != s0:
            self.s0_text.text = str(s0)
            self.s0 = s0
        surface.blit(self.s0_text.surface, self.s0_text.rect)

        s1 = getattr(pm.states.get_object(pm.states.get_active_by_layer(2)), 'score_1', 0)
        if self.s1 != s1:
            self.s1_text.text = str(s1)
            self.s1 = s1
        surface.blit(self.s1_text.surface, self.s1_text.rect)