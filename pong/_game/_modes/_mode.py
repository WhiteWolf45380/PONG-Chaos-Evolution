# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from .._objects import Ball, Paddle
import time

# ======================================== MODE DE JEU ========================================
class Mode(pm.states.State):
    """Mode de jeu"""
    def __init__(self, name: str, max_players: int = 2):
        """
        Args:
            name (str): nom du mode de jeu
            max_players (int, optional): nombre de joueurs maximum
        """

        # Initialisation de l'état
        self.name: str = name
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
        self.max_players: int = max_players

        # Paramètres dynamiques
        self.frozen: bool = False       # jeu en gêle
        self.paused: bool = False       # jeu en pause
        self.ended: bool = False        # menu de fin de partie
        self.end_done: bool = False     # Fin déjà traitée
        self.next_round: bool = False   # en attente du prochain round

        self.score_limit: int = 3
        self.score_0: int = 0
        self.score_1: int = 0
        self.winner: int = None
    
    def __str__(self) -> str:
        """Renvoie le nom du mode"""
        return self.name
    
    # ======================================== LANCEMENT ========================================
    def on_enter(self):
        """Lancement d'une partie"""
        # Paramètres
        self.frozen: bool = False
        self.paused: bool = False
        self.ended: bool = False
        self.end_done: bool = False
        self.next_round: bool = False

        self.score_limit: int = ctx.modifiers["score_limit"]
        self.score_0: int = 0
        self.score_1: int = 0
        self.winner: int = None

        # Balle
        if self.ball is not None: self.ball.kill()
        self.ball = Ball(self.is_end)

        # Raquettes
        if self.paddle_0 is not None: self.paddle_0.kill()
        self.paddle_0 = Paddle(side=0)
        if self.paddle_1 is not None: self.paddle_1.kill()
        self.paddle_1 = Paddle(side=1)

        # Association
        self.player_1 = getattr(self, f'paddle_{ctx.modifiers["p1_side"]}')
        self.player_1.set_player(1)
    
        self.player_2 = getattr(self, f'paddle_{1 - ctx.modifiers["p1_side"]}')
        self.player_2.set_player(2)

        # Limitation
        if self.max_players == 1:
            self.player_2.freeze()
            self.player_2.hide()
        
        # Lancement
        self.start()
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def reset(self):
        """Prépartion des positions"""
        self.ball.reset()
        self.paddle_0.reset()
        self.paddle_1.reset()
    
    def kill_all(self):
        """Elimine tous les objets"""
        self.ball.kill()
        self.paddle_0.kill()
        self.paddle_1.kill()

    def start(self):
        """Lance la partie"""
        self.freeze()
        self.next_round = False
        pm.panels["game_count"].set_count([3, 2, 1, "Go!"])
        pm.panels["game_count"].activate()
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        if self.paused:
            pass
        elif self.frozen:
            pass
        elif self.ended:
            self.end()
        elif self.next_round:
            self.reset()
            self.start()
        
    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie après la collision d'un mur vertical"""
        return False

    def end(self, text: str = None):
        """Fin de partie"""
        if self.end_done:
            return False
        self.end_done = True
        ctx.results.load(text)
        pm.states.activate("results_animation")
        return True
    
    def on_exit(self):
        self.kill_all()
        return super().on_exit()

    # ======================================== METHODES PUBLIQUES ========================================
    @property
    def playing(self):
        """Vérifie que la partie soit en cours"""
        return not (self.frozen or self.paused or self.ended)

    def p1_move_up(self):
        """Déplacement vers le haut du joueur 1"""
        if not self.paused: self.player_1.move_up()

    def p1_move_down(self):
        """Déplacement vers le bas du joueur 1"""
        if not self.paused: self.player_1.move_down()
    
    def p2_move_up(self):
        """Déplacement vers le haut du joueur 2"""
        if not self.paused: self.player_2.move_up()

    def p2_move_down(self):
        """Déplacement vers le bas du joueur 2"""
        if not self.paused: self.player_2.move_down()
    
    def to_dict(self, *filters) -> dict:
        """Sérialise l'état de la partie"""
        game_dict =  {
            "ball_x": self.ball.x,
            "ball_y": self.ball.y,
            "ball_celerity": self.ball.celerity,
            "ball_angle": self.ball.angle,
            "ball_trail": self.ball.trail,
            "paddle_0_x": self.paddle_0.x if self.paddle_0 else None,
            "paddle_0_y": self.paddle_0.y if self.paddle_0 else None,
            "paddle_1_x": self.paddle_1.x if self.paddle_1 else None,
            "paddle_1_y": self.paddle_1.y if self.paddle_1 else None,
            "player_1_x": self.player_1.x if self.player_1 else None,
            "player_1_y": self.player_1.y if self.player_1 else None,
            "player_2_x": self.player_2.x if self.player_2 else None,
            "player_2_y": self.player_2.y if self.player_2 else None,
            "game_score_0": self.score_0,
            "game_score_1": self.score_1,
            "game_winner": self.winner,
            "game_frozen": self.frozen,
            "game_paused": self.paused,
            "game_ended": self.ended,
            "game_end_done": self.end_done,
            "game_next_round": self.next_round,
        }
        if not filters:
            return game_dict
        return {k: v for k, v in game_dict.items() if any(k.startswith(p) for p in filters)}

    def from_dict(self, data: dict, ball: bool = False, paddle_0: bool = False, paddle_1: bool = False, ennemy: bool = False, game: bool = False):
        """Applique l'état reçu"""
        if not data:
            return

        # Balle
        if self.ball and ball:
            self.ball.x = data.get("ball_x", self.ball.x)
            self.ball.y = data.get("ball_y", self.ball.y)
            self.ball.celerity = data.get("ball_celerity", self.ball.celerity)
            self.ball.angle = data.get("ball_angle", self.ball.angle)
            self.ball.trail = data.get("ball_trail", self.ball.trail)

        # Paddle 0
        if self.paddle_0 and paddle_0:
            self.paddle_0.x = data.get("paddle_0_x", self.paddle_0.x)
            self.paddle_0.y = data.get("paddle_0_y", self.paddle_0.y)

        # Paddle 1
        if self.paddle_1 and paddle_1:
            self.paddle_1.x = data.get("paddle_1_x", self.paddle_1.x)
            self.paddle_1.y = data.get("paddle_1_y", self.paddle_1.y)
        
        # Ennemy
        if self.player_2 and ennemy:
            self.player_2.x = data.get("player_1_x", self.player_2.x)
            self.player_2.y = data.get("player_1_y", self.player_2.y)

        # Partie
        if game:
            self.score_0 = data.get("game_score_0", self.score_0)
            self.score_1 = data.get("game_score_1", self.score_1)
            self.winner = data.get("game_winner", self.winner)
            self.frozen = data.get("game_frozen", self.frozen)
            self.paused = data.get("game_paused", self.paused)
            self.ended = data.get("game_ended", self.ended)
            self.end_done = data.get("game_end_done", self.end_done)
            self.next_round = data.get("game_next_round", self.next_round)
    
    def freeze(self):
        """Met le jeu en gêle"""
        self.frozen = True
    
    def unfreeze(self):
        """Enlève le gêle"""
        self.frozen = False

    def pause(self):
        """Met le jeu en pause"""
        self.paused = True
    
    def unpause(self):
        """Enlève la puse"""
        self.paused = False