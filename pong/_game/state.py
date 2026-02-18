# ======================================== IMPORTS ========================================
from .._core import ctx, pm, pygame
from ._panels import GameView, GameCount, GamePause
from ._sessions import Session, Solo, Local, Online
from ._modes import Mode, Wall, Classic

# ======================================== ETAT ========================================
class Game(pm.states.State):
    """
    Une partie de jeu
    """
    def __init__(self):
        super().__init__('game')

        # Panels
        self.view: pm.types.Panel = GameView()
        self.bind_panel(self.view)
        self.count: pm.types.Panel = GameCount()
        self.pause: pm.types.Panel = GamePause()

        # Modes de jeu
        self.modes: dict = {}
        self.modes["wall"] = Wall()
        self.modes["classic"] = Classic()

        # Types de session
        self.sessions: dict = {}
        self.sessions["solo"] = Solo()
        self.sessions["local"] = Local()
        self.sessions["online"] = Online()

        # Partie en cours
        self.current_mode: Mode = None
        self.current_session: Session = None

        # pause
        pm.inputs.add_listener(pygame.K_ESCAPE, self.toggle_pause, condition=self.is_active)

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Initialisation d'une partie"""
        # Activation des panels
        super().on_enter()
        ctx.engine.background.visible = True

        # Actualisation des pseudos
        online_psd = ctx.modifiers["online_pseudo"]
        if online_psd is not None:
            ctx.modifiers.set("p1_pseudo", online_psd)
        else:
            ctx.modifiers.set("p1_pseudo", "P1")

        # Activation de la session
        if self.current_session is None: self.current_session = self.sessions["solo"]
        self.current_session.activate()

        # Activation du mode de jeu
        if self.current_mode is None: self.current_mode = self.modes["classic"]
        self.current_mode.activate()

    def on_exit(self):
        ctx.engine.background.visible = False
        return super().on_exit()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""

    # ======================================== GETTERS ========================================
    def get_session(self) -> Session:
        """Renvoie la session en cours"""
        return self.current_session

    def get_mode(self) -> Mode:
        """Renvoie le mode de jeu en cours"""
        return self.current_mode

    # ======================================== SETTERS ========================================
    def set_session(self, session: str):
        """Fixe la session"""
        self.current_session = self.sessions.get(session)
    
    def set_mode(self, mode: str):
        """Fixe le mode de jeu"""
        self.current_mode = self.modes.get(mode) 

    # ======================================== METHODES PUBLIQUES ========================================
    def toggle_pause(self):
        """Active/Désactive la pause de la partie"""
        if self.current_mode is None: return
        allows_freeze = getattr(self.current_session, 'allow_freeze', True)
        if not self.pause.is_active():
            if allows_freeze: self.current_mode.pause()
            self.pause.text.visible = allows_freeze
            self.pause.activate()
        else:
            if allows_freeze: self.current_mode.unpause()
            self.pause.deactivate()
    
    def pause(self):
        """Active la pause de la partie"""
        if self.current_mode is None: return
        allows_freeze = getattr(self.current_session, 'allow_freeze', True)
        if not self.pause.is_active():
            if allows_freeze: self.current_mode.pause()
            self.pause.text.visible = allows_freeze
            self.pause.activate()
        
    def unpause(self):
        """Désactive la pause de la partie"""
        if self.current_mode is None: return
        allows_freeze = getattr(self.current_session, 'allow_freeze', True)
        if self.pause.is_active():
            if allows_freeze: self.current_mode.unpause()
            self.pause.deactivate()

    def end_session(self):
        """Met fin à la session"""
        if self.current_session is not None:
            self.current_session.deactivate()
    
    def end_mode(self):
        """Met fin à la partie"""
        if self.current_mode is not None:
            self.current_mode.deactivate()