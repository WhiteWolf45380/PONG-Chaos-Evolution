# ======================================== IMPORTS ========================================
from ..._core import pm
from typing import Iterable, Optional

from ._panels import Menu

# ======================================== ETAT ========================================
class Modifiers(pm.states.State):
    """
    Modification des paramètres de la partie
    """
    def __init__(self):
        # Initialisation de l'état
        super().__init__('modifiers_menu')

        # Paramètres de la partie
        self.params = {}

        # Catégorie: Ball
        self.add("radius", 20, category="ball", add_prefix=True)                                        # (int)  : rayon de la balle
        self.add("color", (255, 255, 255), category="ball", add_prefix=True)                            # (color): couleur de la balle
        self.add("trail", True, category="ball", add_prefix=True)      
        self.add("trail_limit", 8, category="ball", add_prefix=True)                                    # (bool) : activation de la traînée
        self.add("celerity_min", 600, category="ball", add_prefix=True)                                 # (int)  : vitesse initiale de la balle
        self.add("celerity_max", 2000, category="ball", add_prefix=True)                                # (int)  : vitesse finale de la balle
        self.add("acceleration_duration", 120, category="ball", add_prefix=True)                        # (int)  : durée d'accéleration de la balle en secondes
        self.add("angle_min", 15, category="ball", add_prefix=True)                                     # (int)  : angle minimal de déplacement de la balle
        self.add("angle_max", 35, category="ball", add_prefix=True)                                     # (int)  : angle maximal de déplacement de la balle

        # Catégorie: Paddle
        self.add("size", 100, category="paddle", add_prefix=True)                                       # (int)  : hauteur de la raquette
        self.add("color", (255, 255, 255), category="paddle", add_prefix=True)                          # (color): couleur de la raquette
        self.add("celerity", 500, category="paddle", add_prefix=True)                                   # (int)  : vitesse de la raquette
        self.add("side", 0, category="paddle", modes=['wall_game', 'solo'], add_prefix=True)            # (int)  : côté de la raquette

        # Panel du menu
        self.menu = Menu()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    # ======================================== ENREGISTREMENT ========================================
    def add(self, name: str, value: object = None, category: Optional[str] = None, modes: Optional[str] | Optional[Iterable[str]] = None, add_prefix: bool = False):
        """
        Ajoute un nouveau paramètre de partie

        Args:
            name (str): nom du paramètre
            value (object): valeur par défaut du paramètre
            category (str | None): catégorie du paramètre (pour l'organisation)
            mode (str | Iterable[str] | None): mode(s) associé(s) à ce paramètre
            add_prefix (bool): ajoute automatquement un prefix selon la catégorie
        """
        prefix = f"{category}_" if add_prefix and category is not None else ""
        name = prefix + name

        if name in self.params:
            raise AttributeError(f"Parameter {name} already exists")
        
        # Normalise le mode en liste
        if isinstance(modes, str):
            modes = [modes]
        elif modes is None:
            modes = []
        
        self.params[name] = {
            "value": value,
            "category": category,
            "modes": modes
        }

    # ======================================== GETTERS ========================================
    def __getattr__(self, name: str):
        """Renvoie un paramètre de la partie"""
        if 'params' in self.__dict__ and name in self.params:
            return self.params[name]["value"]
        raise AttributeError(name)
    
    def __getitem__(self, name: str):
        """Renvoie un paramètre de la partie"""
        if name not in self.params:
            raise KeyError(f"Parameter {name} does not exist")
        return self.params[name]["value"]
    
    def get(self, name: str, index: Optional[int] = None):
        """
        Renvoie un paramètre de partie

        Args:
            name (str): nom du paramètre
            index (int | None): indice du paramètre (si itérable)
            
        Returns:
            Valeur du paramètre (ou élément à l'index si spécifié)
        """
        if name not in self.params:
            raise AttributeError(f"Parameter {name} does not exist")
        value = self.params[name]["value"]
        if index is not None:
            return value[index]
        return value
    
    def get_by_category(self, category: str | None, remove_prefix: bool = False) -> dict:
        """
        Renvoie tous les paramètres d'une catégorie

        Args:
            category (str | None): catégorie à récupérer (None pour les paramètres sans catégorie)
            remove_prefix (bool): retire le préfixe des paramètres
            
        Returns:
            Dictionnaire {nom: valeur} des paramètres de cette catégorie
        """
        prefix = f"{category}_" if category is not None else None
        result = {}
        for name, param in self.params.items():
            if param["category"] != category:
                continue

            key = name
            if remove_prefix and prefix and name.startswith(prefix):
                key = name[len(prefix):]

            result[key] = param["value"]
        return result
    
    def get_by_mode(self, mode: str | None) -> dict:
        """
        Renvoie tous les paramètres d'un mode de jeu

        Args:
            mode (str | None): mode de jeu à vérifier (None pour les paramètres globaux)
            
        Returns:
            Dictionnaire {nom: valeur} des paramètres compatibles avec ce mode
        """
        return {
            name: param["value"]
            for name, param in self.params.items()
            if (mode is None and not param["modes"]) or mode in param["modes"]
        }
    
    def get_categories(self) -> list[str]:
        """
        Renvoie la liste de toutes les catégories

        Returns:
            Liste des noms de catégories uniques
        """
        categories = {param["category"] for param in self.params.values()}
        return list(categories)
    
    # ======================================== SETTERS ========================================
    def __setattr__(self, name: str, value: object):
        """Modifie un paramètre de partie"""
        if 'params' in self.__dict__ and name in self.params:
            self.params[name]["value"] = value
        else:
            super().__setattr__(name, value)
    
    def __setitem__(self, name: str, value: object):
        """Modifie un paramètre de partie"""
        if name not in self.params:
            raise KeyError(f"Parameter {name} does not exist")
        self.params[name]["value"] = value
    
    def set(self, name: str, value: object, index: Optional[int] = None):
        """
        Modifie un paramètre de partie

        Args:
            name (str): nom du paramètre
            value (object): valeur associée
            index (int | None): indice du paramètre (si c'est un itérable)
        """
        if name not in self.params:
            raise AttributeError(f"Parameter {name} does not exist")
        
        if index is not None:
            self.params[name]["value"][index] = value
        else:
            self.params[name]["value"] = value