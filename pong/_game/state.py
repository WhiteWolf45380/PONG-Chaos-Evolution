# ======================================== IMPORTS ========================================
from .._core import ctx, pm, pygame
from ._panels import GameView
from ._modes import WallGame, Solo, Local

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
        self.modes["solo"] = Solo()
        self.modes["local"] = Local()

        # Partie en cours
        self.current = None

        # pause
        self.game_frozen = True
        def toggle_freeze(self):
            if self.current is None: return
            self.game_frozen = not self.game_frozen
            for name in ("ball", "paddle_0", "paddle_1"):
                obj: pm.types.Entity = getattr(self.current, name)
                if obj is not None: obj.freeze() if not self.game_frozen else obj.unfreeze()
        pm.inputs.add_listener(pygame.K_SPACE, toggle_freeze, args=[self])

    # ======================================== CHARGEMENT ========================================
    def on_enter(self):
        """Initialisation d'une partie"""
        super().on_enter()
        self.current = self.modes[ctx.modes.selected]
        pm.states.activate(ctx.modes.selected)
        return self

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
    @property
    def current_mode(self):
        """Renvoie le mode de jeu actuel"""
        return ctx.modes.selected