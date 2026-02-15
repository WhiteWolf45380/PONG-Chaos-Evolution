# ======================================== IMPORTS ========================================
from ._session import Session
from    ..._core import pm, ctx

# ======================================== MODE DE JEU ========================================
class Online(Session):
    """Type de session : En ligne"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("online")
        self._is_host = pm.network.is_hosting()
        self._connected = pm.network.is_connected()
        self._last_data = {}
        self._pseudo_received = False
        self._pseudo_sent = False

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self.current.player_2.set_status("ennemy")
        self._is_host = pm.network.is_hosting()
        self._connected = pm.network.is_connected()
        ctx.modifiers.set("p1_pseudo", ctx.modifiers.get("online_pseudo") + f"({'host' if self._is_host else 'client'})")
        self._pseudo_received = False
        self._pseudo_sent = False
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

        # Vérification que la partie soit en cours
        if self.current is None or not self._connected:
            return

        # Vérification de la connexion
        if pm.network.is_connection_lost():
            error = pm.network.get_last_error()
            self._connected = False
            if self._is_host:
                print(f"Client perdu: {error}")
                ctx.engine.sys_message(pm.languages("error_host"), sender="Network", type="error") 
            else:
                print(f"Connexion perdue: {error}")
                ctx.engine.sys_message(pm.languages("error_client"), sender="Network", type="error") 
                pm.states.activate("main_menu")
            return

        # Synchronisation
        if self._is_host: self._update_host()
        else: self._update_client()
    
    def _update_host(self):
        """Synchronisation côté hôte"""
        data = pm.network.receive()
        if data:
            self._last_data = data
            if not self._pseudo_received and 'pseudo' in data:
                ctx.modifiers.set("p2_pseudo", data['pseudo'] + " (client)")
                self._pseudo_received = True
            self.current.from_dict(self._last_data, ennemy=True)
        send_data = self.current.to_dict('ball', 'player_1', 'game')
        if not self._pseudo_sent:
            send_data['pseudo'] = ctx.modifiers.get("online_pseudo")
            self._pseudo_sent = True
        pm.network.send(send_data)
        
    def _update_client(self):
        """Synchronisation côté client"""
        data = pm.network.receive()
        if data:
            self._last_data = data
            if not self._pseudo_received and 'pseudo' in data:
                ctx.modifiers.set("p2_pseudo", data['pseudo'] + " (host)")
                self._pseudo_received = True
            self.current.from_dict(self._last_data, ball=True, ennemy=True, game=True)
        send_data = self.current.to_dict('player_1')
        if not self._pseudo_sent:
            send_data['pseudo'] = ctx.modifiers.get("online_pseudo")
            self._pseudo_sent = True
        pm.network.send(send_data)

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        if pm.network.is_connected():
            self.update()
            pm.network.disconnect()
        print("[Online] Session ended") 
        super().end()