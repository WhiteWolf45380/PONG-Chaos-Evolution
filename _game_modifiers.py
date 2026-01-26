import pygame
import pygame_manager as pm


class GameModifiers(pm.states.State):
    """
    Menu de modification des paramètres de la partie
    """
    def __init__(self, width: int=1920, height: int=1080):
        super().__init__('game_modifiers')

        # surface
        self.surface_width = width
        self.surface_height = height
        self.surface = pygame.Surface((self.surface_with, self.surface_height))
        self.surface_rect = self.surface.get_rect()

        # modifiers
        self.modifiers_init = {
            "ball_radius": 20,
            "ball_celerity_min": 600,
            "ball_celerity_max": 2000,
            "ball_acceleration_duration": 120,
            "ball_trail": True,
            "paddle_size": 100,
            "paddle_celerity": 500,
            "player_1_side": "left",
        }
        pm.settings.create("ball_radius", 20)
