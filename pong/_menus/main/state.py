# ======================================== IMPORTS ========================================
from ..._core import pm
from ._panels import MainMenuView

# ======================================== ETAT ========================================
class Main(pm.states.State):
    """
    Menu principal
    """
    def __init__(self):
        # Initialisation de l'état
        super().__init__('main_menu')

        # Panel de vue
        self.view = MainMenuView()
        self.bind_panel(self.view)

        # Boutons
        self.buttons = {
            "play": None,
            "settings": None,
            "leave": None,
        }

        top = self.view.title.rect.bottom + self.view.height * 0.1
        bottom = self.view.height * 0.85
        buttons_space = abs(bottom - top) / len(self.buttons)
        buttons_height = buttons_space * 0.6
        buttons_width = buttons_height * 3
        for i, button in enumerate(self.buttons):
            self.buttons[button] = pm.ui.RectButton(
                x=self.view.centerx,
                y=top + i * buttons_space,
                width=buttons_width,
                height=buttons_height,
                anchor="midtop",
                filling=True,
                filling_color=(255, 255, 255, 10),
                text=pm.languages(f"main_{button}"),
                font_color=(255, 255, 255),
                font_color_hover=(240, 200, 0),
                border_width=3,
                border_color=(255, 255, 255),
                border_color_hover=(240, 200, 0),
                border_radius=int(buttons_height*0.2),
                hover_scale_ratio=1.05,
                hover_scale_duration=0.1,
                callback=getattr(self, f"handle_{button}", lambda: None),
                panel="main_menu_view",
            )
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        print(pm.time.fps)
    
    # ======================================== HANDLERS ========================================
    def handle_play(self):
        """Action du bouton Jouer"""
        pm.states.activate("game")
    
    def handle_settings(self):
        """Action du bouton Paramètres"""
        pm.states.activate("settings")
    
    def handle_leave(self):
        """Action du bouton Quitter"""
        pm.stop()