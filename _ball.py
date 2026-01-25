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
        self.disabled_side = random.choice(("left", "right"))   # côté dont on ignore la collision
        self.start_angle = (random.randint(20, 35) if self.disabled_side == "left" else random.randint(145, 160)) * random.choice((-1, 1))
        self.start_angle_radians = math.radians(self.start_angle)

        # design
        self.color = color

        # taille
        self.radius = radius

        # position
        self.x = pm.states["game"].surface_width / 2
        self.y = pm.states["game"].surface_height / 2
        self.vect = self.vect_from_angle(self.start_angle_radians)

        # paramètres
        self.celerity_min = 600
        self.celerity_max = 2000
        self.celerity = self.celerity_min
        self.celerity_variation_time = 120  # temps total d'augmentation de la vitesse (en secondes)

    def update(self) -> None | int:
        """
        Actualisation de la frame
        """
        # déplacement
        celerity = pm.time.scale_value(self.celerity)
        self.x += self.dx * celerity
        self.y = min(max(self.y + self.dy * celerity, self.radius), pm.states["game"].surface_height - self.radius)

        # vitesse croissante
        self.celerity = min(self.celerity + pm.time.scale_value((self.celerity_max - self.celerity_min) / self.celerity_variation_time), self.celerity_max)
        print(round(self.celerity))

        # collision contre la bordure
        self.check_border()

        # atteinte du côté d'un des deux joueurs
        goal = self.check_goal()
        if goal != 0:
            return goal
        
        # affichage
        pygame.draw.circle(pm.states["game"].surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(pm.states["game"].surface, (0, 0, 0), (self.x, self.y), self.radius, 1)
        
    def check_collide(self, rect: pygame.Rect):
        """
        Vérifie la collision avec une raquette

        Args:
            rect (pygame.Rect) : Rectangle de la raquette
        """
        side = "left" if rect.centerx < pm.states["game"].surface_width / 2 else "right"
        if side == self.disabled_side:
            return
        closest_x = min(max(self.x, rect.left), rect.right)
        closest_y = min(max(self.y, rect.top), rect.bottom)
        distance = self.get_distance(closest_x, closest_y)
        if distance <= self.radius:
            self.scale(-1, 1)
            self.disabled_side = side

    def check_border(self):
        """
        Vérifie la collision avec les murs
        """
        if self.y - self.radius <= 0 or self.y + self.radius >= pm.states["game"].surface_height:
            self.scale(1, -1)

    def scale(self, dx: float=0, dy: float=0):
        """
        Modifie le déplacmeent de la balle

        Args:
            dx (float) : facteur dx
            dy (float) : facteur dy
        """
        self.dx = dx * self.dx
        self.dy = dy * self.dy

    def check_goal(self):
        """
        Vérifie si la balle a atteint une extremité
        """
        if self.x - self.radius <= 0:
            return 2
        elif self.x + self.radius >= pm.states["game"].surface_width:
            return 1
        return 0

    @property
    def dx(self) -> float:
        """
        Renvoie la composante x du vecteur déplacement
        """
        return self.vect[0]
    
    @dx.setter
    def dx(self, value: int|float):
        """
        Fixe la composante x du vecteur déplacement
        """
        if not isinstance(value, (int, float)):
            raise TypeError("dx must be an integer or float")
        self.vect[0] = value
    
    @property
    def dy(self) -> float:
        """
        Renvoie la composante y du vecteur déplacement
        """
        return self.vect[1]
    
    @dy.setter
    def dy(self, value: int|float):
        """
        Fixe la composante y du vecteur déplacement
        """
        if not isinstance(value, (int, float)):
            raise TypeError("dy must be an integer or float")
        self.vect[1] = value
    
    @property
    def angle(self) -> float:
        """
        Renvoie l'angle entre le vecteur déplacement et le vecteur (1, 0)
        """
        return math.atan2(-self.dy, self.dx)
    
    def get_distance(self, x: int|float, y: int|float) -> float:
        """
        Renvoie la distance entre le centre de la balle et la point

        Args:
            x (int, float) : coordonnée x du point
            y (int, float) : coordonnée y du point
        """
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)

    def get_norm(self, vect: tuple[float, float]) -> float:
        """
        Renvoie la norme d'un vecteur

        Args:
            vect (tuple) : le vecteur dont on veut connaître la norme
        """
        return math.sqrt(sum(x**2 for x in vect))
    
    def normalize(self, vect: tuple[float, float]) -> tuple[float, float]:
        """
        Renvoie le vecteur normalisé

        Args:
            vect (tuple) : vecteur à normaliser
        """
        norm = self.get_norm(vect)
        if norm == 0:   # vecteur nul
            return vect
        return [x / norm for x in vect]
    
    def vect_from_angle(self, angle: int|float) -> tuple[float, float]:
        """
        Renvoie le vecteur normalisé pour un angle donné

        Args:
            angle (int, float) : angle entre le vecteur (1, 0) et le vecteur renvoyé
        """
        dx = math.cos(angle)
        dy = -math.sin(angle)
        return self.normalize((dx, dy))