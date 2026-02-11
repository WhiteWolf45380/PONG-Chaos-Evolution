# ======================================== IMPORTS ========================================
from ..._core import ctx
from ._mode import Mode

# ======================================== MODE DE JEU ========================================
class Wall(Mode):
    """
    Mode de jeu : Mur

    Jeu seul contre un mur.
    Le score augment à chaque rebond contre le mur.
    La partie se termine lorsque la balle touche le mur côté raquette.
    Le but est d'effectuer le plus grand score.
    """
    def __init__(self):
        # Initialisation du mode
        super().__init__("wall", paddles=1)

    # ======================================== LANCEMENT ========================================
    def on_enter(self):
        """Activation de l'état"""
        super().on_enter()
        setattr(self, f"score_{1 - ctx.modifiers.get('paddle_side')}", None)

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        super().update()

    # ======================================== FIN ========================================
    def is_end(self, side: int):
        """Vérifie la fin de partie"""
        player_side = ctx.modifiers['paddle_side']
        if side == player_side:
            self.ended = True
            return True
        if player_side == 0: self.score_0 += 1
        else: self.score_1 += 1
        return False

    def end(self):
        """Fin de partie"""
        if not super().end():
            return
        print(f"La partie est terminée !\nScore: {getattr(self, f'score_{ctx}', 0)}")