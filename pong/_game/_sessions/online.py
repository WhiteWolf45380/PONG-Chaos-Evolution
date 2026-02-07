# ======================================== IMPORTS ========================================
from ._session import Session
from    ..._core import pm

# ======================================== MODE DE JEU ========================================
class Online(Session):
    """Type de session : En ligne"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("online")
        self._is_host = pm.network.is_host
        self._connected = pm.network.is_connected

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
        super().update()
        pm.network.update()
        self._connected = pm.network.is_connected

        if not self._connected:
            return

        if self._is_host:
            pm.network.send(self.current.to_dict())
        else:
            data = pm.network.receive()
            print(data)
            if data:
                self.current.from_dict(data)

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()
        if pm.network.is_host or pm.network.is_connected:
            pm.network.disconnect()
        print("[Online] Session ended")