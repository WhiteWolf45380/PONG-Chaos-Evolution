import pygame
import pygame_manager as pm
import math
import random


class Ball:
    """
    Balle
    """
    def __init__(self, radius: int=20, color: tuple[int]=(255, 255, 255)):
        # position initiale
        self.disabled_side = random.choice(("left", "right")) if pm.states["game"].game_mode != 1 else "right"
        self.start_angle = (random.randint(20, 40) if self.disabled_side == "left" else random.randint(140, 160)) * random.choice((-1, 1))
        self.start_angle_radians = math.radians(self.start_angle)

        # design
        self.color = color
        self.trail = []
        self.trail_limit = 10

        # taille
        self.radius = radius

        # position (garder en float pour éviter le scintillement)
        self.x = float(pm.states["game"].surface_width / 2)
        self.y = float(pm.states["game"].surface_height / 2)
        self.d = pm.geometry.Vector(*self.vect_from_angle(self.start_angle_radians))

        # paramètres
        self.celerity_min = 350
        self.celerity_max = 2000
        self.celerity = self.celerity_min
        self.celerity_variation_time = 300

        # contrainte de déplacement
        self.x_extremum = None
        self.y_at_extremum = 0

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
        self.x += self.d.x * celerity
        self.y += self.d.y * celerity

        # contrainte horizontale
        if self.x_extremum:
            self.x = min(self.x, self.x_extremum) if self.disabled_side == "left" else max(self.x, self.x_extremum)
            if self.x == self.x_extremum:
                self.y = self.y_at_extremum
        
        # contrainte verticale
        self.y = min(max(self.y, self.radius), pm.states["game"].surface_height - self.radius)
        self.check_border()

        # atteinte du côté d'un des deux joueurs
        goal = self.check_goal()
        if goal != 0:
            return goal
    
    def draw(self):
        """affichage"""
        # trainée
        for i, pos in enumerate(self.trail):
            color = tuple(self.color[j] + (pm.states["game"].surface_color[j] - self.color[j]) * min(max(1 - (i + 1) / (self.trail_limit + 1), 0), 1) for j in range(3))
            pygame.draw.circle(pm.states["game"].surface, color, tuple(map(int, pos)), self.radius)
        
        # balle
        pygame.draw.circle(pm.states["game"].surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(pm.states["game"].surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 1)

    def bounce(self, dx: float=0, dy: float=0):
        """
        Modifie le déplacement de la balle

        Args:
            dx (float) : facteur dx
            dy (float) : facteur dy
        """
        self.d.x *= dx
        self.d.y *= dy
        
    def check_collide(self, rect: pygame.Rect):
        """
        Vérifie la collision avec une raquette

        Args:
            rect (pygame.Rect) : Rectangle de la raquette
        """
        side = "left" if rect.centerx < pm.states["game"].surface_width / 2 else "right"
        if side == self.disabled_side:
            if pm.states["game"].game_mode == 1:
                self.x_extremum = None
            return
        
        closest_x = min(max(self.x, rect.left), rect.right)
        closest_y = min(max(self.y, rect.top), rect.bottom)
        distance = self.get_distance(closest_x, closest_y)
        
        if distance <= self.radius:  
            self.bounce(-1, 1)
            self.disabled_side = side
        else:
            edge = rect.right + self.radius if side == "left" else rect.left - self.radius
            inter_y = self.y + self.d.y * (edge - self.x) / self.d.x
            if rect.top <= inter_y <= rect.bottom:
                self.x_extremum = edge
                self.y_at_extremum = inter_y
            else:
                self.x_extremum = None

    def check_border(self):
        """
        Vérifie la collision avec les murs
        """
        if self.y - self.radius <= 0 or self.y + self.radius >= pm.states["game"].surface_height:
            self.bounce(1, -1)
            self.y = max(self.radius, min(self.y, pm.states["game"].surface_height - self.radius))

    def check_goal(self):
        """
        Vérifie si la balle a atteint une extremité
        """
        return getattr(self, f"check_goal_{pm.states['game'].game_mode}", self.check_goal_2)()
    
    def check_goal_1(self):
        """
        Vérifie si la balle a atteint une extremité (wall game)
        """
        side = "left" if self.x < pm.states["game"].surface_width / 2 else "right"
        if self.x - self.radius <= 0:
           return max(1, pm.states["game"].score)
        if self.x + self.radius >= pm.states["game"].surface_width and side != self.disabled_side:
            self.bounce(-1, 1)
            self.disabled_side = side
            pm.states["game"].score += 1
        return 0

    def check_goal_2(self):
        """
        Vérifie si la balle a atteint une extremité (Joueur contre Joueur)
        """
        if self.x - self.radius <= 0:
            return 2
        elif self.x + self.radius >= pm.states["game"].surface_width:
            return 1
        return 0
    
    @property
    def angle(self) -> float:
        """
        Renvoie l'angle entre le vecteur déplacement et le vecteur (1, 0)
        """
        return math.atan2(-self.d.y, self.d.x)
    
    def get_distance(self, x: int|float, y: int|float) -> float:
        """
        Renvoie la distance entre le centre de la balle et la point

        Args:
            x (int, float) : coordonnée x du point
            y (int, float) : coordonnée y du point
        """
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)
    
    def vect_from_angle(self, angle: int|float) -> tuple[float, float]:
        """
        Renvoie le vecteur normalisé pour un angle donné

        Args:
            angle (int, float) : angle entre le vecteur (1, 0) et le vecteur renvoyé
        """
        dx = math.cos(angle)
        dy = -math.sin(angle)
        return (dx, dy)