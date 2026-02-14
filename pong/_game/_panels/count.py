from ..._core import pm

# ======================================== PANEL ========================================
class GameCount(pm.panels.Panel):
    """
    Panel de compte à rebours avant le début du jeu
    """
    def __init__(self, width: int = 1440, height: int = 1080):
        super().__init__('game_count', predecessor='game_view', rect=(0, 0, width, height), centered=True, srcalpha=True)
        self.send_to_back()

        # Fond
        self.background = (0, 0, 0, 0)

        # Configuration du décompte
        self.count_values = [3, 2, 1]
        self.current_index = 0
        self.animation_timer = 0.0
        self.animation_duration = 1.0
        
        # Double buffering
        self.text_current = pm.ui.Text(
            x=self.centerx,
            y=self.centery,
            text="3",
            font_size=256,
            font_color=(255, 255, 255),
            shadow=True,
            shadow_offset=3,
            anchor="center",
            panel=str(self),
            zorder=2,
        )
        self.text_current.visible = False
        
        self.text_next = pm.ui.Text(
            x=self.centerx,
            y=self.centery,
            text="2",
            font_size=256,
            font_color=(255, 255, 255),
            shadow=True,
            shadow_offset=3,
            anchor="center",
            panel=str(self),
            zorder=2,
        )
        self.text_next.visible = False

        # Voile assombrissant
        self.curtain = pm.ui.Surface(
            x=0,
            y=0,
            width=self.width,
            height=self.height,
            color=(0, 0, 0, 255),
            zorder=1,
            panel=str(self),
        )
        self.curtain.visible = False
    
    # ======================================== FOND ========================================
    def draw_back(self, surface):
        surface.fill(self.background)

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualise l'animation du décompte"""
        self.animation_timer += pm.time.dt
        progress = min(self.animation_timer / self.animation_duration, 1.0)

        # Animation : grossissement puis rétrécissement (effet de rebond)
        scale_factor = 1 - 4 * (progress - 0.5) ** 3
        scale_factor = max(0.1, min(1.0, scale_factor))

        # Appliquer l'animation au texte actuel
        self.text_current.reset()
        self.text_current.set_alpha(int(255 * scale_factor))
        self.text_current.scale(scale_factor)

        # Passer au chiffre suivant quand l'animation est terminée
        if progress >= 1.0:
            self.current_index += 1
            
            # Fin du décompte
            if self.current_index >= len(self.count_values):
                self.deactivate()
                return
            
            # Échanger les textes et préparer le suivant
            self._swap_texts()

    # ======================================== HOOKS ========================================
    def on_enter(self):
        """Initialise le panel au démarrage"""
        super().on_enter()
        
        # Réinitialiser l'état
        self.current_index = 0
        self.animation_timer = 0.0
        
        # Préparer les deux premiers textes
        self.text_current.text = str(self.count_values[0])
        self.text_current.visible = True
        self.text_current.reset()
        
        if len(self.count_values) > 1:
            self.text_next.text = str(self.count_values[1])
            self.text_next.reset()
        
        self.text_next.visible = False
        
        # Afficher le rideau avec fondu
        self.curtain.fade_out(duration=0.3, start_alpha=255, target_alpha=150)

    def on_exit(self):
        """Termine le décompte et lance le jeu"""
        self.text_current.visible = False
        self.text_current.reset()
        self.text_next.visible = False
        self.text_next.reset()
        self.curtain.fade_out(0.3)
        self.current_index = 0
        pm.states[pm.states.get_active_by_layer(2)].unfreeze()
        return super().on_exit()
    
    # ======================================== GETTERS ========================================
    def get_count(self) -> list:
        """Retourne la séquence du décompte"""
        return self.count_values.copy()

    
    def set_count(self, count_list: list):
        """Définit la séquence du décompte"""
        self.count_values = count_list.copy()
    
    # ======================================== METHODES PRIVEES ========================================
    def _swap_texts(self):
        """Échange les deux textes et prépare le suivant"""
        # Cacher le texte qui vient de finir son animation
        self.text_current.visible = False
        self.text_current.reset()
        
        # Échanger les références
        self.text_current, self.text_next = self.text_next, self.text_current
        
        # Préparer le texte suivant (si il en reste)
        if self.current_index + 1 < len(self.count_values):
            self.text_next.text = str(self.count_values[self.current_index + 1])
            self.text_next.reset()
        
        # Afficher et configurer le nouveau texte actuel
        self.text_current.text = str(self.count_values[self.current_index])
        self.text_current.visible = True
        self.text_current.reset()
        
        # Réinitialiser le timer
        self.animation_timer = 0.0