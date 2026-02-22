# ======================================== IMPORTS ========================================
from ...._core import pm, pygame

# ======================================== PANEL ========================================
class SettingsMenuView(pm.panels.Panel):
    """
    Panel de vue du menu des paramètres
    """
    def __init__(self, width : int = 1440, height : int = 1080):
        super().__init__('settings_menu_view', rect=(0, 0, width, height), centered=True)

        # Fond
        self.background_color = (0, 0, 15)

        # Titre
        self.title = pm.ui.Text(
            x=self.centerx,
            y=self.height * 0.04,
            anchor="midtop",
            text=pm.languages("settings_title"),
            font="davidclmmedium",
            font_size=96,
            font_color=(210, 225, 230),
            shadow=True,
            underline=True,
            panel=str(self),
        )

    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)