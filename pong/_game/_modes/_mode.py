# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from .._objects import Ball, Paddle

# ======================================== MODE DE JEU ========================================
class Mode(pm.states.State):
    """Mode de jeu"""
    def __init__(self, name: str, paddles: int = 2):
        """
        Args:
            name (str): nom du mode de jeu
            paddles (int, optional): nombre de raquettes
        """

        # Initialisation de l'état
        self.name = name
        super().__init__(f"{self.name}_mode", layer=2)
    
        # Pannel de vue
        self.view: pm.types.Panel = pm.panels["game_view"]

        # Balle
        self.ball: Ball = None

        # Raquettes
        self.paddle_0: Paddle = None    # gauche
        self.paddle_1: Paddle = None    # droite

        # Joueurs
        self.player_1: Paddle | None = None
        self.player_2 : Paddle | None = None

        # Paramètres fixes
        self.paddles = paddles

        # Paramètres dynamiques
        self.running = False
        self.ended = False
        self.winner: int = None
        self.score: int = 0
    
    def __str__(self) -> str:
        """Renvoie le nom du mode"""
        return self.name
    
    # ======================================== LANCEMENT ========================================
    def on_enter(self):
        """Lancement d'une partie"""
        # Balle
        self.ball = Ball(self.is_end)

        # Raquettes
        self.paddle_0 = Paddle(Paddle.OFFSET, self.view.centery)
        self.paddle_1 = Paddle(self.view.width - Paddle.OFFSET, self.view.centery)

        # Association
        self.player_1 = getattr(self, f'paddle_{ctx.modifiers["paddle_side"]}')
        self.player_2 = getattr(self, f'paddle_{1 - ctx.modifiers["paddle_side"]}')

        # Limitation
        if self.paddles == 1:
            self.player_2.freeze()
            self.player_2.hide()
            setattr(self, f'paddle_{1 - ctx.modifiers["paddle_side"]}', None)
        
        # Paramètres
        self.running = True # Jeu en cours
        self.frozen = False # Jeu en gêle
        self.ended = False  # Fin de partie
        self.winner = None
        self.score = 0
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        if not pm.states.is_active("game"):
            if self.running:
                self.running = False
                self.freeze()
        elif not self.running:
            self.running = True
            self.unfreeze()

        if self.ended:
            self.end()
    
    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie après la collision d'un mur vertical"""
        return False

    def end(self):
        """Fin de partie"""
        pm.stop()

    # ======================================== METHODES PUBLIQUES ========================================
    def p1_move_up(self):
        """Déplacement vers le haut du joueur 1"""
        if self.running: self.player_1.move_up()

    def p1_move_down(self):
        """Déplacement vers le bas du joueur 1"""
        if self.running: self.player_1.move_down()
    
    def p2_move_up(self):
        """Déplacement vers le haut du joueur 2"""
        if self.running: self.player_2.move_up()

    def p2_move_down(self):
        """Déplacement vers le bas du joueur 2"""
        if self.running: self.player_2.move_down()
    
    @property
    def playing(self):
        """Vérifie que la partie soit en cours"""
        return (self.running and not self.ended and not self.frozen)
    
    def get_infos(self):
        """Renvoie les informations relatives à la partie"""
        if self.ended: return None
        return {
            "ball_x": self.ball.x,
            "ball_y": self.ball.y,
            "ball_dx": self.ball.dx,
            "ball_dy": self.ball.dy,
            "player_1": self.player_1.is_active(),
            "p1_x": self.player_1.x,
            "p1_y": self.player_2.y,
            "player_2": self.player_2.is_active(),
            "p2_x": self.player_2.x,
            "p2_y": self.player_2.y
        }
    
    def freeze(self):
        """Met le jeu en gêle"""
        self.ball.freeze()
        self.player_1.freeze()
        self.player_2.freeze()
        self.frozen = True
    
    def unfreeze(self):
        """Enlêve le gêle"""
        if not self.running: return
        self.ball.unfreeze()
        self.player_1.unfreeze()
        if self.paddles > 1:
            self.player_2.unfreeze()
        self.frozen = False