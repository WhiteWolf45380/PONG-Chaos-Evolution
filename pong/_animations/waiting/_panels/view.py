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

    # ======================================== FOND ========================================
    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)