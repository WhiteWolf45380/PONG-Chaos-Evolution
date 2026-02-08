# ======================================== IMPORTS ========================================
from ..._core import pm, ctx
from ._panels import LobbiesMenuView

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

        # Boutton de host
        self.host_button = pm.ui.RectButton(
            self.view.centerx,
            self.view.height * 0.8,
            200,
            80,
            anchor="center",
            text="Host",
            callback=self.host,
            panel="lobbies_menu_view"
        )

        # Bouton de join
        self.join_button = pm.ui.RectButton(
            self.view.centerx,
            self.view.height * 0.6,
            200,
            80,
            anchor="center",
            text="Join",
            callback=self.join,
            panel="lobbies_menu_view"
        )

        # Bouton de refresh
        self.join_button = pm.ui.RectButton(
            self.view.centerx,
            self.view.height * 0.4,
            200,
            80,
            anchor="center",
            text="Refresh",
            callback=self.refresh,
            panel="lobbies_menu_view"
        )

    def refresh(self):
        pm.network.update()
        print(pm.network.get_lobbies())

    def host(self):
        pm.network.host(name="Partie test", mode="classic")
        pm.states.activate("game", transition=True)
        ctx.modifiers.set("paddle_side", 0)

    def join(self):
        pm.network.join("192.168.1.22")
        pm.states.activate("game", transition=True)
        ctx.modifiers.set("paddle_side", 1)