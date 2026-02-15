# ======================================== IMPORTS ========================================
from ..._core import ctx, pm
from ._mode import Mode

# ======================================== MODE DE JEU ========================================
class Classic(Mode):
    """
    Mode de jeu : Classique

    Jeu de PONG basique.
    Une raquette de chaque côté.
    La partie se termine lorsque la balle touche l'un des murs verticaux.
    Le but est d'envoyer la balle toucher le mur adverse.
    """
    def __init__(self):
        # Initialisation du mode
        super().__init__("classic", max_players=2)

        # Sessions conformes
        self.allowed_sessions = ["solo", "local", "online"]

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        super().update()

    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie"""
        if side == 0: self.score_1 += 1
        else: self.score_0 += 1
        if self.score_0 >= self.score_limit or self.score_1 >= self.score_limit:
            self.winner = getattr(self, f'paddle_{1 - side}', self.paddle_0).get_player()
            self.ended = True
        self.next_round = True
        return True

    def end(self):
        """Fin de partie"""
        text = pm.languages("game_results_winner", winner=ctx.modifiers.get(f"p{self.winner}_pseudo", fallback=f"P{self.winner}"))
        color = getattr(self, f'player_{self.winner}', self.player_1).color
        if not super().end(text, color=color):
            return