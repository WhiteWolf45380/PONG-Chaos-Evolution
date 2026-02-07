# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame

# ======================================== OBJET ========================================
class Paddle(pm.entities.RectEntity):
    """
    Raquette d'une joueur
    """
    OFFSET = 50
    def __init__(self, x: int = 0, y: int = 0):
        # Panel de vue
        self.view = pm.panels["game_view"]

        # Propriétés
        self.properties = ctx.modifiers.get_by_category("paddle", remove_prefix=True)

        # Initialisation de l'entité
        super().__init__(0, 0, self["size"] / 6, self["size"], self["border_radius"], zorder=2, panel="game_view")
        self.center = (x, y)

        # Déplacement
        self.celerity = 700

        # Paramètres dynamiques
        self.cooldown = 0  

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""
        self.cooldown = max(0, self.cooldown - pm.time.dt)
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def move_up(self):
        """Se dirige vers le haut"""
        super().move_up(pm.time.scale_value(self.celerity), min=0)
    
    def move_down(self):
        """Se dirige vers le bas"""
        super().move_down(pm.time.scale_value(self.celerity), max=(self.view.height - self.height))

    def collision(self):
        """Fixe un cooldown avant le prochain rebond"""
        self.cooldown = 0.1

    # ======================================== GETTERS ========================================
    def __getitem__(self, name: str):
        """Proxy vers les propriétés"""
        if name in self.properties:
            return self.properties[name]
        raise AttributeError(name)