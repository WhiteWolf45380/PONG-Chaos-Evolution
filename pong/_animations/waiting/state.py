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

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        pm.network.update()
        print(pm.network.is_connected)
        if pm.network.is_connected:
            self.start()

    # ======================================== START ========================================
    def start(self):
        """Fin de l'attente"""
        pm.states.activate("game", transition=True)

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Lancement de l'animation"""
        ctx.engine.background.visible = True
        return super().on_enter()

    def on_exit(self):
        """Fermeture de l'animation"""
        ctx.engine.background.visible = False
        return super().on_exit()