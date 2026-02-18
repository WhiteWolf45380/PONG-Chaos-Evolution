# ======================================== IMPORTS ========================================
from . import ctx, pm, get_path, pygame

# ======================================== CLASSE PRINCIPALE ========================================
class Engine:
    """
    Moteur d'éxécution
    """
    def __init__(self):
        # Initialisation du framework modulable
        pm.init()

        pm.time.set_fps_limit(80)
        pm.screen.set_vsync(True)

        pm.languages.load_directory(get_path("_languages"))
        pm.languages.set_language('fr', fallback='en')

        pm.screen.set_caption("PONG : Chaos Evolution")
        pm.screen.set_icon(pygame.image.load(get_path("_assets/icons/icon.ico")))

        # Messages système
        pm.ui.set_messages_y(pm.screen.height * 0.2)
        pm.ui.set_messages_spacing(pm.screen.height * 0.02)
        self.messages_types = {
            "default": (10, 150, 20),
            "system": (180, 100, 20),
            "error": (200, 40, 60)
        }

        # Registration dans le context manager
        ctx.engine = self

        # Instanciation du jeu
        from .._game import Game

        self.game = Game()
        ctx.game = self.game

        # Instanciation des menus
        from .._menus import Main, Modes, Modifiers, Settings, Lobbies
        
        self.main = Main()
        ctx.main = self.main

        self.modes = Modes()
        ctx.modes = self.modes

        self.modifiers = Modifiers()
        ctx.modifiers = self.modifiers

        self.settings = Settings()
        ctx.settings = self.settings

        self.lobbies = Lobbies()
        ctx.lobbies = self.lobbies

        # Instanciation des animations
        from .._animations import Waiting, Results

        self.waiting = Waiting()
        ctx.waiting = self.waiting

        self.results = Results()
        ctx.results = self.results

        # Fond par défaut
        self.background = pm.ui.Surface(
            x=0,
            y=0,
            width=1920,
            height=1080,
            color=(0, 0, 40),
            gradient=True,
            gradient_color=(0, 0, 15),
            gradient_direction="vertical",
            gradient_fluctuation=True,
            gradient_fluctuation_amplitude=0.7,
            gradient_fluctuation_speed=2.0,
            gradient_brightness_pulse=False,
            gradient_brightness_amplitude=0.05,
            panel=None
        )
        self.background.visible = False
        
        # Lancement d'une partie
        pm.states.activate("main_menu", transition=True, ease_out=False, duration=1.5)

    # ======================================== ACTUALISATION FONDAMENTALE ========================================
    def update(self):
        """Actualisation de la frame"""
        pm.screen.fill((30, 30, 47))
        if not pm.states.get_active_states():
            pm.stop()

    # ======================================== DEMARRAGE INITIAL ========================================
    def run(self):
        """Lance l'éxécution"""
        pm.run(self.update)

    # ======================================== METHODES GLOBALES ========================================
    def sys_message(self, text: str, sender: str = "System", type: str = "default"):
        """Génère un message système"""
        if sender is not None:
            text = f"[{sender}] {text}"
        message = pm.ui.Text(
            text=text,
            anchor="center",
            font="segoeuisemibold",
            font_size=48,
            font_color=self.messages_types.get(type, self.messages_types["default"]),
            shadow=True,
            auto=False,
        )
        pm.ui.sys_message(message)

# ======================================== EXPORTS ========================================
__all__ = ["Engine"]