# ======================================== IMPORTS ========================================
from ...._core import ctx, pm

# ======================================== PANEL ========================================
class Menu(pm.panels.Panel):
    """
    Panel du menu
    """
    def __init__(self):
        # Initialisation du panel
        super().__init__("modifiers_menu")