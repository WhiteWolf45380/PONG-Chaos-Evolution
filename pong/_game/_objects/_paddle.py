# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame

# ======================================== OBJET ========================================
class Paddle(pm.entities.RectEntity):
    """
    Raquette d'une joueur
    """
    OFFSET = 50
    def __init__(self, x: int = 0, y: int = 0, up: int = None, down: int = None):
        # Panel de vue
        self.view = pm.panels["game_view"]

        # Propriétés
        self.properties = ctx.modifiers.get_by_category("paddle", remove_prefix=True)

        # Initialisation de l'entité
        super().__init__(0, 0, self.width, self.height, self.border_radius, 1, self.view)

        # Position
        self.center = (x, y)

        # Déplacement
        self.celerity = 700

        self.up = up
        pm.inputs.add_listener(up, self.move_up, repeat=True, condition=lambda: not pm.states["game"].game_frozen)
        
        self.down = down
        pm.inputs.add_listener(down, self.move_down, repeat=True, condition=lambda: not pm.states["game"].game_frozen)     

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """
        Actualisation de la frame
        """
        self.rect.center = (self.x, self.y)

    def draw(self):
        """Affichage"""
        pygame.draw.rect(pm.states["game"].surface, self.color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(pm.states["game"].surface, (0, 0, 0), self.rect, 1, border_radius=self.border_radius)

    # ======================================== PREDICATS ========================================
    def is_playing(self):
        """
        Prédicat de l'état actif du jeu
        """
        return self.main.current_state
    
    # ======================================== METHODES DYNAMIQUES ========================================
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