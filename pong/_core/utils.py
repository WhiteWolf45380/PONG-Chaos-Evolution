# ======================================== IMPORTS ========================================
from .imports import *
import sys

# ======================================== METHODES GLOBALES ========================================
def get_path(relative_path: str | Path) -> str:
    """Obtention du chemin absolu d'un fichier"""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS) / "pong"
    else:
        base_path = Path(__file__).resolve().parent.parent
    return str(base_path / relative_path)

# ======================================== EXPORTS ========================================
__all__ = [
    "get_path",
]