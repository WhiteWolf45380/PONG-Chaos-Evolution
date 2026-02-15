# ======================================== IMPORTS ========================================
from ...._core import ctx, pm, pygame
import math

# ======================================== PANEL ========================================
class ModesMenuChoices(pm.panels.Panel):
    """
    Panel de la liste des choix du menu des modes
    """
    def __init__(self, width : int = 1280, height : int = 700):
        super().__init__('modes_menu_choices', predecessor='modes_menu_view', rect=(0, 0, width, height), centered=True, border_width=2, border_color=(30, 40, 50), border_around=True)

        # Fond
        self.background_color = (45, 50, 55)

        # Liste des choix
        self.current_session = None
        self.all = []                   # [(name, selector), ...]

        self.margin = 15
        self.max_cols = 4
        self.choices_width = 0
        self.choices_height = 0
        self.choices_space = self.margin

    # ======================================== FOND ========================================
    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
    
    # ======================================== HOOKS ========================================
    def on_enter(self):
        pm.ui.unselect("mode")
        return super().on_enter()

    # ======================================== METHODES PUBLIQUES ========================================
    def load(self, session: str):
        """Charge un lot de modes adaptés à une session"""
        if session == self.current_session: return
        self.clear()
        for name, mode in ctx.game.modes.items():
            if session in mode.allowed_sessions:
                self.all.append((name, None))
        self.render()

    def clear(self):
        """Nettoie les choix"""
        for choice in self.all:
            if choice[1] is not None:
                choice[1].kill()
        self.all = []
    
    def render(self):
        """Génère tous les choix"""
        if not self.all:
            return
        
        # Calcul de la grille
        n = len(self.all)
        cols = min(n, self.max_cols)
        rows = math.ceil(n / cols)
        
        # Calcul de la taille des choix
        self.choices_width = min((self.width - self.margin * (cols + 1)) / cols, self.width / 2)
        self.choices_height = min((self.height - self.margin * (rows + 1)) / rows, self.height / 2)
        
        # Génération des sélecteurs
        for i, (choice, _) in enumerate(self.all):
            row = i // cols
            col = i % cols
            
            x = self.width / (cols + 1) * (col + 1)
            y = self.height / (rows + 1) * (row + 1)
            
            selector = pm.ui.RectSelector(
                x=x,
                y=y,
                width=self.choices_width,
                height=self.choices_height,
                title=choice,
                border_radius=20,
                border_width=5,
                border_color=(20, 25, 30),
                border_color_selected=(30, 50, 200),
                selection_id="mode",
                selector_id=choice,
                anchor="center",
                panel=str(self)
            )
            
            self.all[i] = (choice, selector)