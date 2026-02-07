# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from .._modes._mode import Mode

# ======================================== MODE DE JEU ========================================
class Session(pm.states.State):
    """Session"""
    def __init__(self, name: str):
        """
        Args:
            name (str): nom de la session
        """
        # Initialisation de l'état
        super().__init__(f"{name}_session", layer=1)

        # Partie en cours
        self.initialized: bool = False
        self.current: Mode = None

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        pm.inputs.add_listener(pm.settings["p1_up"], self.p1_move_up, repeat=True, condition=self.is_running)
        pm.inputs.add_listener(pm.settings["p1_down"], self.p1_move_down, repeat=True, condition=self.is_running)
        self.initialized = True

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        if not pm.states.is_active("game"):
            return

        current_str = pm.states.get_active_by_layer(2)
        if current_str is not None: self.current = pm.states[current_str]
        if isinstance(self.current, Mode):
            if not self.initialized: self.start()
        elif self.initialized:
            self.end()

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        pm.inputs.remove_listener(pm.settings["p1_up"], self.p1_move_up)
        pm.inputs.remove_listener(pm.settings["p1_down"], self.p1_move_up)
        self.initialized = False

    
    def on_exit(self):
        """Désactivation de l'état"""
        if self.initialized:
            self.end()
            
    # ======================================== METHODES PUBLIQUES ========================================
    def is_running(self):
        """Vérifie que la partie soit en cours"""
        return pm.states.is_active("game") and self.current.playing

    def p1_move_up(self):
        """Déplacement vers le haut du joueur 1"""
        self.current.p1_move_up()

    def p1_move_down(self):
        """Déplacement vers le bas du joueur 1"""
        self.current.p1_move_down()
    
    def p2_move_up(self):
        """Déplacement vers le haut du joueur 2"""
        self.current.p2_move_up()

    def p2_move_down(self):
        """Déplacement vers le bas du joueur 2"""
        self.current.p2_move_down()