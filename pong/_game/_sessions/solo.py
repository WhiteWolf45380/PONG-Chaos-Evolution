# ======================================== IMPORTS ========================================
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

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        super().update()

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()