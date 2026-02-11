# ======================================== IMPORTS ========================================
from .._core import ctx, pm, pygame
from ._panels import GameView
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
        self.view = GameView()
        self.bind_panel(self.view)

        # Modes de jeu
        self.modes = {}
        self.modes["wall"] = Wall()
        self.modes["classic"] = Classic()

        # Types de session
        self.sessions = {}
        self.sessions["solo"] = Solo()
        self.sessions["local"] = Local()
        self.sessions["online"] = Online()

        # Partie en cours
        self.current_mode: Mode = None
        self.current_session: Session = None

        # pause
        pm.inputs.add_listener(pygame.K_ESCAPE, self.toggle_pause)

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Initialisation d'une partie"""
        # Activation des panels
        super().on_enter()
        ctx.engine.background.visible = True

        # Activation de la session
        self.current_session = self.sessions[ctx.main.session_type]
        self.current_session.activate()

        # Activation du mode de jeu
        self.current_mode = self.modes[ctx.modes.selected]
        self.current_mode.activate()

    def on_exit(self):
        ctx.engine.background.visible = False
        return super().on_exit()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""

    # ======================================== METHODES DYNAMIQUES ========================================
    def toggle_pause(self):
        """Active/Désactive le gêle de la partie"""
        if self.current_mode is None or not getattr(self.current_session, 'allow_freeze', True): return
        if not self.current_mode.paused: self.current_mode.pause()
        else: self.current_mode.unpause()

    def end_session(self):
        """Met fin à la session"""
        if self.current_session is not None:
            self.current_session.deactivate()
    
    def end_mode(self):
        """Met fin à la partie"""
        if self.current_mode is not None:
            self.current_mode.deactivate()