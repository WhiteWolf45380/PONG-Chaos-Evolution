# ======================================== IMPORTS ========================================
from ...._core import ctx, pm, pygame

# ======================================== PANEL ========================================
class LobbiesMenuRooms(pm.panels.Panel):
    """
    Panel de la liste des salons du menu des lobbies
    """
    def __init__(self, width : int = 1080, height : int = 700):
        super().__init__('lobbies_menu_rooms', predecessor='lobbies_menu_view', rect=(0, 0, width, height), centered=True, border_width=2, border_color=(30, 40, 50), border_around=True)

        # Fond
        self.background_color = (45, 50, 55)

        # Bouton précédent
        self.previous_button = pm.ui.RectButton(
            x=self.width * 0.48,
            y=self.height * 0.98,
            width=200,
            height=50,
            anchor="bottomright",
            filling=True,
            filling_color=(255, 255, 255, 10),
            filling_hover=True,
            filling_color_hover=(255, 255, 255, 20),
            text=pm.languages("lobbies_previous"),
            font_color=(230, 230, 230),
            font_color_hover=(255, 255, 255),
            font_size_ratio_limit=0.85,
            underline=True,
            border_radius=10,
            hover_scale_ratio=0.97,
            hover_scale_duration=0.05,
            callback=self.handle_previous,
            panel=str(self),
        )

        # Bouton suivant
        self.next_button = pm.ui.RectButton(
            x=self.width * 0.52,
            y=self.height * 0.98,
            width=200,
            height=50,
            anchor="bottomleft",
            filling=True,
            filling_color=(255, 255, 255, 10),
            filling_hover=True,
            filling_color_hover=(255, 255, 255, 20),
            text=pm.languages("lobbies_next"),
            font_color=(230, 230, 230),
            font_color_hover=(255, 255, 255),
            font_size_ratio_limit=0.85,
            underline=True,
            border_radius=10,
            hover_scale_ratio=0.97,
            hover_scale_duration=0.05,
            callback=self.handle_next,
            panel=str(self),
        )

        # Affichage du nombre de pages
        self.pages_count_text = pm.ui.Text(
            x=self.width * 0.98,
            y=self.height * 0.98,
            text=f"0/0",
            anchor="bottomright",
            font_size=48,
            font_color=(255, 255, 255),
            shadow=True,
            shadow_offset=1,
            panel=str(self),
        )

        # Liste des salons
        self.all = {}   # {"ip": (**kwargs, selector)}
        self.sorted_ips = []

        self.rows = 4
        self.rows_margin = 30
        self.rows_space = 50

        self.cols = 2
        self.cols_margin = 50
        self.cols_space = 150

        self.rooms_width = (self.width - 2 * self.cols_margin - (self.cols - 1) * self.cols_space) / self.cols
        self.rooms_height = (self.next_button.rect.y - 2 * self.rows_space - (self.rows - 1) * self.rows_space) / self.rows

        self.current_page = 0
        self.current_hovered = None
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation du panel"""

    def _update_count(self):
        """Actualise le compteur de pages"""
        total = len(self.all)
        self.pages_count_text.text = f"{int(self.current_page + (1 if total > 0 else 0))}/{int(total / (self.cols * self.rows) + (1 if total > 0 else 0))}"

    # ======================================== FOND ========================================
    def draw_back(self, surface: pygame.Surface):
        """Dessin par frame"""
        surface.fill(self.background_color)
    
    # ======================================== HANDLERS ========================================
    def handle_previous(self):
        """Affichage des salons précédents"""
        self.current_page = max(0, self.current_page - 1)
        self.filter()

    def handle_next(self):
        """Affichage des salons suivants"""
        self.current_page = min(int(len(self.all) // (self.cols * self.rows)), self.current_page + 1)
        self.filter()
    
    def handle_join(self):
        """Rejoint un lobby"""
        ip = pm.ui.get_selected("lobby")
        if not pm.network.join(ip):
            error = pm.network.get_last_error()
            print(f"Échec de connexion: {error}")
            pm.states.activate("lobbies_menu", transition=True, duration=0.5)
            ctx.engine.sys_message(pm.languages("error_connection"), sender="Network", type="error") 
            return
        ctx.modifiers.set("p1_side", 1 - self.all[ip][0].get("host_side", 0))
        ctx.game.set_mode(self.all[ip][0].get("mode"))
        pm.states.activate("waiting_animation", transition=False)
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def load(self, rooms: dict):
        """Charge un ensemble de salons"""
        if isinstance(rooms, list): rooms = dict(rooms)
        self.clear(rooms=rooms)
        for ip, lobby in rooms.items():
            if ip not in self.all:
                self.all[ip] = [lobby, None]
        self.sort()
        self.render()

    def clear(self, rooms: dict = None):
        """Nettoie les anciens salons"""
        if rooms is None: rooms = {}
        to_discard = []

        # Tri des salons à nettoyer
        for ip, (lobby, selector) in self.all.items():
            if ip not in rooms or lobby != rooms[ip]:
                to_discard.append((ip, selector))
        
        # Nettoyage
        for ip, selector in to_discard:
            selector.kill()
            del selector
            self.all.pop(ip)
    
    def sort(self):
        """Tri les salons selon leur ancienneté"""
        self.sorted_ips = sorted(self.all.keys(), key=lambda k: self.all[k][0].get("time"))

    def render(self):
        """Génère les salons"""
        for i, ip in enumerate(self.sorted_ips):
            selector = self.all[ip][1]
            if selector is None:
                content = self.all[ip][0]
                selector = pm.ui.RectSelector(
                    x=self.cols_margin + (i // self.rows) * (self.rooms_width + self.cols_space),
                    y=self.rows_margin + (i % self.rows),
                    width=self.rooms_width,
                    height=self.rooms_height,

                    filling_color=(0, 0, 0, 100),
                    filling_color_hover=(0, 0, 0, 150),

                    title=content["name"],
                    title_anchor="topleft",
                    title_size_ratio=0.9,

                    text=content["mode"],
                    text_anchor="left",
                    text_size_ratio=0.9,

                    description=ip,
                    description_anchor="bottomright",
                    description_size_ratio=0.8,

                    font_color=(255, 255, 255),
                    padding=10,

                    border_radius=8,
                    border_width=2,
                    border_color=(0, 0, 0, 10),

                    selection_id="lobby",
                    selector_id=ip,
        
                    callback=self.handle_join,
                    panel=str(self),
                )
                self.all[ip][1] = selector
        self._update_count()
    
    def filter(self):
        """Filtre les salons visibles"""
        rooms_per_page = self.cols * self.rows
        visibles = range(self.current_page * rooms_per_page, (self.current_page + 1) * rooms_per_page - 1)
        for i, ip in enumerate(self.sorted_ips):
            if self.all[ip][1] is None: continue
            if i in visibles:
               self.all[ip][1].visible = True
            else:
               self.all[ip][1].visible = False