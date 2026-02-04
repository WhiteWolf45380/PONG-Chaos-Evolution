# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, pygame, TYPE_CHECKING
import math
import random

if TYPE_CHECKING:
    from ._paddle import Paddle

# ======================================== OBJET ========================================
class Ball(pm.entities.CircleEntity):
    """
    Balle
    """
    def __init__(self):
        # Panel de vue
        self.view = pm.panels["game_view"]

        # Propriétés
        self.properties = ctx.modifiers.get_by_category("ball", remove_prefix=True)

        # Init de la super-classe
        super().__init__(self.view.center, self.ball_radius, zorder=0, panel="game_view")

        # Traînée        
        self.trail = []

        # Angle
        self.disabled_side = random.choice(("left", "right")) if ctx.modes.selected != 1 else "right"
        self.angle = (random.randint(15, 35) if self.disabled_side == "left" else random.randint(145, 165)) * random.choice((-1, 1))
        self.angle_epsilon = math.radians(5) # bruit dans le rebond
        self.angle_min = 15
        self.angle_max = 35

        # Déplacement
        self.celerity_min = 700
        self.celerity_max = 2500
        self.celerity = self.celerity_min
        self.celerity_variation_time = 240

    # ======================================== ACTUALISATION ========================================
    def update(self) -> None | int:
        """
        Actualisation de la frame
        """
        # Détermination du côté
        side = int(self.centerx // (0.5 * self.view.width))
        side_paddle: Paddle = getattr(ctx.game.current, f'paddle_{side}')

        # Trainée
        self.trail.append((self.centerx, self.centery))
        while len(self.trail) > int(self.trail_limit * (pm.time.smoothfps / 60)):
            self.trail.pop(0)

        # Vitesse croissante
        self.celerity = min(self.celerity + pm.time.scale_value((self.celerity_max - self.celerity_min) / self.celerity_variation_time), self.celerity_max)
        celerity = pm.time.scale_value(self.celerity)

        # Déplacement
        pos_0 = pm.geometry.Point(self.center)
        self.centerx += self.dx * celerity
        self.centery += self.dy * celerity
        pos_1 = pm.geometry.Point(self.center)

        # Collision contre les raquettes
        self.collidepaddle(side_paddle, pos_0, pos_1)

        # Collision avec les murs horizontaux
        self.collidehorizontal()

        # Collision avec les murs verticaux
        self.collidevertical()
    
    def draw_behind(self, surface: pygame.Surface):
        """affichage derrière la balle"""
        # Trainée
        for i, pos in enumerate(self.trail):
            advancement = min(max((i + 1) / (len(self.trail) + 2), 0), 1)
            color = tuple(self.color[j] + (self.view.color[j] - self.color[j]) * (1 - advancement) for j in range(3))
            pygame.draw.circle(surface, color, tuple(map(int, pos)), self.radius * advancement**0.75)

    # ======================================== GETTERS ========================================
    def __getattr__(self, name: str):
        """Proxy vers les propriétés"""
        if name in self.properties:
            return self.properties[name]
        return super().__getattr__(name)

    @property
    def dx(self):
        """Renvoie la composante x du vecteur déplacement normalisé"""
        return math.cos(self.angle)
    
    @property
    def dy(self):
        """Renvoie la composante y du vecteur déplacement normalisé"""
        return -math.sin(self.angle)
    
    def get_vect(self):
        """Renvoie le vecteur déplacement normalisé"""
        return pm.geometry.Vector(self.dx, self.dy)

    # ======================================== METHODES DYNAMIQUES ========================================
    def bounce(self, normal_angle: int|float):
        """
        Fait rebondir la balle

        Args:
            normal_angle (int|float) : angle du vect normal extérieur (radians)
        """
        self.angle = 2 * normal_angle - self.angle                                                                  # réflexion mirroir
        self.angle += random.uniform(-self.angle_epsilon, self.angle_epsilon)                                       # bruit
        self.angle = (self.angle + math.pi) % (2 * math.pi) - math.pi                                               # normalisation
        self.angle = (self.angle / abs(self.angle)) * min(max(abs(self.angle), self.angle_min), self.angle_max)     # clamp

    def collidepaddle(self, paddle: Paddle, p0: pm.types.PointObject, p1: pm.types.PointObject): 
        """
        Vérifie si déplacement de la balle rencontre une raquette

        Args:
            p0 (pm.geometry.Point) : position initiale
            p1 (pm.geometry.Point) : position finale
        """
        if abs(p1.x - self.view.centerx) >= abs(paddle.centerx - 0.5 * paddle.width - self.view.centerx):
            line = pm.geometry.Line(p0, p1 - p0)

            rect_inflation = 2 * self.radius
            rect = pm.geometry.Rect(point=(0, 0), width=paddle.width + rect_inflation, height=paddle.height + rect_inflation, border_radius=paddle.border_radius)

            intersections = rect._line_intersection(line)
            if intersections:
                I = min(intersections, key=lambda P: p0.distance(P))
                normal = pm.geometry.Circle(I, self.radius).rect_collision_normal(paddle.rect)
                self.bounce(normal)
    
    def collidehorizontal(self):
        """Vérifie la collision avec les murs horizontaux"""
        self.centery = min(max(self.centery, self.radius), self.view.height - self.radius)
        if self.top <= 0:
            self.bounce(pm.geometry.Vector(0, 1))
        elif self.bottom >= self.view.height:
            self.bounce(pm.geometry.Vector(0, -1))
    
    def collidevertical(self):
        """Vérifie la collision avec les murs verticaux"""
        self.centerx = min(max(self.centerx, self.radius), self.view.width - self.radius)
        if self.left <= 0:
            _end = ctx.game.current.is_end(0)
            if not _end: self.bounce(pm.geometry.Vector(1, 0))
        elif self.right >= self.view.width:
            _end = ctx.game.current.is_end(1)
            if not _end: self.bounce(pm.geometry.Vector(-1, 0))