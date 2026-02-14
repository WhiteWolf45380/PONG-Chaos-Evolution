# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class WaitingAnimationView(pm.panels.Panel):
    """
    Panel de vue de l'animation d'attente
    """
    def __init__(self, width : int = 1080, height : int = 640):
        super().__init__('waiting_animation_view', rect=(0, 0, width, height), centered=True, border_width=3, border_color=(0, 0, 15), border_around=True)

        # Fond
        self.background_color = (7, 7, 20)

        # Text
        self.base_text = pm.languages("lobbies_search_text")
        self.text = pm.ui.Text(
            x=self.centerx,
            y=self.height * 0.25,
            anchor="center",
            text=self.base_text + '.',
            font="amiriquranregular",
            font_size=64,
            font_color=(255, 255, 255),
            shadow=True,
            gradient=True,
            gradient_color=(150, 150, 150),
            gradient_direction="diagonal",
            gradient_fluctuation=True,
            gradient_fluctuation_amplitude=0.5,
            gradient_fluctuation_speed=3.0,
            panel=str(self),
            zorder=1,
        )
        self.text.blink(speed=0.4, visible_time=2.0, alpha_min=30)
        self.text_total = 3
        self.text_index = 0
        self.text_duration = 1
        self.text_timer = 0.0

        # Nombre de joueurs
        self.players = 1
        self.players_max = 2
        self.players_text = pm.ui.Text(
            x=self.centerx,
            y=self.centery,
            anchor="midbottom",
            text=f"{self.players}/{self.players_max}",
            font="amiriquranregular",
            font_size=56,
            font_color=(255, 255, 255),
            shadow=True,
            panel=str(self),
            zorder=2
        )

    # ======================================== FOND ========================================
    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        self.text_timer += pm.time.dt
        if self.text_timer >= self.text_duration:
            self.text_index = (self.text_index + 1) % self.text_total
            self.text.text = f"{self.base_text}{'.' * (self.text_index + 1)}"
            self.text_timer = 0.0