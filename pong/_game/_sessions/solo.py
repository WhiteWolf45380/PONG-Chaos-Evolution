# ======================================== IMPORTS ========================================
from ..._core import ctx
from ._session import Session

# ======================================== MODE DE JEU ========================================
class Solo(Session):
    """Type de session : Seul"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("solo")

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self.current.player_2.set_status("ennemy")

    def on_enter(self):
        """Activation de l'état"""
        ctx.modifiers.set("p2_pseudo", "Bot")
        return super().on_enter()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        super().update()

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()