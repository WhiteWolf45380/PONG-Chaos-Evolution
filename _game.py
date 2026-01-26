import pygame
import pygame_manager as pm
from _ball import Ball
from _paddle import Paddle


class Game(pm.states.State):
    """
    Une partie de jeu
    """
    def __init__(self, width: int=1440, height: int=1080):
        super().__init__('game')
        self.game_mode = 1

        # surface de jeu
        self.surface_width = width
        self.surface_height = height
        self.surface = pygame.Surface((self.surface_width, self.surface_height))
        self.surface_rect = self.surface.get_rect(center=pm.screen.center)
        self.surface_color = (0, 0, 15)

        # bordure
        self.border_width = 3
        self.border = pygame.Rect(
            self.surface_rect.left - self.border_width, 
            self.surface_rect.top - self.border_width, 
            self.surface_rect.width + 2 * self.border_width, 
            self.surface_rect.height + 2 * self.border_width
        )
        self.border_color = (230, 230, 230)

        # lancement de la partie
        self.game_frozen = True
        def toggle_freeze(self):
            self.game_frozen = not self.game_frozen
        pm.inputs.add_listener(pygame.K_SPACE, toggle_freeze, args=[self])

        # objets
        self.ball = None    # balle
        self.paddles = []   # raquettes

        # wall game
        self.score = 0

    def init(self):
        """
       Initialisation d'une partie
        """
        # balle
        self.ball = Ball()

        # raquettes
        offset = 50
        self.paddles.append(Paddle(offset, self.surface_rect.height / 2, up=pygame.K_z, down=pygame.K_s))
        if self.game_mode == 2:
            self.paddles.append(Paddle(self.surface_rect.width - offset, self.surface_rect.height / 2, up=pygame.K_UP, down=pygame.K_DOWN))
        
        pm.states.switch("game") 
        return self

    def update(self):
        """
        Actualisation de la frame
        """
        # jeu en pause
        if self.game_frozen:
            self.draw()
            return

        # balle
        for paddle in self.paddles:
            self.ball.check_collide(paddle.rect)
        result = self.ball.update()
        if result:
            self.end(result=result)

        # raquettes
        for paddle in self.paddles:
            paddle.update()
        
        self.draw()
    
    def draw(self):
        # fond du jeu
        self.surface.fill(self.surface_color)

        # balle
        self.ball.draw()

        # raquettes
        for paddle in self.paddles:
            paddle.draw()

        # affichage de la surface
        pm.screen.blit(self.surface, self.surface_rect)
        pygame.draw.rect(pm.screen.surface, self.border_color, self.border, self.border_width)
    
    def end(self, result: int=0):
        """
        Fin de partie

        Args:
            winner (int) : le gagnant
        """
        if self.game_mode == 1:
            print(f"Score : {result}")
        else:
            print(f"Le gagnant est le joueur {result}")
        pm.stop()