# ======================================== IMPORTS ========================================
from ..._core import pm, pygame

# ======================================== PANEL ========================================
class GamePause(pm.panels.Panel):
    """
    Panel de vue du jeu
    """
    def __init__(self, width : int = 1440, height : int = 1080):
        # Initialisation du panel
        super().__init__('game_pause', predecessor='game_view', rect=(0, 0, width, height), centered=True, srcalpha=True)

        # Fond
        self.background: pm.types.SurfaceObject = pm.ui.Surface(
            x=0,
            y=0,
            width=width,
            height=height,
            color=(0, 0, 0, 150),
            panel=str(self),
            zorder=0,
        )

        # Text
        self.text: pm.types.TextObject = pm.ui.Text(
            x=self.centerx,
            y=self.centery,
            anchor="center",
            text="Partie en pause...",
            font_size=112,
            font_color=(255, 255, 255),
            shadow=True,
            panel=str(self),
            zorder=1
        )
        self.text.blink(alpha_min=0, alpha_max=255, speed=0.5, visible_time=1)

        # Bouton de retour à la partie
        self.resume_button: pm.types.RectButtonObject = pm.ui.RectButton(
            x=self.width * 0.4,
            y=self.height * 0.75,
            width=220,
            height=75,
            anchor="center",
            filling=True,
            filling_color=(60, 180, 75),
            filling_hover=True,
            filling_color_hover=(50, 150, 60),
            text=pm.languages("game_pause_resume"),
            font_size_ratio_limit=0.8,
            font_color=(255, 255, 255),
            font_color_hover=(220, 220, 0),
            border_radius=15,
            border_width=2,
            border_color=(80, 80, 80),
            border_color_hover=(60, 60, 60),
            hover_scale_ratio=0.97,
            hover_scale_duration=0.08,
            callback=self.handle_resume,
            panel=str(self),
            zorder=2
        )

        # Bouton de fin de partie
        self.leave_button: pm.types.RectButtonObject = pm.ui.RectButton(
            x=self.width * 0.6,
            y=self.height * 0.75,
            width=220,
            height=75,
            anchor="center",
            filling=True,
            filling_color=(180, 50, 50),
            filling_hover=True,
            filling_color_hover=(150, 40, 40),
            text=pm.languages("game_pause_leave"),
            font_size_ratio_limit=0.8,
            font_color=(255, 255, 255),
            font_color_hover=(220, 220, 0),
            border_radius=15,
            border_width=2,
            border_color=(80, 80, 80),
            border_color_hover=(60, 60, 60),
            hover_scale_ratio=0.97,
            hover_scale_duration=0.08,
            callback=self.handle_leave,
            panel=str(self),
            zorder=2
        )

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    def draw_back(self, surface: pygame.Surface):
        """Affichage du fond"""
        surface.fill((0, 0, 0, 0))
    
    # ======================================== HANDLERS ========================================
    def handle_resume(self):
        """Retour à la partie"""
        pm.states["game"].unpause()

    def handle_leave(self):
        """Quitte la partie"""
        pm.states.activate("main_menu", transition=True)