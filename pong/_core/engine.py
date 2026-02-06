# ======================================== IMPORTS ========================================
from . import ctx, pm

# ======================================== CLASSE PRINCIPALE ========================================
class Engine:
    """
    Moteur d'éxécution
    """
    def __init__(self):
        # Initialisation du framework modulable
        pm.init()
        pm.time.set_fps_limit(60)
        pm.screen.set_vsync(True)

        # Imports
        from .._menus import Main, Modes, Modifiers
        from .._game import Game

        # Instanciation du jeu
        self.game = Game()
        ctx.game = self.game

        # Instanciation des menus
        self.main = Main()
        ctx.main = self.main

        self.modes = Modes()
        ctx.modes = self.modes

        self.modifiers = Modifiers()
        ctx.modifiers = self.modifiers
        
        # Lancement d'une partie
        pm.states.activate("game")

    def update(self):
        """Actualisation de la frame"""
        pm.screen.fill((80, 80, 90))

    def run(self):
        """Lance l'éxécution"""
        pm.run(self.update)

# ======================================== EXPORTS ========================================
__all__ = ["Engine"]