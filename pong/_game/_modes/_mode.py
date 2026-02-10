# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from .._objects import Ball, Paddle
import time

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
        self.paddles: int = paddles

        # Paramètres dynamiques
        self.frozen: bool = False       # jeu en gêle
        self.paused: bool = False       # jeu en pause
        self.ended: bool = False        # menu de fin de partie
        self.next_round: bool = False   # en attente du prochain round

        self.score_limit: int = 3
        self.score_0: int = 0
        self.score_1: int = 0
        self.winner: int = None

        # Animation de lancement
        self.nums: list = []
        self.nums_index: int = 0
        self.nums_timer: float = 0.0
        for i in range(3, 0, -1):
            num: pm.types.TextObject = pm.ui.Text(
                x=self.view.centerx,
                y=self.view.centery,
                text=str(i),
                font_size=256,
                font_color=(255, 255, 255),
                shadow=True,
                shadow_offset=3,
                anchor="center",
                panel=str(self.view),
                zorder=2,
            )
            num.visible = False
            self.nums.append(num)

        self.curtain_alpha_max = 120
        self.curtain = pm.ui.Surface(
            x=0,
            y=0,
            width=self.view.width,
            height=self.view.height,
            color=(0, 0, 0, 255),
            zorder=1,
            panel=str(self.view),
        )
        self.curtain.visible = False
    
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
        self.paddle_0 = Paddle(Paddle.OFFSET, self.view.centery)
        if self.paddle_1 is not None: self.paddle_1.kill()
        self.paddle_1 = Paddle(self.view.width - Paddle.OFFSET, self.view.centery)

        # Association
        self.player_1 = getattr(self, f'paddle_{ctx.modifiers["paddle_side"]}')
        self.player_2 = getattr(self, f'paddle_{1 - ctx.modifiers["paddle_side"]}')

        # Limitation
        if self.paddles == 1:
            self.player_2.freeze()
            self.player_2.hide()
            setattr(self, f'paddle_{1 - ctx.modifiers["paddle_side"]}', None)
        
        # Lancement
        self.start()
    
    def reset(self):
        """Prépartion des positions"""
        self.ball.reset()
        self.paddle_0.reset()
        self.paddle_1.reset()
        self.next_round = False
        self.start()

    def start(self):
        """Lance la partie"""
        self.freeze()
        self.nums_index = 0
        self.nums_timer = 0.0
        self.nums[0].visible = True
        self.curtain.set_alpha(0)
        self.curtain.visible = True
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        if self.paused:
            pass
        elif self.frozen:
            self._update_count()
        elif self.ended:
            self.end()
        elif self.next_round:
            self.reset()

    def _update_count(self):
        """Actualise le décompte"""
        self.nums_timer += pm.time.dt
        t = min(self.nums_timer / 1.0, 1.0)

        factor = 1 - 4 * (t - 0.5) ** 3
        factor = max(0.1, min(1.0, factor))

        current: pm.types.TextObject = self.nums[self.nums_index]
        current.set_alpha(int(255 * factor))
        current.reset()
        current.scale(factor)

        if self.nums_index == 0:
            self.curtain.set_alpha(int(self.curtain_alpha_max * min(1, 2 * t)))
        elif self.nums_index == len(self.nums) - 1:
            self.curtain.set_alpha(int(self.curtain_alpha_max * max(0, 1 - 2 * t)))

        if t >= 1.0:
            current.visible = False
            current.reset()
            self.nums_index += 1
            if self.nums_index >= len(self.nums):
                self.curtain.visible = False
                self.nums_index = 0
                self.unfreeze()
                return

            self.nums[self.nums_index].visible = True
            self.nums_timer = 0.0
        
    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie après la collision d'un mur vertical"""
        return False

    def end(self):
        """Fin de partie"""
        time.sleep(2)
        pm.states.activate("main", transition=True, duration=3.0)

    # ======================================== METHODES PUBLIQUES ========================================
    @property
    def playing(self):
        """Vérifie que la partie soit en cours"""
        return not (self.frozen or self.paused or self.ended)

    def p1_move_up(self):
        """Déplacement vers le haut du joueur 1"""
        if self.playing: self.player_1.move_up()

    def p1_move_down(self):
        """Déplacement vers le bas du joueur 1"""
        if self.playing: self.player_1.move_down()
    
    def p2_move_up(self):
        """Déplacement vers le haut du joueur 2"""
        if self.playing: self.player_2.move_up()

    def p2_move_down(self):
        """Déplacement vers le bas du joueur 2"""
        if self.playing: self.player_2.move_down()
    
    def to_dict(self) -> dict:
        """Sérialise l'état de la partie"""
        return {
            "ball_x": self.ball.x,
            "ball_y": self.ball.y,
            "ball_angle": self.ball.angle,
            "paddle_0_x": self.paddle_0.x if self.paddle_0 else None,
            "paddle_0_y": self.paddle_0.y if self.paddle_0 else None,
            "paddle_1_x": self.paddle_1.x if self.paddle_1 else None,
            "paddle_1_y": self.paddle_1.y if self.paddle_1 else None,
            "player_1_x": self.player_1.x if self.player_1 else None,
            "player_1_y": self.player_1.y if self.player_1 else None,
            "player_2_x": self.player_2.x if self.player_2 else None,
            "player_2_y": self.player_2.y if self.player_2 else None,
            "score_0": self.score_0,
            "score_1": self.score_1,
            "winner": self.winner,
            "frozen": self.frozen,
            "paused": self.paused,
            "ended": self.ended,
        }

    def from_dict(self, data: dict, ball: bool = False, paddle_0: bool = False, paddle_1: bool = False, ennemy: bool = False, game: bool = False):
        """Applique l'état reçu"""
        if not data:
            return

        # Balle
        if self.ball and ball:
            self.ball.x = data.get("ball_x", self.ball.x)
            self.ball.y = data.get("ball_y", self.ball.y)
            self.ball.angle = data.get("ball_angle", self.ball.angle)

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
            self.score_0 = data.get("score_0", self.score_0)
            self.score_1 = data.get("score_1", self.score_1)
            self.winner = data.get("winner", self.winner)
            self.paused = data.get("paused", self.paused)
            self.ended = data.get("ended", self.ended)
    
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