import pygame
import pygame_manager as pm
from _ball import Ball
from _paddle import Paddle


class Game:
    """
    Une partie de jeu
    """
    def __init__(self):
        self.players = 1

        self.ball = None    # balle
        self.paddles = []   # raquettes

    def init(self):
        """
       Initialisation d'une partie
        """
        self.ball = Ball()
        self.paddles = []
        for i in range(self.players):   # une raquette par joueur
            self.paddles.append(Paddle(i))

    def update(self):
        """
        Actualisation de la frame
        """
        # fond du jeu
        pm.screen.fill((0, 0, 0))

        # balle
        self.ball.update()
        
        # raquettes
        for paddle in self.paddles:
            paddle.update()