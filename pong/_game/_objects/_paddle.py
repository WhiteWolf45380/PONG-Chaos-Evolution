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
        super().__init__(0, 0, 0.2 * self["size"], self["size"], self["border_radius"], zorder=1, panel="game_view")
        self.center = (x, y)

        # Déplacement
        self.celerity = 700

        self.up = up
        pm.inputs.add_listener(up, self.move_up, repeat=True, condition=lambda: self.is_active())
        
        self.down = down
        pm.inputs.add_listener(down, self.move_down, repeat=True, condition=lambda: self.is_active())     

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def move_up(self):
        """Se dirige vers le haut"""
        super().move_up(pm.time.scale_value(self.celerity), min=0)
    
    def move_down(self):
        """Se dirige vers le bas"""
        super().move_down(pm.time.scale_value(self.celerity), max=(self.view.height - self.height))

    # ======================================== GETTERS ========================================
    def __getitem__(self, name: str):
        """Proxy vers les propriétés"""
        if name in self.properties:
            return self.properties[name]
        raise AttributeError(name)