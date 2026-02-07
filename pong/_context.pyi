# ======================================== IMPORTS ========================================
from typing import Optional
from ._game import Game
from ._menus import Main, Modes, Modifiers, Settings, Lobbies

# ======================================== EXPOSITIONS ========================================
game: Optional[Game]
main: Optional[Main]
modes: Optional[Modes]
modifiers: Optional[Modifiers]
settings: Optional[Settings]
lobbies: Optional[Lobbies]