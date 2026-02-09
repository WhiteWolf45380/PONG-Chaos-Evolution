# ======================================== IMPORTS ========================================
import sys

# ======================================== GESTIONNAIRE ========================================
class ContextManager:
    """
    Context Manager
    """
    def __init__(self):
        pass

    def __getattr__(self, name):
        raise AttributeError(f"context has no attribute {name!r}")

# ======================================== CLASSE MODULAIRE ========================================
sys.modules[__name__] = ContextManager()