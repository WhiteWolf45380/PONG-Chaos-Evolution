# ======================================== IMPORTS ========================================
from __future__ import annotations
from ...._core import ctx, pm, pygame
import math
import random

# ======================================== OBJET ========================================
class BallObject(pm.entities.CircleEntity):
    """
    Balle
    """
    def __init__(self):
        # Panel de vue
        self.view = pm.panels["main_menu_view"]

        # Paramètres
        radius = 15
        x = random.randint(int(self.view.width * 0.1), int(self.view.width * 0.9))
        y = random.randint(int(self.view.height * 0.1), int(self.view.height * 0.9))

        # Init de la super-classe
        super().__init__((x, y), radius, zorder=1, panel=str(self.view))

        # Propriétés
        self.color = (255, 255, 255)
        self.border = True
        self.border_width = 2
        self.border_color = (120, 120, 120)
        self.border_around = True

        # Traînée       
        self.trail = []
        self.trail_limit = 6

        # Angle
        self.angle_min = math.radians(20)
        self.angle_max = math.radians(50)
        self.angle = (random.uniform(self.angle_min, self.angle_max) + random.choice([0, math.pi / 2])) * random.choice([-1, 1])
        self.bouncing_epsilon = math.radians(10)

        # Déplacement
        self.celerity = random.randint(800, 1200)

    # ======================================== ACTUALISATION ========================================
    def update(self) -> None | int:
        """
        Actualisation de la frame
        """
        # Trainée
        self.trail.append((self.centerx, self.centery))
        while len(self.trail) > int(self.trail_limit):
            self.trail.pop(0)

        # Déplacement
        celerity = pm.time.scale_value(self.celerity)
        self.centerx += self.dx * celerity
        self.centery += self.dy * celerity

        # Collision avec les murs horizontaux
        self.collidehorizontal()

        # Collision avec les murs verticaux
        self.collidevertical()
    
    def draw_behind(self, surface: pygame.Surface):
        """affichage derrière la balle"""
        self.draw_trail_continuous(surface)

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
                color = tuple(int(self.color[k] + (self.view.background_color[k] - self.color[k]) * (1 - advancement))for k in range(3))
                radius = self.radius * advancement**0.75
                
                pygame.draw.circle(surface, color, (int(pos_x), int(pos_y)), max(1, int(radius)))

    # ======================================== GETTERS ========================================
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
        angle += random.uniform(-self.bouncing_epsilon, self.bouncing_epsilon)

        # Clamp
        sign = 1 if angle >= 0 else -1
        abs_angle = abs(angle)
        if abs_angle > math.pi / 2: abs_angle = min(math.pi - self.angle_min, max(math.pi - self.angle_max, abs_angle))
        else: abs_angle = min(self.angle_max, max(self.angle_min, abs_angle))
        self.angle = sign * abs_angle

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
            self.bounce(pm.geometry.Vector(1, 0))
        elif self.right >= self.view.width:
           self.bounce(pm.geometry.Vector(-1, 0))