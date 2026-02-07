# ======================================== IMPORTS ========================================
from ._session import Session

# ======================================== MODE DE JEU ========================================
class Online(Session):
    """Type de session : En ligne"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("online")

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        super().update()

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()