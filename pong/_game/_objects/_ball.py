# ======================================== IMPORTS ========================================
from __future__ import annotations
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
    def __init__(self, check_end: callable):
        # Panel de vue
        self.view: pm.typeS.Panel = pm.panels["game_view"]

        # Propriétés
        self.properties: dict = ctx.modifiers.get_by_category("ball", remove_prefix=True)

        # Init de la super-classe
        super().__init__(self.view.center, self["radius"], zorder=1, panel="game_view")
        self.border: bool = True
        self.border_width: int = 2
        self.border_color: tuple[int, int, int] = (120, 120, 120)
        self.border_around: bool = True

        # Traînée        
        self.trail: list[tuple] = []

        # Angle
        self.disabled_side: str = random.choice(("left", "right")) if ctx.modes.selected != 1 else "right"
        self.angle: float = math.radians((random.randint(self["angle_min"], self["angle_max"]) if self.disabled_side == "left" else random.randint(180 - self["angle_max"], 180 - self["angle_min"])) * random.choice((-1, 1)))
        self.angle_min: float = math.radians(self["angle_min"])
        self.angle_max: float = math.radians(self["angle_max"])
        self.bouncing_epsilon: float = math.radians(self["bouncing_epsilon"]) # bruit dans le rebond

        # Déplacement
        self.celerity_min: int = 700
        self.celerity_max: int = 2500
        self.celerity: float = self.celerity_min

        # Fonction de vérification de fin de partie
        self.check_end: callable = check_end

    # ======================================== ACTUALISATION ========================================
    def update(self) -> None | int:
        """
        Actualisation de la frame
        """
        # Détermination du côté
        side = int(self.centerx // (0.5 * self.view.width))
        side_paddle: Paddle = getattr(pm.states.get_object(pm.states.get_active_by_layer(2)), f'paddle_{side}')

        # Trainée
        self.trail.append((self.centerx, self.centery))
        while len(self.trail) > int(self["trail_length"] * (pm.time.smoothfps / 60)):
            self.trail.pop(0)

        # Vitesse croissante
        self.celerity = min(self.celerity + pm.time.scale_value((self.celerity_max - self.celerity_min) / self["acceleration_duration"]), self.celerity_max)
        celerity = pm.time.scale_value(self.celerity)

        # Déplacement
        pos_0 = pm.geometry.Point(*self.center)
        self.centerx += self.dx * celerity
        self.centery += self.dy * celerity
        pos_1 = pm.geometry.Point(*self.center)

        # Collision contre les raquettes
        if side_paddle is not None:
            self.collidepaddle(side_paddle, pos_0, pos_1)

        # Collision avec les murs horizontaux
        self.collidehorizontal()

        # Collision avec les murs verticaux
        self.collidevertical()
    
    def draw_behind(self, surface: pygame.Surface):
        """affichage derrière la balle"""
        if self["trail"] == "discret":
            self.draw_trail_discret(surface)
        elif self["trail"] == "continuous":
            self.draw_trail_continuous(surface)

    def draw_trail_discret(self, surface: pygame.Surface):
        """Traînée par progression discrète"""
        if len(self.trail) < 2:
            return
        
        for i, pos in enumerate(self.trail):
            advancement = (i + 1) / len(self.trail)
            color = tuple(int(self["color"][j] * advancement + self.view.background_color[j] * (1 - advancement)) for j in range(3))
            radius = max(1, int(self.radius * (advancement ** 0.75)) * 0.9)
            pygame.draw.circle(surface, color, tuple(map(int, pos)), radius)

    def draw_trail_continuous(self, surface: pygame.Surface):
        """Traînée par interpolation linéaire"""
        num_segments = len(self.trail)
        if num_segments < 2:
            return
        
        current_pos = (self.centerx, self.centery)
        for i in range(num_segments):
            if i == num_segments - 1:
                start_pos = self.trail[i]
                end_pos = current_pos
            else:
                start_pos = self.trail[i]
                end_pos = self.trail[i + 1]

            subdivisions = 5
            for j in range(subdivisions):
                t = j / subdivisions
                
                pos_x = start_pos[0] + t * (end_pos[0] - start_pos[0])
                pos_y = start_pos[1] + t * (end_pos[1] - start_pos[1])
                
                advancement = (i + t) / num_segments
                color = tuple(int(self["color"][k] + (self.view.background_color[k] - self["color"][k]) * (1 - advancement))for k in range(3))
                radius = self.radius * advancement**0.75
                
                pygame.draw.circle(surface, color, (int(pos_x), int(pos_y)), max(1, int(radius)))

    # ======================================== GETTERS ========================================
    def __getitem__(self, name: str):
        """Proxy vers les propriétés"""
        if name in self.properties:
            return self.properties[name]
        raise AttributeError(name)

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
    def bounce(self, normal: pm.types.VectorObject):
        """
        Fait rebondir la balle

        Args:
            normal (pm.types.VectorObject) : vect normal extérieur (radians)
        """
        # Réflexion vectorielle
        vector = self.get_vect()
        dot = vector @ normal
        if dot >= 0: return
        vector -= 2 * (vector @ normal) * normal
        vector.normalize()

        # Calcul du nouvel angle
        angle = math.atan2(-vector.y, vector.x)
        angle = (angle + math.pi) % (2 * math.pi) - math.pi

        # Clamp
        sign = 1 if angle >= 0 else -1
        abs_angle = abs(angle)
        if abs_angle > math.pi / 2: abs_angle = min(math.pi - self.angle_min, max(math.pi - self.angle_max, abs_angle))
        else: abs_angle = min(self.angle_min, max(self.angle_max, abs_angle))
        abs_angle += random.uniform(0, self.bouncing_epsilon)
        self.angle = sign * abs_angle

    def collidepaddle(self, paddle: Paddle, p0: pm.types.PointObject, p1: pm.types.PointObject): 
        """
        Vérifie si déplacement de la balle rencontre une raquette

        Args:
            p0 (pm.geometry.Point) : position initiale
            p1 (pm.geometry.Point) : position finale
        """
        if paddle.cooldown > 0:
            return
        if abs(p1.x - paddle.centerx) <= (paddle.width / 2 + self.radius):
            line = pm.geometry.Line(p0, p1 - p0)

            rect_inflation = 2 * self.radius
            rect = pm.geometry.Rect(point=(0, 0), width=paddle.width + rect_inflation, height=paddle.height + rect_inflation, border_radius=paddle.border_radius)
            rect.center = paddle.center

            intersections = rect._line_intersection(line)
            if intersections:
                I = min(intersections, key=lambda P: p0.distance(P))
                normal: pm.types.VectorObject = pm.geometry.Circle(I, self.radius).rect_collision_normal(paddle.rect)
                self.bounce(normal)
                paddle.collision()
    
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
            if not self.check_end(0): self.bounce(pm.geometry.Vector(1, 0))
        elif self.right >= self.view.width:
            if not self.check_end(1): self.bounce(pm.geometry.Vector(-1, 0))