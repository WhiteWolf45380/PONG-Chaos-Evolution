# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
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

        # Fond
        self.balls_n = 10
        self.balls = [BallObject() for _ in range(self.balls_n)]

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
        
        # Pseudo
        self.pseudo_text = pm.ui.Text(
            x=self.view.width * 0.1,
            y=self.view.height * 0.47,
            anchor="center",
            text="Pseudo",
            font="bahnschrift",
            font_size=30,
            font_color=(255, 255, 255),
            panel=str(self.view)
        )

        self.pseudo_case = pm.ui.TextCase(
            x=self.view.width * 0.1,
            y=self.view.height * 0.52,
            width=200,
            height=47,
            anchor="center",
            text="",
            placeholder="Guest",
            max_length=20,
            font="bahnschrift",
            font_size=28,
            font_color=(0, 0, 0),
            font_color_placeholder=(100, 100, 100),
            filling=True,
            filling_color=(180, 180, 180),
            filling_color_hover=(200, 200, 200),
            filling_color_focus=(255, 255, 255),
            border_width=2,
            border_color=(120, 120, 120),
            border_color_focus=(20, 60, 180),
            padding=10,
            callback=self.handle_pseudo,
            panel=str(self.view)
        )

        # Paramètres dynamique
        self.session_type = None
    
    def init(self):
        online_psd = ctx.modifiers["online_pseudo"]
        if online_psd is not None:
            self.pseudo_case.text = ctx.modifiers["online_pseudo"]
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    # ======================================== HOOKS ========================================
    def on_exit(self):
        self.pseudo_case.unfocus()
        return super().on_exit()
    
    # ======================================== HANDLERS ========================================
    def handle_solo(self):
        """Action du bouton Solo"""
        self.session_type = "solo"
        self.forward()
    
    def handle_local(self):
        """Action du bouton Local"""
        self.session_type = "local"
        self.forward()
    
    def handle_online(self):
        """Action du bouton Online"""
        self.session_type = "online"
        self.forward("lobbies_menu")
    
    def handle_settings(self):
        """Action du bouton Paramètres"""
        pm.states.activate("settings_menu", transition=True)
    
    def handle_quit(self):
        """Action du bouton Quitter"""
        pm.states.deactivate_all(fade_out=True)
    
    def handle_pseudo(self, pseudo: str):
        """Modification du pseudo"""
        if pseudo != "":
            ctx.modifiers.set("online_pseudo", pseudo)
        else:
            ctx.modifiers.set("online_pseudo", None)
    
    # ======================================== METHODES PUBLIQUES ========================================
    def forward(self, state: str = "modes_menu"):
        """Passe au menu suivant"""
        ctx.modes.load(self.session_type)
        ctx.game.set_session(self.session_type)
        pm.states.activate(state, transition=True)