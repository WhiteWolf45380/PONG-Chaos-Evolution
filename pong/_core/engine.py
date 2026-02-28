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

        # Méthodes à appelé lors de l'arrêt du programme
        self.finals = []

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

        # Seconde initialisation
        self.main.init()

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
        
        # Chargement des sons et musics
        self.load_sounds()
        self.load_musics()
        pm.audio.play_music("menus", loop=True, fade_ms=1500)
        pm.inputs.add_listener(pm.inputs.MOUSELEFT, callback=lambda: pm.audio.play_sound("click"))
        
        # Démarrage dans le menu principal
        pm.states.activate("main_menu", transition=True, ease_out=False, duration=1.5)

    # ======================================== DEMARRAGE INITIAL ========================================
    def run(self):
        """Lance l'éxécution"""
        pm.run(self.update, final=self.final)

    def load_sounds(self):
        """Charge les sons"""
        pm.audio.create_group(
            "ui",
            channels=3,
            volume=1.0
        )
        
        pm.audio.add_sound(
            "click",
            get_path("_assets/sounds/click.mp3"),
            volume=0.2,
            group="ui"
        )

        pm.audio.add_sound(
            "select",
            get_path("_assets/sounds/select.mp3"),
            volume=0.5,
            cooldown=0.5,
            group="ui"
        )

        pm.audio.create_group(
            "entities",
            channels=5,
            volume=1.0,
        )

        pm.audio.add_sound(
            "bounce",
            get_path("_assets/sounds/bounce.mp3"),
            volume=0.55,
            group="entities",
        )
        
        pm.audio.add_sound(
            "goal",
            get_path("_assets/sounds/goal.mp3"),
            volume=2.0,
            cooldown=1.0,
            group="entities"
        )
    
    def load_musics(self):
        """Charge les musiques"""
        pm.audio.add_music(
            "menus",
            get_path("_assets/musics/menus.mp3"),
            volume=0.4,
        )

        pm.audio.add_music(
            "game",
            get_path("_assets/musics/game.mp3"),
            volume=0.25,
        )

    # ======================================== ACTUALISATION FONDAMENTALE ========================================
    def update(self):
        """Actualisation de la frame"""
        pm.screen.fill((30, 30, 47))
        if not pm.states.get_active_states():
            pm.stop()

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
    
    # ======================================== FIN D'EXECUTION ========================================
    def add_final(self, func: callable, priority: int = 0):
        """Ajoute une méthode à la liste de fin d'éxéction"""
        self.finals.insert(priority, func)

    def final(self):
        """Méthode appelée lors de l'arrêt du programme"""
        for final_func in self.finals:
            final_func()

# ======================================== EXPORTS ========================================
__all__ = ["Engine"]