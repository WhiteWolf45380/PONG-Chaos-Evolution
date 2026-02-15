# ======================================== IMPORTS ========================================
from ._session import Session
from ..._core import pm, ctx
import time

# ======================================== MODE DE JEU ========================================
class Online(Session):
    """Type de session : En ligne"""
    INIT_TIMEOUT = 2.0
    def __init__(self):
        # Initialisation de l'état
        super().__init__("online")

        # Statut de la connexion
        self._is_host = pm.network.is_hosting()
        self._connected = pm.network.is_connected()

        # Données de secours
        self._last_data = {}

        # Initialisation
        self._is_initialized = False
        self._init_infos_list = ["pseudo", "ready"]
        self._init_infos = {k: {"received": False, "sent": False} for k in self._init_infos_list}

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()

        ctx.modifiers.set("p1_pseudo", ctx.modifiers.get("online_pseudo"))
        self.current.player_2.set_status("ennemy")

        self._is_host = pm.network.is_hosting()
        self._connected = pm.network.is_connected()

        self._is_initialized = False
        self._init_infos = {k: {"received": False, "sent": False} for k in self._init_infos_list}

        if self._is_host:
            self.allow_freeze = True
        else:
            self.allow_freeze = False
        
        self._init()
    
        print(f"[Online] Start session | Host: {self._is_host}, Connected: {self._connected}")
    
    def on_enter(self):
        """Activation de l'état"""
        ctx.modes.selected = "classic"
        return super().on_enter()
    
    def _init(self):
        """Initialisation"""
        t0 = time.time()
        while not self._is_initialized:
            if time.time() - t0 > self.INIT_TIMEOUT:
                break
            self._update_init()

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
        if self._is_host:
            self._update_host()
        else:
            self._update_client()
            
    
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
                ctx.modifiers._pseudo_sync("p2_pseudo", data['pseudo'])
                self._pseudo_received = True
            self.current.from_dict(self._last_data, ball=True, ennemy=True, game=True)
        send_data = self.current.to_dict('player_1')
        send_data['pseudo'] = ctx.modifiers.get("online_pseudo")
        pm.network.send(send_data)
    
    def _update_init(self):
        """Initialisation avec échange séquentiel des infos"""
        for info_key in self._init_infos_list:
            info = self._init_infos[info_key]
            
            if not info["received"]:
                self._send_init_info(info_key)
                if not info["sent"]:
                    info["sent"] = True
                    print(f"[Online] Sending {info_key}...")
                
                data = pm.network.receive()
                if data and data.get("type") == info_key:
                    self._process_init_info(info_key, data)
                    info["received"] = True
                    print(f"[Online] {info_key.capitalize()} received!")
                
                return
        
        if all(info["received"] for info in self._init_infos.values()):
            if self._is_host:
                pm.network.send({"type": "start"})
                self._is_initialized = True
                print("[Online] Host: Initialization complete - Starting game")
            else:
                data = pm.network.receive()
                if data and data.get("type") == "start":
                    self._is_initialized = True
                    print("[Online] Client: Initialization complete - Starting game")
    
    def _send_init_info(self, info_key: str):
        """Envoie une info d'initialisation selon son type"""
        if info_key == "pseudo":
            pm.network.send({
                "type": "pseudo",
                "pseudo": ctx.modifiers.get("online_pseudo")
            })
        elif info_key == "ready":
            pm.network.send({
                "type": "init_ready"
            })
    
    def _process_init_info(self, info_key: str, data: dict):
        """Traite une info d'initialisation reçue selon son type"""
        if info_key == "pseudo":
            ctx.modifiers.set("p2_pseudo", data.get("pseudo", "Player 2"))
        elif info_key == "ready":
            pass

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        if pm.network.is_connected():
            self.update()
            pm.network.disconnect()
        print("[Online] Session ended") 
        super().end()