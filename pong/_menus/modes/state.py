# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame, get_path
from ._panels import ModesMenuView, ModesMenuChoices

# ======================================== ETAT ========================================
class Modes(pm.states.State):
    """
    Modification du mode de jeu
    """
    def __init__(self):
        # Initialisation de l'entité
        super().__init__('modes_menu')

        # Panel de vue
        self.view = ModesMenuView()
        self.bind_panel(self.view)

        # Panel des choix
        self.choices = ModesMenuChoices()
        self.bind_panel(self.choices)

        # Paramètres dynamiques
        self.selected = None

        # Boutton de retour
        self.back_button = pm.ui.CircleButton(
            x=self.view.width * 0.15,
            y=self.view.height * 0.92,
            radius=32,
            filling=True,
            filling_color=(10, 10, 30, 40),
            filling_color_hover=(10, 10, 30, 60),
            border_width=2,
            border_color=(0, 0, 0, 5),
            icon=pygame.image.load(get_path("_assets/icons/back.png")).convert_alpha(),
            icon_keep_ratio=True,
            icon_scale_ratio=0.6,
            hover_scale_ratio=1.05,
            hover_scale_duration=0.05,
            callback=self.handle_back,
            panel=str(self.view),
        )

        # Bouton de lancement
        self.start_button = pm.ui.RectButton(
            x=self.view.centerx,
            y=self.view.height * 0.92,
            width=300,
            height=90,
            anchor="center",
            filling_color=(10, 10, 30, 40),
            filling_color_hover=(10, 10, 30, 60),
            text=pm.languages("modes_select"),
            font_color=(255, 255, 255),
            font_color_hover=(230, 120, 20),
            border_width=3,
            border_color=(255, 255, 255), 
            border_color_hover=(230, 120, 20),
            border_radius=15,
            hover_scale_ratio=(1.03),
            hover_scale_duration=0.08,
            callback=self.handle_start,
            panel=str(self.view)
        )

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Activation de l'état"""
        ctx.engine.background.visible = True
        self.selected = None
        return super().on_enter()
    
    def on_exit(self):
        """Sortie de l'état"""
        ctx.engine.background.visible = False
        return super().on_exit()
    
    # ======================================== METHODES PUBLIQUES ========================================
    def load(self, session: str):
        """Charge un lot de modes adaptés à une session"""
        self.choices.load(session)
    
    # ======================================== HANDLERS ========================================
    def handle_back(self):
        """Retourne au menu précédent"""
        if ctx.main.session_type == "online":
            pm.states.activate("lobbies_menu", transition=True)
        else:
            pm.states.activate("main_menu", transition=True)

    def handle_start(self):
        """Démarre la partie"""
        selected = pm.ui.get_selected("mode")
        if selected is None:
            return
        self.selected = selected
        ctx.game.set_mode(selected)

        if ctx.main.session_type == "online":
            ctx.lobbies.start_host(selected)
        else:
            pm.states.activate("game", transition=True)