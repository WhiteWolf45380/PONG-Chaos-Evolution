# ======================================== IMPORTS ========================================
from ..._core import ctx, pm

# ======================================== OBJET ========================================
class Paddle(pm.entities.RectEntity):
    """
    Raquette d'une joueur
    """
    OFFSET = 50
    def __init__(self, side: int = 0, player: int = 1, status: str = None):
        # Panel de vue
        self.view: pm.types.Panel = pm.panels["game_view"]

        # Propriétés
        self.properties: dict = ctx.modifiers.get_by_category("paddle", remove_prefix=True)

        # Statut
        self.available_status = ('player', 'friend', 'ennemy')
        self.side = side
        self.player = player
        self.status = status

        # Initialisation de l'entité
        super().__init__(0, 0, self["size"] / 6, self["size"], self["border_radius"], zorder=2, panel="game_view")
        self.sides_center: dict = {
            0: (self.OFFSET, self.view.centery),
            1: (self.view.width - self.OFFSET, self.view.centery)
        }

        # Seconde initialisation
        self.init()

    def init(self):
        """Initialisation des constantes"""
        # Position
        self.center = self.sides_center.get(self.side, self.sides_center[0])

        # Déplacement
        self.celerity: int = 700

        # Paramètres dynamiques
        self.cooldown: float = 0

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation de la frame"""
        mode = pm.states.get_object(pm.states.get_active_by_layer(2))
        if not mode.playing:
            return

        # Actualisation du cooldown
        self.cooldown = max(0, self.cooldown - pm.time.dt)
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def reset(self):
        """Remise à zéro"""
        self.init()

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
    
    def get_side(self) -> int:
        """Renvoie le côté"""
        return self.side
    
    def get_player(self) -> int:
        """Renvoie le joueur"""
        return self.player
    
    def get_status(self) -> str | None:
        """Renvoie le statut"""
        return self.status
    
    # ======================================== SETTERS ========================================
    def set_side(self, side: int):
        """Fixe le côté"""
        self.side = side

    def set_player(self, player: int):
        """Fixe le joueur"""
        self.player = player

    def set_status(self, status: str):
        """Fixe le statut"""
        self.status = status
        self.color = self[f"color_{status if status in self.available_status else 'default'}"]