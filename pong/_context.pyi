# ======================================== IMPORTS ========================================
from typing import Optional
from ._core.engine import Engine
from ._game import Game
from ._menus import Main, Modes, Modifiers, Settings, Lobbies
from ._animations import Waiting

# ======================================== EXPOSITIONS ========================================
engine: Optional[Engine]
game: Optional[Game]
main: Optional[Main]
modes: Optional[Modes]
modifiers: Optional[Modifiers]
settings: Optional[Settings]
lobbies: Optional[Lobbies]
waiting: Optional[Waiting]