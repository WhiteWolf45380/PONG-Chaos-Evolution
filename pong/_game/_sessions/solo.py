# ======================================== IMPORTS ========================================
from ..._core import ctx
from ._session import Session
from ._bot import Bot

# ======================================== MODE DE JEU ========================================
class Solo(Session):
    """Type de session : Seul"""
    def __init__(self):
        # Initialisation de l'état
        super().__init__("solo")

        # Agent
        self.bot = Bot()

    # ======================================== LANCEMENT ========================================
    def start(self):
        """Initialisation d'une session"""
        super().start()
        self.current.player_2.set_status("ennemy")

    def on_enter(self):
        """Activation de l'état"""
        ctx.modifiers.set("p2_pseudo", "Bot")
        return super().on_enter()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la session"""
        if not super().update():
            return
        p2_y = self.current.player_2.centery
        ball_x, ball_y = self.current.ball.center
        ball_dx, ball_dy = self.current.ball.dx, self.current.ball.dy
        move = self.bot.get_move(p2_y, ball_x, ball_y, ball_dx, ball_dy)
        if move == -1:
            self.p2_move_up()
        elif move == 1:
            self.p2_move_down()

    # ======================================== FIN ========================================
    def end(self):
        """Fin de la session"""
        super().end()