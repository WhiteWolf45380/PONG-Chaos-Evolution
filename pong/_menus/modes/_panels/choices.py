# ======================================== IMPORTS ========================================
from ...._core import ctx, pm, pygame, get_path
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

        self.margin = 10
        self.padding = 40
        self.max_cols = 4

        self.choices_width = 0
        self.choices_height = 0

        # Sauvegarde des images
        self.previews = {}

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

        full_width = self.width - 2 * self.margin
        full_height = self.height - 2 * self.margin

        # Calcul de la taille des cartes        
        card_width = (full_width - self.padding * (cols + 1)) / cols
        card_height = (full_height - self.padding * (rows + 1)) / rows
        
        # Limite de taille
        max_card_width = self.width / 2
        max_card_height = self.height / 2
        
        card_width = min(card_width, max_card_width)
        card_height = min(card_height, max_card_height)
        
        # Conservation du ratio
        ratio = self.width / self.height
        if card_width / card_height > ratio:
            card_width = card_height * ratio
        else:
            card_height = card_width / ratio
        
        self.choices_width = card_width
        self.choices_height = card_height
        
        # Calcule de l'espacement
        total_cards_width = cols * card_width
        total_cards_height = rows * card_height
        
        spacing_x = (full_width - total_cards_width) / (cols + 1)
        spacing_y = (full_height - total_cards_height) / (rows + 1)
        
        # Génération des sélecteurs
        for i, (choice, _) in enumerate(self.all):
            # Calcul de la position théorique
            row = i // cols
            col = i % cols
            
            # Positionnement
            x = self.margin + spacing_x * (col + 1) + card_width * (col + 0.5)
            y = self.margin + spacing_y * (row + 1) + card_height * (row + 0.5)

            # Image
            if choice not in self.previews:
                try:
                    preview = pygame.image.load(get_path(f"_assets/modes/{choice}/preview.png")).convert()
                    overlay = pygame.Surface(preview.get_size(), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 120))
                    preview.blit(overlay, (0, 0))
                    self.previews[choice] = preview
                except Exception:
                    pass
            
            # Génération du sélecteur
            selector = pm.ui.RectSelector(
                x=x,
                y=y,
                width=card_width,
                height=card_height,
                icon=self.previews.get(choice),
                icon_keep_ratio=True,
                icon_scale_ratio=1.0,
                text=choice,
                text_size_ratio=0.8,
                font_color=(255, 255, 255),
                border_radius=20,
                border_width=4,
                border_color=(255, 255, 255),
                border_color_hover=(150, 100, 20),
                border_color_selected=(30, 50, 200),
                hover_scale_ratio=1.02,
                hover_scale_duration=0.05,
                selected_scale_ratio=0.97,
                selected_scale_duration=0.05,
                selection_id="mode",
                selector_id=choice,
                anchor="center",
                panel=str(self)
            )
            
            # Registration du sélecteur
            self.all[i] = (choice, selector)