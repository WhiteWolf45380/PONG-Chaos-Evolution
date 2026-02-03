# ======================================== IMPORTS ========================================
from . import ctx, pm
from .._menus import Main, Modes, Modifiers
from .._game import Game

# ======================================== CLASSE PRINCIPALE ========================================
class Engine:
    """
    Moteur d'éxécution
    """
    def __init__(self):
        # Initialisation du framework modulable
        pm.init()

        # Instanciation du jeu
        self.game = Game().init()
        ctx.game = self.game

        # Instanciation des menus
        self.modes = Modes.init()
        ctx.modes = self.modes

        self.modifiers = Modifiers().init()
        ctx.modifiers = self.modifiers

        self.main = Main.init()
        ctx.main = self.main
        

    def update(self):
        """Actualisation de la frame"""
        pm.screen.fill((80, 80, 90))

    def run(self):
        """Lance l'éxécution"""
        pm.run(self.update)

# ======================================== EXPORTS ========================================
__all__ = ["Engine"]