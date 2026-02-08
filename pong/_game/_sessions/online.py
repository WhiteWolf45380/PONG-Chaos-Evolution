# ======================================== IMPORTS ========================================
from ._session import Session
from    ..._core import pm, ctx

# ======================================== MODE DE JEU ========================================
class Online(Session):
    """Type de session : En ligne"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("online")
        self._is_host = pm.network.is_host
        self._connected = pm.network.is_connected

    def on_enter(self):
        return super().on_enter()

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self._is_host = pm.network.is_host
        self._connected = pm.network.is_connected
        print(f"[Online] Start session | Host: {self._is_host}, Connected: {self._connected}")

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        # Actualisation de la session
        super().update()

        # Vérification que la partie soit en cours
        if self.current is None:
            return

        # Vérification de la connexion
        self._connected = pm.network.is_connected
        if not self._connected:
            pm.network.update()
            return

        # Actualisation côté hôte
        if self._is_host:
            data = pm.network.receive()
            if data: self.current.from_dict(data, ennemy=True)
            pm.network.send(self.current.to_dict())

        # Actualisation côté client
        else:
            data = pm.network.receive()
            if data: self.current.from_dict(data, ball=True, ennemy=True, game=True)
            pm.network.send(self.current.to_dict())

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()
        if pm.network.is_host or pm.network.is_connected:
            pm.network.disconnect()
        print("[Online] Session ended")