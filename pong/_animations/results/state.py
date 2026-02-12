# ======================================== IMPORTS ========================================
from ..._core import pm, pygame, get_path
from ._panels import ResultsAnimationView

# ======================================== ETAT ========================================
class Results(pm.states.State):
    """
    Animation d'attente avec fondus enchaînés
    """
    def __init__(self):
        # Initialisation de l'état
        super().__init__('results_animation')

        # Panel de vue
        self.view = ResultsAnimationView()
        self.bind_panel(self.view)

        # Animation
        self.duration = 3.0
        self.fade_duration = 0.7
        self.timer = 0.0

        # Message de fin de partie
        self.default_text = pm.ui.Text(
            x=self.view.centerx,
            y=self.view.centery,
            text=pm.languages("game_results_default"),
            anchor="midbottom",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=48,
            font_color=(255, 255, 255),
            shadow=True,
            panel=str(self.view),
        )
        self.default_text.visible = False

        # Message spécifique au mode de jeu
        self.text = None
        self.special_text = pm.ui.Text(
            x=self.view.centerx,
            y=self.view.centery,
            text="[Special Text]",
            anchor="midbottom",
            font_path=get_path("_assets/fonts/arcade.ttf"),
            font_size=48,
            font_color=(255, 255, 255),
            shadow=True,
            panel=str(self.view),
        )
        self.special_text.visible = False

        # Différentes phases
        self.phase = "default"
        self.phases = {
            "default": self.default_text,
            "special": self.special_text,
        }

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        self.timer += pm.time.dt
        self.update_phase()
        if self.timer >= self.duration:
            if self.phase == "default" and self.text is not None:
                self.next_phase(phase="special")
            else:
                self.end()
    
    def update_phase(self):
        """Actualisation de la phase en cours avec gestion des fondus"""
        current_text = self.phases[self.phase]
        
        if self.timer < self.fade_duration:
            fade_progress = min(1.0, max(0.0, self.timer / self.fade_duration))
            alpha = int(255 * fade_progress)
            current_text.set_alpha(alpha)
        
        elif self.timer > self.duration - self.fade_duration:
            fade_progress = min(1.0, max(0.0, (self.duration - self.timer) / self.fade_duration))
            alpha = int(255 * fade_progress)
            current_text.set_alpha(alpha=alpha)

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Lancement de l'animation"""
        self.timer = 0.0
        self.phase = "default"
        self.phases["default"].visible = True
        self.phases["default"].set_alpha(0)
        pm.inputs.add_listener(pygame.K_SPACE, self.skip)
        return super().on_enter()

    def on_exit(self):
        """Fermeture de l'animation"""
        pm.inputs.remove_listener(pygame.K_SPACE, self.skip)
        for text in self.phases.values():
            text.visible = False
        return super().on_exit()
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def load(self, text: str):
        """
        Charge un texte pour l'animation
        
        Args :
            text (str) : texte spécifique à afficher après le texte par défaut
        """
        self.text = text
        if self.text is not None:
            self.render()
        
    def render(self):
        """Génère la surface du texte"""
        self.special_text.text = self.text
    
    def next_phase(self, phase: str = None):
        """
        Passe à la prochaine phase de l'animation
        
        Args :
            phase (str) : nom de la phase à activer
        """
        self.timer = 0
        self.phases[self.phase].visible = False
        
        if phase is not None:
            self.phase = phase
            phase_text = self.phases.get(phase, self.phases["default"])
            phase_text.visible = True
            phase_text.set_alpha(0)
        else:
            self.phase = "default"
            self.phases["default"].visible = True
            self.phases["default"].set_alpha(0)

    def skip(self):
        """Passe l'animation immédiatement"""
        self.timer = self.duration

    def end(self):
        """Termine l'animation et retourne au menu principal"""
        pm.states.activate("main_menu", transition=True)