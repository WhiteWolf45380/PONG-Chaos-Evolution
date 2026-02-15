# ======================================== IMPORTS ========================================
from ..._core import pm, ctx, pygame, get_path
from ... import __version__
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
        self.rooms = LobbiesMenuRooms()
        self.bind_panel(self.rooms)

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
            panel=str(self.view),
        )

        # Boutton de host
        self.host_button = pm.ui.RectButton(
            x=self.view.centerx,
            y=self.view.height * 0.92,
            width=300,
            height=90,
            anchor="center",
            text=pm.languages("lobbies_host"),
            font_color=(200, 215, 220),
            font_color_hover=(220, 235, 240),
            underline=True,
            filling_color=(255, 255, 255, 15),
            filling_color_hover=(255, 255, 255, 25),
            border_width=3,
            border_color=(0, 0, 0, 10),
            border_color_hover=(0, 0, 0, 20),
            border_radius=20,
            hover_scale_ratio=1.03,
            hover_scale_duration=0.07,
            callback=self.handle_host,
            panel=str(self.view),
        )

        # Bouton de refresh
        self.refresh_button = pm.ui.RectButton(
            x=self.view.width * 0.85,
            y=self.view.height * 0.92,
            width=64,
            height=64,
            anchor="center",
            filling=True,
            filling_color=(255, 255, 255, 15),
            filling_hover=True,
            filling_color_hover=(255, 255, 255, 30),
            border_width=2,
            border_color=(0, 0, 0, 5),
            border_radius=10,
            icon=pygame.image.load(get_path("_assets/icons/refresh.png")),
            icon_keep_ratio=True,
            icon_scale_ratio=0.6,
            hover_scale_ratio=1.05,
            hover_scale_duration=0.05,
            callback=self.handle_refresh,
            panel=str(self.view),
        )

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de l'état"""

    # ======================================== HANDLERS ========================================
    def handle_back(self):
        """Retour au menu principal"""
        pm.states.activate("main_menu", transition=True)

    def handle_refresh(self):
        """Mise à jour de la liste des salons"""
        self.rooms.load(dict(pm.network.get_lobbies(version=__version__, status="open")))

    def handle_host(self):
        """Héberge un lobby"""
        pm.network.host(
            name="Partie test",
            mode="classic",
            host_side=ctx.modifiers.get("p1_side"),
            max_players=getattr(ctx.game.current_mode, 'max_players', 2),
            max_spectators=10,
            time=time(),
            version=__version__
        )
        pm.states.activate("waiting_animation", transition=True)
    
    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Ouverture du menu"""
        ctx.engine.background.visible = True
        self.handle_refresh()
        return super().on_enter()
    
    def on_exit(self):
        """Fermeture du menu"""
        ctx.engine.background.visible = False
        return super().on_exit()