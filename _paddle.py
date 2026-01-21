import pygame
import pygame_manager as pm


class Paddle:
    """
    Raquette d'une joueur
    """
    def __init__(self, player: int=1, width: int=10, height: int=30, offset_x: int= 50, color: tuple[int]=(255, 255, 255)):
        # profil
        self.player = player
        self.color = color

        # taille
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        # position
        self.x = pm.screen.width - offset_x if player == 1 else offset_x
        self.y = pm.screen.height / 2
        self.rect.center = (self.x, self.y)

        # paramètres
        self.celerity = 10

    def update(self):
        """
        Actualisation de la frame
        """
        self.rect.center = (self.x, self.y)
        pygame.draw.rect(pm.screen, self.color, self.rect)
    
    def move_up(self):
        """
        Se dirige vers le haut
        """
        self.y = max(self.height / 2, self.y - pm.time.scale_value(self.celerity))
    
    def move_down(self):
        """
        Se dirige vers le bas
        """
        self.y = max(self.height / 2, self.y + pm.time.scale_value(self.celerity))