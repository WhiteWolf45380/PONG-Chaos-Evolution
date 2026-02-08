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
        self._start_pos = False

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self._is_host = pm.network.is_host
        self._connected = pm.network.is_connected
        if not self._is_host: ctx.modifiers.set("paddle_side", 1)
        print(f"[Online] Start session | Host: {self._is_host}, Connected: {self._connected}")

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        super().update()
        if self.current is None: return

        pm.network.update()
        self._connected = pm.network.is_connected

        if not self._connected:
            return

        if self._is_host:
            pm.network.send(self.current.to_dict())
        else:
            data = pm.network.receive()
            if data:
                if not self._start_pos:
                    self.current.from_dict(data, ball=True, player_1=True, player_2=True, game=True)
                    self._start_pos = True
                else:
                    self.current.from_dict(data, player_2=True, game=True)

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()
        if pm.network.is_host or pm.network.is_connected:
            pm.network.disconnect()
        print("[Online] Session ended")