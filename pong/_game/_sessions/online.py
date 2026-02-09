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
        if self._is_host:
            self.allow_freeze = True
        else:
            self.allow_freeze = False
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
            pm.network.update() # en attente
            return

        # Synchronisation
        if self._is_host: self._update_host()
        else: self._update_client()
    
    def _update_host(self):
        """Synchronisation côté hôte"""
        data = pm.network.receive()
        if data:
            self.current.from_dict(data, ennemy=True)
        pm.network.send(self.current.to_dict())
        
    def _update_client(self):
        """Synchronisation côté client"""
        data = pm.network.receive()
        if data:
            if data.get("ended", False): self.end()
            self.current.from_dict(data, ball=True, ennemy=True, game=True)
        pm.network.send(self.current.to_dict())

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()
        if pm.network.is_host or pm.network.is_connected:
            pm.network.disconnect()
            pm.network
        print("[Online] Session ended")