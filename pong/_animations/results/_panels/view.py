# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class ResultsAnimationView(pm.panels.Panel):
    """
    Panel de vue de l'annonce des résultats
    """
    def __init__(self, width : int = 1920, height : int = 1080):
        super().__init__('results_animation_view', rect=(0, 0, width, height), centered=True)

        # Fond
        self.background_color = (5, 5, 10)

    # ======================================== FOND ========================================
    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)