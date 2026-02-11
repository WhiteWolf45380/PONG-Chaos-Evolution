# ======================================== IMPORTS ========================================
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
        super().__init__("classic", paddles=2)

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
            self.winner = 1 - side
            self.ended = True
        self.next_round = True
        return True

    def end(self):
        """Fin de partie"""
        if not super().end():
            return
        print(f"La partie est terminée !\nLe gagnant est le joueur {self.winner}")