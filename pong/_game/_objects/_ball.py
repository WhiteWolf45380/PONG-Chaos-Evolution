# ======================================== IMPORTS ========================================
from ..._core import pm, pygame
import math
import random

# ======================================== OBJET ========================================
class Ball:
    """
    Balle
    """
    def __init__(self, radius: int=20, color: tuple[int]=(255, 255, 255)):
        # design
        self.color = color
        self.trail = []
        self.trail_limit = 8

        # taille
        self.radius = radius

        # position
        self.x = float(pm.states["game"].surface_width / 2)
        self.y = float(pm.states["game"].surface_height / 2)

        # angle
        self.disabled_side = random.choice(("left", "right")) if pm.states["game"].game_mode != 1 else "right"
        self.angle = (random.randint(15, 35) if self.disabled_side == "left" else random.randint(145, 165)) * random.choice((-1, 1))
        self.angle_epsilon = math.radians(5) # bruit dans le rebond
        self.angle_min = 15
        self.angle_max = 35

        # paramètres
        self.celerity_min = 700
        self.celerity_max = 2500
        self.celerity = self.celerity_min
        self.celerity_variation_time = 240

        # contrainte de déplacement
        self.x_extremum = None
        self.y_at_extremum = 0

    # ======================================== ACTUALISATION ========================================
    def update(self) -> None | int:
        """
        Actualisation de la frame
        """
        # trainée
        self.trail.append((self.x, self.y))
        while len(self.trail) > int(self.trail_limit * (pm.time.smoothfps / 60)):
            self.trail.pop(0)

        # vitesse croissante
        self.celerity = min(self.celerity + pm.time.scale_value((self.celerity_max - self.celerity_min) / self.celerity_variation_time), self.celerity_max)

        # déplacement
        celerity = pm.time.scale_value(self.celerity)
        self.x += self.dx * celerity
        self.y += self.dy * celerity

        # contrainte horizontale
        if self.x_extremum:
            self.x = min(self.x, self.x_extremum) if self.disabled_side == "left" else max(self.x, self.x_extremum)
            if self.x == self.x_extremum:
                self.y = self.y_at_extremum
        
        # contrainte verticale
        self.y = min(max(self.y, self.radius), pm.states["game"].surface_height - self.radius)
        self.check_border()

        # atteinte du côté d'un des deux joueurs
        return self.check_sides()
    
    def draw(self):
        """affichage"""
        # trainée
        for i, pos in enumerate(self.trail):
            advancement = min(max((i + 1) / (len(self.trail) + 2), 0), 1)
            color = tuple(self.color[j] + (pm.states["game"].surface_color[j] - self.color[j]) * (1 - advancement) for j in range(3))
            pygame.draw.circle(pm.states["game"].surface, color, tuple(map(int, pos)), self.radius * advancement**0.75)
        
        # balle
        pygame.draw.circle(pm.states["game"].surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(pm.states["game"].surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 1)

    # ======================================== GETTERS ========================================
    @property
    def dx(self):
        """Renvoie la composante x du vecteur déplacement"""
        return math.cos(self.angle)
    
    @property
    def dy(self):
        """Renvoie la composante y du vecteur déplacement"""
        return -math.sin(self.angle)
    
    def get_vect(self):
        """Renvoie le vecteur déplacement"""
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
        
    def colliderect(self, rect: pygame.Rect):
        """
        Vérifie la collision avec une raquette

        Args:
            rect (pygame.Rect) : Rectangle de la raquette
        """
        side = "left" if rect.centerx < pm.states["game"].surface_width / 2 else "right"
        if side == self.disabled_side:
            # wall game
            if pm.states["game"].game_mode == 1:
                self.x_extremum = None
            return
        
        closest_x = min(max(self.x, rect.left), rect.right) # coordonnée x du rectangle la plus proche du centre
        closest_y = min(max(self.y, rect.top), rect.bottom) # coordonnée y du rectangle la plus proche du centre
        distance = self.get_distance(closest_x, closest_y)  # distance entre le rectangle et le centre du cercle
        
        # rebond
        if distance <= self.radius: # si dans le cercle
            normal_vect = pm.geometry.Vector(self.x, self.y) - pm.geometry.Vector(closest_x, closest_y) # angle du vecteur normal à la raquette
            self.bounce(math.atan2(-normal_vect.y, normal_vect.x))
            self.disabled_side = side
        
        # pas de rebond
        else:
            edge = rect.right + self.radius if side == "left" else rect.left - self.radius
            inter_y = self.y + self.d.y * (edge - self.x) / self.d.x
            if rect.top <= inter_y <= rect.bottom:
                self.x_extremum = edge
                self.y_at_extremum = inter_y
            else:
                self.x_extremum = None

    def collidewalls(self):
        """
        Vérifie la collision avec les murs
        """
        if self.y - self.radius <= 0 or self.y + self.radius >= pm.states["game"].surface_height:
            self.bounce(random.randint(*self.bounce_plage) / 100, -random.randint(*self.bounce_plage) / 100)
            self.y = max(self.radius, min(self.y, pm.states["game"].surface_height - self.radius))

    def collidesides(self):
        """
        Vérifie si la balle a atteint une extremité
        """
        if pm.states["game"].game_mode == 1:    # wall game
            return self.collidesides_wallgame()

        if self.x - self.radius <= 0:
            return 2
        elif self.x + self.radius >= pm.states["game"].surface_width:
            return 1
        return 0
    
    def collidesides_wallgame(self):
        """
        Vérifie si la balle a atteint une extremité (wall game)
        """
        side = "left" if self.x < pm.states["game"].surface_width / 2 else "right"
        if self.x - self.radius <= 0:
           return max(1, pm.states["game"].score)
        if self.x + self.radius >= pm.states["game"].surface_width and side != self.disabled_side:
            self.bounce(-random.randint(*self.bounce_plage) / 100, random.randint(*self.bounce_plage) / 100)
            self.disabled_side = side
            pm.states["game"].score += 1
        return 0
    
    def distance(self, x: int|float, y: int|float) -> float:
        """
        Renvoie la distance entre le centre de la balle et la point

        Args:
            x (int, float) : coordonnée x du point
            y (int, float) : coordonnée y du point
        """
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)