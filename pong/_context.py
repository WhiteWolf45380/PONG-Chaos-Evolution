# ======================================== IMPORTS ========================================
import sys

# ======================================== GESTIONNAIRE ========================================
class ContextManager:
    """
    Context Manager
    """
    def __init__(self):
        # Engine
        self.engine = None

        # Jeu
        self.game = None

        # Menus
        self.main = None
        self.modes = None
        self.modifiers = None

    def __getattr__(self, name):
        raise AttributeError(f"context has no attribute {name!r}")

# ======================================== CLASSE MODULAIRE ========================================
sys.modules[__name__] = ContextManager()