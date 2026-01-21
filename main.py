import pygame
import pygame_manager as pm # package personnel pour pygame
from _game import Game


class Main:
    """
    Jeu entier
    """
    def __init__(self):
        pm.init()

    def init(self):
        self.game = Game().init()
        pm.states.activate("game")

    def update(self):
        """
        Actualisation de la frame
        """
        pm.screen.fill((80, 80, 90))
        pm.states.update_current()

if __name__ == '__main__':
    main = Main()
    pm.run(main.update)