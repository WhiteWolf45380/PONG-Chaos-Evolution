import pygame
import pygame_manager as pm


class Paddle:
    """
    Raquette d'une joueur
    """
    def __init__(self, x: int=0, y: int=0, width: int=20, height: int=160, color: tuple[int]=(255, 255, 255), up: int=None, down: int=None):
        # design
        self.color = color

        # taille
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        # position
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)

        # touches
        self.up = up
        self.down = down

        # handlers de déplacement
        pm.inputs.add_listener(up, self.move_up, repeat=True)
        pm.inputs.add_listener(down, self.move_down, repeat=True)

        # paramètres
        self.celerity = 700

    def update(self):
        """
        Actualisation de la frame
        """
        self.rect.center = (self.x, self.y)
        pygame.draw.rect(pm.states["game"].surface, self.color, self.rect)

    def is_playing(self):
        """
        Prédicat de l'état actif du jeu
        """
        return self.main.current_state
    
    def move_up(self):
        """
        Se dirige vers le haut
        """
        self.y = max(self.height / 2, self.y - pm.time.scale_value(self.celerity))
    
    def move_down(self):
        """
        Se dirige vers le bas
        """
        self.y = min(pm.states["game"].surface_height - self.height / 2, self.y + pm.time.scale_value(self.celerity))