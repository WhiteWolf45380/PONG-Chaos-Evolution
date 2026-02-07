# ======================================== IMPORTS ========================================
from . import ctx, pm, get_folder

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

        pm.languages.load_directory(get_folder("_languages"))
        pm.languages.set_language('en', fallback='fr')

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
        pm.states.activate("main_menu", ease_out=False, duration=1.5)

    def update(self):
        """Actualisation de la frame"""
        pm.screen.fill((80, 80, 90))

    def run(self):
        """Lance l'éxécution"""
        pm.run(self.update)

# ======================================== EXPORTS ========================================
__all__ = ["Engine"]