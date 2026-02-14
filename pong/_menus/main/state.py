# ======================================== IMPORTS ========================================
from ..._core import pm
from ._panels import MainMenuView
from ._objects import BallObject

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
            "solo": None,
            "local": None,
            "online": None,
            "settings": None,
            "quit": None,
        }

        top = self.view.title.rect.bottom + self.view.height * 0.08
        bottom = self.view.height * 0.96
        buttons_space = abs(bottom - top) / len(self.buttons)
        buttons_height = buttons_space * 0.7
        buttons_width = buttons_height * 3.6
        for i, button in enumerate(self.buttons):
            self.buttons[button] = pm.ui.RectButton(
                x=self.view.centerx,
                y=top + i * buttons_space,
                width=buttons_width,
                height=buttons_height,
                anchor="midtop",
                filling=True,
                filling_color=(10, 10, 25, 255),
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

        # Fond
        self.balls_n = 10
        self.balls = [BallObject() for _ in range(self.balls_n)]

        # Paramètres dynamique
        self.session_type = None
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    # ======================================== HANDLERS ========================================
    def handle_solo(self):
        """Action du bouton Solo"""
        self.session_type = "solo"
        pm.states.activate("game", transition=True)
    
    def handle_local(self):
        """Action du bouton Local"""
        self.session_type = "local"
        pm.states.activate("game", transition=True)
    
    def handle_online(self):
        """Action du bouton Online"""
        self.session_type = "online"
        pm.states.activate("lobbies_menu", transition=True)
    
    def handle_settings(self):
        """Action du bouton Paramètres"""
        pm.states.activate("settings_menu", transition=True)
    
    def handle_quit(self):
        """Action du bouton Quitter"""
        pm.stop()