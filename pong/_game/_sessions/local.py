# ======================================== IMPORTS ========================================
from ._session import Session
from ..._core import pm, ctx

# ======================================== MODE DE JEU ========================================
class Local(Session):
    """Type de session : Locale"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("local")

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self.current.player_2.set_status("friend")
        pm.inputs.add_listener(pm.settings["p2_up"], self.p2_move_up, repeat=True, condition=self.is_running)
        pm.inputs.add_listener(pm.settings["p2_down"], self.p2_move_down, repeat=True, condition=self.is_running)
    
    def on_enter(self):
        """Activation de l'état"""
        ctx.modifiers.set("p2_pseudo", "P2")
        return super().on_enter()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        if not super().update():
            return

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()
        pm.inputs.remove_listener(pm.settings["p2_up"], self.p2_move_up)
        pm.inputs.remove_listener(pm.settings["p2_down"], self.p2_move_down)