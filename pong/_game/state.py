# ======================================== IMPORTS ========================================
from .._core import ctx, pm, pygame
from ._panels import GameView
from ._modes import WallGame, Solo, Local
from ._objects import Ball, Paddle

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

        # temporaire
        self.game_mode = 2

        # lancement de la partie
        self.game_frozen = True
        def toggle_freeze(self):
            self.game_frozen = not self.game_frozen
        pm.inputs.add_listener(pygame.K_SPACE, toggle_freeze, args=[self])

        # objets
        self.ball = None    # balle
        self.paddles = []   # raquettes

        # wall game
        self.score = 0

    # ======================================== CHARGEMENT ========================================
    def init(self):
        """Initialisation d'une partie"""
        # balle
        self.ball = Ball()

        # raquettes
        offset = 50
        self.paddles.append(Paddle(offset, self.surface_rect.height / 2, up=pygame.K_z, down=pygame.K_s))
        if self.game_mode == 2:
            self.paddles.append(Paddle(self.surface_rect.width - offset, self.surface_rect.height / 2, up=pygame.K_UP, down=pygame.K_DOWN))
        
        pm.states.activate("game") 
        return self

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""
        # jeu en pause
        if self.game_frozen:
            return
        
    # ======================================== GETTERS ========================================
    @property
    def current_mode(self):
        """Renvoie le mode de jeu actuel"""
        return ctx.modes.selected