import pygame
import pygame_manager as pm
from _ball import Ball
from _paddle import Paddle


class Game(pm.states.State):
    """
    Une partie de jeu
    """
    def __init__(self):
        super().__init__('game')
        self.players = 1

        # fond
        self.board = pygame.Surface((1440, 1080))
        self.board_rect = self.board.get_rect(center=pm.screen.center)

        # bordure
        self.border_width = 3
        self.border = pygame.Rect(
            self.board_rect.left - self.border_width, 
            self.board_rect.top - self.border_width, 
            self.board_rect.width + 2 * self.border_width, 
            self.board_rect.height + 2 * self.border_width
        )
        self.border_color = (230, 230, 230)

        # objets
        self.ball = None    # balle
        self.paddles = []   # raquettes

    def init(self):
        """
       Initialisation d'une partie
        """
        # balle
        self.ball = Ball()

        # raquettes
        offset = 50
        self.paddles.append(Paddle(offset, self.board_rect.height / 2, up=pygame.K_z, down=pygame.K_s))
        if self.players == 2:
            self.paddles.append(Paddle(self.board_rect.width - offset, self.board_rect.height / 2, up=pygame.K_UP, down=pygame.K_DOWN))
        
        pm.states.switch("game") 
        return self

    def update(self):
        """
        Actualisation de la frame
        """
        # fond du jeu
        self.board.fill((0, 0, 15))

        # balle
        self.ball.update(self.board)
        
        # raquettes
        for paddle in self.paddles:
            paddle.update(self.board)

        pm.screen.blit(self.board, self.board_rect)
        pygame.draw.rect(pm.screen.surface, self.border_color, self.border, self.border_width)
