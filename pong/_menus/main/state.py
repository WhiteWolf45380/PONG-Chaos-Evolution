# ======================================== IMPORTS ========================================
from ..._core import pm

# ======================================== ETAT ========================================
class Main(pm.states.State):
    """
    Menu principal
    """
    def __init__(self):
        super().__init__('main_menu')
    
    def update(self):
        """Actualisation par frame"""