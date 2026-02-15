# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from ._panels import WaitingAnimationView

# ======================================== ETAT ========================================
class Waiting(pm.states.State):
    """
    Animation d'attente
    """
    def __init__(self):
        # Initialisation de l'état
        super().__init__('waiting_animation')

        # Panel de vue
        self.view = WaitingAnimationView()
        self.bind_panel(self.view)

        # Bouton d'annulation
        self.cancel_button = pm.ui.RectButton(
            x=self.view.centerx,
            y=self.view.height * 0.8,
            width=200,
            height=80,
            anchor="center",
            filling_color=(10, 10, 25),
            filling_color_hover=(20, 20, 50),
            text=pm.languages("lobbies_search_cancel"),
            font="reemkufi",
            font_color=(255, 255, 255),
            font_color_hover=(200, 150, 0),
            border_radius=15,
            border_width=2,
            border_color=(255, 255, 255),
            border_color_hover=(180, 180, 0),
            hover_scale_ratio=1.04,
            hover_scale_duration=0.1,
            callback=self.handle_cancel,
            panel=str(self.view),
            zorder=3,
        )

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        pm.network.update()
        if pm.network.is_game_started():
            self.handle_start()

    # ======================================== HANDLERS ========================================
    def handle_start(self):
        """Fin de l'attente"""
        pm.states.activate("game", transition=True)
    
    def handle_cancel(self):
        """Annuler de la recherche"""
        if pm.network._connected:
            pm.network.disconnect()
        pm.states.activate("lobbies_menu", transition=True)

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Lancement de l'animation"""
        ctx.engine.background.visible = True
        return super().on_enter()

    def on_exit(self):
        """Fermeture de l'animation"""
        ctx.engine.background.visible = False
        return super().on_exit()