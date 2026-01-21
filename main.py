import pygame
import pygame_manager as pm # package personnel pour pygame
from _game import Game


class Main:
    """
    Jeu entier
    """
    def __init__(self):
        pm.init()
        
        self.game = Game()
        self.game.init()

    def update(self):
        """
        Actualisation de la frame
        """
        self.game.update()


if __name__ == '__main__':
    main = Main()
    pm.run(main.update)
