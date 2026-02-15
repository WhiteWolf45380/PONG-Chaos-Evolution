# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame, get_path

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
        self.art_color = (135, 130, 125)

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
            font_color=self.art_color,
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
            font_color=self.art_color,
            auto=False,
        )

        # Pseudos
        self.paddle0_pseudo = "P1"
        self.paddle0_text = pm.ui.Text(
            x=self.width * 0.25,
            y=self.height * 0.05,
            text=self.paddle0_pseudo,
            anchor="midtop",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=24,
            font_color=self.art_color,
            auto=False,
        )

        self.paddle1_pseudo = "P2"
        self.paddle1_text = pm.ui.Text(
            x=self.width * 0.75,
            y=self.height * 0.05,
            text=self.paddle1_pseudo,
            anchor="midtop",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=24,
            font_color=self.art_color,
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

        # Caractéristiques des joueurs
        max_players = getattr(pm.states["game"].current_mode, 'max_players', 2)

        # Scores
        if max_players >= 1:
            s0 = getattr(pm.states["game"].current_mode, 'score_0', None)
            if s0 is not None:
                if self.s0 != s0:
                    self.s0_text.text = str(s0)
                    self.s0 = s0
                surface.blit(self.s0_text.surface, self.s0_text.rect)

        if max_players >= 2:
            s1 = getattr(pm.states["game"].current_mode, 'score_1', None)
            if s1 is not None:
                if self.s1 != s1:
                    self.s1_text.text = str(s1)
                    self.s1 = s1
                surface.blit(self.s1_text.surface, self.s1_text.rect)
        
        # Pseudos
        paddle0 = 1 if ctx.modifiers.get("p1_side") == 0 else 2
        if paddle0 <= max_players:
            paddle0_pseudo = ctx.modifiers.get(f"p{paddle0}_pseudo", fallback=f'P{paddle0}')
            if paddle0_pseudo != self.paddle0_pseudo:
                self.paddle0_text.text = paddle0_pseudo
                self.paddle0_pseudo = paddle0_pseudo
            surface.blit(self.paddle0_text.surface, self.paddle0_text.rect)
        
        paddle1 = 2 if ctx.modifiers.get("p1_side") == 0 else 1
        if paddle1 <= max_players:
            paddle1_pseudo = ctx.modifiers.get(f"p{paddle1}_pseudo", fallback=f'P{paddle1}')
            if paddle1_pseudo != self.paddle1_pseudo:
                self.paddle1_text.text = paddle1_pseudo
                self.paddle1_pseudo = paddle1_pseudo
            surface.blit(self.paddle1_text.surface, self.paddle1_text.rect)