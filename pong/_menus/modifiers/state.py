# ======================================== IMPORTS ========================================
from ..._core import ctx, pm, get_folder, Path
from typing import Iterable, Optional, Any

from ._panels import ModifiersMenuView

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
        self.data_path = str(Path(get_folder()) / "data/modifiers.json")
        ctx.engine.add_final(self.save)

        # Catégorie: Players
        self.add("online_pseudo", None, category="players", to_save=True)                               # (str)  : pseudo en ligne
        self.add("p1_pseudo", 'P1', category="players")                                                 # (str)  : pseudo du joueur 1
        self.add("p2_pseudo", 'P2', category="players", sessions=["local"])                             # (str)  : pseudo du joueur 2
        self.add("p1_side", 0, category="players")                                                      # (int)  : côté du joueur 1

        # Catégorie Game
        self.add("score_limit", 3, category="game")                                                     # (int)  : score à atteindre

        # Catégorie: Ball
        self.add("radius", 15, category="ball", add_prefix=True)                                        # (int)  : rayon de la balle
        self.add("color", (255, 255, 255), category="ball", add_prefix=True)                            # (color): couleur de la balle
        self.add("trail", "continuous", category="ball", add_prefix=True)                               # (str)  : type de traînée
        self.add("trail_length", 0.13, category="ball", add_prefix=True)                                # (float): longueur de la traînée en secondes
        self.add("trail_color", (0, 200, 200), category="ball", add_prefix=True)                        # (color): couleur de la traînée
        self.add("celerity_min", 600, category="ball", add_prefix=True)                                 # (int)  : vitesse initiale de la balle
        self.add("celerity_max", 2400, category="ball", add_prefix=True)                                # (int)  : vitesse finale de la balle
        self.add("acceleration_duration", 64, category="ball", add_prefix=True)                         # (int)  : durée d'accéleration de la balle en secondes
        self.add("angle_min", 15, category="ball", add_prefix=True)                                     # (int)  : angle minimal de déplacement de la balle
        self.add("angle_max", 30, category="ball", add_prefix=True)                                     # (int)  : angle maximal de déplacement de la balle
        self.add("bouncing_epsilon", 5, category="ball", add_prefix=True)                               # (int)  : aléatoire de l'angle dans les rebonds

        # Catégorie: Paddle
        self.add("celerity", 500, category="paddle", add_prefix=True)                                   # (int)  : vitesse de la raquette
        self.add("size", 120, category="paddle", add_prefix=True)                                       # (int)  : hauteur de la raquette
        self.add("border_radius", 10, category="paddle", add_prefix=True)                               # (int)  : arrondi des coins de la raquette
        self.add("color_default", (255, 255, 255), category="paddle", add_prefix=True)                  # (color): couleur de la raquette par défaut
        self.add("border_color_default", (60, 60, 60), category="paddle", add_prefix=True)              # (color): couleur de la bordure par défaut
        self.add("color_player", (38, 166, 91), category="paddle", add_prefix=True)                     # (color): couleur de la raquette du joueur
        self.add("border_color_player", (57, 230, 20), category="paddle", add_prefix=True)              # (color): couleur de la bordure du joueur
        self.add("color_friend", (41, 121, 185), category="paddle", add_prefix=True)                    # (color): couleur de la raquette d'un ami
        self.add("border_color_friend", (0, 191, 230), category="paddle", add_prefix=True)              # (color): couleur de la bordure d'un ami
        self.add("color_ennemy", (183, 49, 44), category="paddle", add_prefix=True)                     # (color): couleur de la raquette d'un ennemi
        self.add("border_color_ennemy", (230, 59, 48), category="paddle", add_prefix=True)              # (color): couleur de la bordure par défaut

        # Panel du menu
        self.menu = ModifiersMenuView()

        # Chargement des données sauvegardées
        self.load()

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    # ======================================== ENREGISTREMENT ========================================
    def add (
        self,
        name: str,
        value: object = None,
        category: Optional[str] = None,
        sessions: Optional[str] | Optional[Iterable[str]] = None,
        modes: Optional[str] | Optional[Iterable[str]] = None,
        add_prefix: bool = False,
        to_save: bool = False
    ):
        """
        Ajoute un nouveau paramètre de partie

        Args:
            name (str): nom du paramètre
            value (object, optional): valeur par défaut du paramètre
            category (str | None, optional): catégorie du paramètre (pour l'organisation)
            sessions (str | Iterable[str], optional): sessions exclusives
            modes (str | Iterable[str], optional): modes exclusifs
            add_prefix (bool, optional): ajoute automatiquement un prefix selon la catégorie
            to_save (bool, optional): sauvegarde du paramète dans un dossier externe
        """
        prefix = f"{category}_" if add_prefix and category is not None else ""
        name = prefix + name

        if name in self.params:
            raise AttributeError(f"Parameter {name} already exists")
        
        # Normalise la session en liste
        if isinstance(sessions, str):
            sessions = [sessions]
        elif sessions is None:
            sessions = []
        
        # Normalise le mode en liste
        if isinstance(modes, str):
            modes = [modes]
        elif modes is None:
            modes = []
        
        self.params[name] = {
            "value": value,
            "category": category,
            "sessions": sessions,
            "modes": modes,
            "to_save": to_save,
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
    
    def get(self, name: str, index: Optional[int] = None, fallback: Any = None):
        """
        Renvoie un paramètre de partie

        Args:
            name (str): nom du paramètre
            index (int | None): indice du paramètre (si itérable)
            
        Returns:
            Valeur du paramètre (ou élément à l'index si spécifié)
        """
        if self.params.get(name) is None:
            return fallback
        value = self.params[name]["value"]
        if index is not None:
            return value[index]
        return value
    
    def get_with_filters(self, category: str | None = None, session: str | None = None, mode: str | None = None, remove_prefix: bool = False):
        """
        Renvoie tous les paramètres se conformant aux filtres
        
        Args:
            category (str | None): catégorie à filtrer
            session (str | None): session à filtrer
            mode (str | None): mode de jeu à filtrer
            remove_prefix (bool): retire le préfixe des paramètres
            
        Returns:
            Dictionnaire {nom: valeur} des paramètres correspondant aux filtres
        """
        prefix = f"{category}_" if category is not None else None
        result = {}
        
        for name, param in self.params.items():
            # Filtre par catégorie
            if category is not None and param["category"] != category:
                continue
            
            # Filtre par session
            if session is not None and session not in param["sessions"]:
                continue
            
            # Filtre par mode
            if mode is not None and mode not in param["modes"]:
                continue
            
            key = name
            if remove_prefix and prefix and name.startswith(prefix):
                key = name[len(prefix):]
            
            result[key] = param["value"]
        
        return result
    
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
    
    def get_by_session(self, session: str) -> dict:
        """
        Renvoie tous les paramètres d'une session

        Args:
            session (str): session à vérifier
            
        Returns:
            Dictionnaire {nom: valeur} des paramètres compatibles avec cette session
        """
        return {
            name: param["value"]
            for name, param in self.params.items()
            if session in param["sessions"]
        }
    
    def get_by_mode(self, mode: str) -> dict:
        """
        Renvoie tous les paramètres d'un mode de jeu

        Args:
            mode (str): mode de jeu à vérifier
            
        Returns:
            Dictionnaire {nom: valeur} des paramètres compatibles avec ce mode
        """
        return {
            name: param["value"]
            for name, param in self.params.items()
            if mode in param["modes"]
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
    
    # ======================================== GESTION DE DONNEES ========================================
    def load(self):
        """Charge un ensemble de paramètres"""
        try:
            data = pm.data.load(self.data_path)
            for k, v in data.items():
                self.params[k] = v
        except (FileNotFoundError, RuntimeError):
            print(f"[Data] Not file found at {self.data_path}")
    
    def save(self):
        """Sauvegarde un ensemble de paramètres"""
        try:
            data = {k: v for (k, v) in self.params.items() if v.get("to_save", False)}
            pm.data.save(data, self.data_path)
        except Exception as e:
            print(f"[Data] Saving error : {e}")