# ======================================== IMPORTS ========================================
from .._core import ctx, pm, pygame
from ._panels import GameView
from ._sessions import Solo, Local, Online
from ._modes import WallGame, Classic

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
        self.modes["wall_game"] = WallGame()
        self.modes["classic"] = Classic()

        # Types de session
        self.sessions = {}
        self.sessions["solo"] = Solo()
        self.session["local"] = Local()
        self.session["online"] = Online()

        # Partie en cours
        self.current_mode = None
        self.current_session = None

        # pause
        self.game_frozen = True
        pm.inputs.add_listener(pygame.K_SPACE, self.toggle_freeze)

    # ======================================== Initialisation ========================================
    def on_enter(self):
        """Initialisation d'une partie"""
        # Activation des panels
        super().on_enter()

        # Activation de la session
        self.current_session = self.sessions[ctx.main.session_type]
        self.current_session.activate()

        # Activation du mode de jeu
        self.current_mode = self.modes[ctx.modes.selected]
        self.current_mode.activate()

        # Gêle avant partie
        self.toggle_freeze()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""
        # Jeu en pause
        if self.game_frozen:
            return
        
        # Jeu en cours
        if self.current is not None:
            self.current.update()
        
    # ======================================== GETTERS ========================================

    # ======================================== SETTERS ========================================

    # ======================================== METHODES DYNAMIQUES ========================================
    def toggle_freeze(self):
        """Active/Désactive le gêle de la partie"""
        if self.current_mode is None: return
        self.game_frozen = not self.game_frozen
        for name in ("ball", "paddle_0", "paddle_1"):
            obj: pm.types.Entity = getattr(self.current, name, None)
            if obj is not None: obj.freeze() if not self.game_frozen else obj.unfreeze()