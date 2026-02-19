# ======================================== IMPORTS ========================================
from ._session import Session
from    ..._core import pm, ctx

# ======================================== MODE DE JEU ========================================
class Online(Session):
    """Type de session : En ligne"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("online")

        # Statut de la connexion
        self._is_host = pm.network.is_hosting()
        self._connected = pm.network.is_connected()

        # Données de secours
        self._last_data = {}
        self.end_done = False

        # Initialisation
        self._pseud_sync = False

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()

        ctx.modifiers.set("p1_pseudo", ctx.modifiers.get("online_pseudo"))
        self.current.player_2.set_status("ennemy")

        self._is_host = pm.network.is_hosting()
        self._connected = pm.network.is_connected()

        self._last_data = {}
        self.end_done = False

        self._pseudo_sync = False

        if self._is_host:
            self.allow_freeze = True
        else:
            self.allow_freeze = False
    
        print(f"[Online] Start session | Host: {self._is_host}, Connected: {self._connected}")
    
    def on_enter(self):
        """Activation de l'état"""
        ctx.modes.selected = "classic"
        return super().on_enter()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        # Actualisation de la session
        super().update()

        # Vérification qu'une partie soit en cours
        if self.current is None:
            return

        # Vérification de la fin de partie côté client
        if not self._connected:
            if not self.end_done:
                try:
                    self._update_client()
                except Exception:
                    pass
                self.end_done = True
            return

        # Vérification de la connexion
        if pm.network.is_connection_lost():
            try:
                data = pm.network.receive()
                if data and "game_ended" in data:
                    self.current.ended = data["game_ended"]
            except Exception as _:
                pass
    
            if not self.current.ended:
                return self.end()
    
            error = pm.network.get_last_error()
            self._connected = False
            if self._is_host:
                print(f"Client perdu: {error}")
                ctx.engine.sys_message(pm.languages("error_host"), sender="Network", type="error") 
            else:
                print(f"Connexion perdue: {error}")
                ctx.engine.sys_message(pm.languages("error_client"), sender="Network", type="error") 
            return

        # Synchronisation
        if self._is_host: self._update_host()
        else: self._update_client()
    
    def _update_host(self):
        """Synchronisation côté hôte"""
        data = pm.network.receive()
        if data:
            self._last_data = data
            if not self._pseudo_sync and 'pseudo' in data:
                ctx.modifiers.set("p2_pseudo", data['pseudo'])
                self._pseudo_sync = True
            self.current.from_dict(self._last_data, ennemy=True)
        send_data = self.current.to_dict('ball', 'player_1', 'game')
        send_data['pseudo'] = ctx.modifiers.get("online_pseudo")
        pm.network.send(send_data)
        
    def _update_client(self):
        """Synchronisation côté client"""
        data = pm.network.receive()
        if data:
            self._last_data = data
            if not self._pseudo_sync and 'pseudo' in data:
                ctx.modifiers.set("p2_pseudo", data['pseudo'])
                self._pseudo_received = True
            self.current.from_dict(self._last_data, ball=True, ennemy=True, game=True)
        send_data = self.current.to_dict('player_1')
        send_data['pseudo'] = ctx.modifiers.get("online_pseudo")
        pm.network.send(send_data)

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        pm.network.send(self.current.to_dict('game'))
        pm.network.disconnect()
        print("[Online] Session ended") 
        super().end()