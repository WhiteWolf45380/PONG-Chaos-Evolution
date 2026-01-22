import pygame
import pygame_manager as pm # package personnel pour pygame
from _game import Game

class Main:
    """
    Jeu entier
    """
    def __init__(self):
        pm.init()
        self.game = Game().init()
        self.game.activate()

    def update(self):
        """
        Actualisation de la frame
        """
        pm.screen.fill((80, 80, 90))
        pm.states.update()

if __name__ == '__main__':
    main = Main()
    pm.run(main.update)