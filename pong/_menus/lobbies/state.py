# ======================================== IMPORTS ========================================
from ..._core import pm, ctx, pygame, get_path
from ._panels import LobbiesMenuView, LobbiesMenuRooms
from time import time

# ======================================== ETAT ========================================
class Lobbies(pm.states.State):
    """
    Menu principal
    """
    def __init__(self):
        # Initialisation de l'état
        super().__init__('lobbies_menu')

        # Panel de vue
        self.view = LobbiesMenuView()
        self.bind_panel(self.view)

        # Panel des salons
        self.list = LobbiesMenuRooms()

        # Boutton de retour
        self.back_button = pm.ui.CircleButton(
            x=self.view.width * 0.15,
            y=self.view.height * 0.92,
            radius=32,
            filling=True,
            filling_color=(255, 255, 255, 20),
            filling_color_hover=(255, 255, 255, 40),
            border_width=2,
            border_color=(0, 0, 0, 5),
            icon=pygame.image.load(get_path("_assets/icons/back.png")),
            icon_keep_ratio=True,
            icon_scale_ratio=0.6,
            hover_scale_ratio=1.05,
            hover_scale_duration=0.05,
            callback=self.handle_back,
            panel="lobbies_menu_view",
        )

        # Boutton de host
        self.host_button = pm.ui.RectButton(
            x=self.view.centerx,
            y=self.view.height * 0.92,
            width=300,
            height=90,
            anchor="center",
            text=pm.languages("lobbies_host"),
            font_color=(220, 215, 200),
            font_color_hover=(240, 235, 220),
            underline=True,
            filling_color=(90, 85, 80),
            filling_color_hover=(100, 95, 90),
            border_width=3,
            border_color=(0, 0, 0, 10),
            border_color_hover=(70, 63, 55),
            border_radius=20,
            hover_scale_ratio=1.03,
            hover_scale_duration=0.07,
            callback=self.handle_host,
            panel="lobbies_menu_view",
        )

        # Bouton de refresh
        self.refresh_button = pm.ui.RectButton(
            x=self.view.width * 0.85,
            y=self.view.height * 0.92,
            width=64,
            height=64,
            anchor="center",
            filling=True,
            filling_color=(255, 255, 255, 20),
            filling_hover=True,
            filling_color_hover=(255, 255, 255, 40),
            border_width=2,
            border_color=(0, 0, 0, 5),
            border_radius=10,
            icon=pygame.image.load(get_path("_assets/icons/refresh.png")),
            icon_keep_ratio=True,
            icon_scale_ratio=0.6,
            hover_scale_ratio=1.05,
            hover_scale_duration=0.05,
            callback=self.handle_refresh,
            panel="lobbies_menu_view",
        )

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de l'état"""

    # ======================================== HANDLERS ========================================
    def handle_back(self):
        """Retour au menu principal"""
        pm.states.activate("main_menu", transition=True)

    def handle_refresh(self):
        """Met à jour la liste des salons"""
        pm.network.update()
        print(pm.network.get_lobbies())

    def handle_host(self):
        """Héberge un lobby"""
        pm.network.host(name="Partie test", mode="classic", time=time())
        pm.states.activate("game", transition=True)
    
    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Ouverture du menu"""
        ctx.engine.background.visible = True
        return super().on_enter()
    
    def on_exit(self):
        """Fermeture du menu"""
        ctx.engine.background.visible = False
        return super().on_exit()