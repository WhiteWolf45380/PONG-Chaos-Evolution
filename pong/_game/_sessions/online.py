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

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self._is_host = pm.network.is_host
        self._connected = pm.network.is_connected
        while not pm.network.is_connected: pass
        if not self._is_host: ctx.modifiers.set("paddle_side", 1)
        print(f"[Online] Start session | Host: {self._is_host}, Connected: {self._connected}")

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        super().update()
        if self.current is None: return
        if not self._is_host and not self.current.frozen: self.current.freeze()

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