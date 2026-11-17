"""
Instructa-Gotchi Display Navigation Controller (Stitch UI Aligned)
Renders the top status bar and bottom 4-tab touch navigation bar:
[Home, Care, Modes, More] matching the Stitch UNIHIKER M10 layout.
"""
from typing import Dict, Any, Callable
from config.settings import DISPLAY_WIDTH, DISPLAY_HEIGHT, ASSETS_DIR
import time

NAV_TABS = [
    {"id": "home", "label": "Home", "icon": "mode_auto"},
    {"id": "care", "label": "Care", "icon": "care_hunger"},
    {"id": "modes", "label": "Modes", "icon": "mode_workshop"},
    {"id": "settings", "label": "More", "icon": "care_energy"}
]

class NavigationController:
    def __init__(self, on_navigate: Callable[[str], None]):
        self.active_tab = "home"
        self.on_navigate = on_navigate

    def switch_tab(self, tab_id: str):
        """Switches active tab and triggers screen change."""
        self.active_tab = tab_id
        self.on_navigate(tab_id)

    def render_top_bar(self, renderer, state: Dict[str, Any]):
        """Renders Stitch-styled compact top status bar (10:24 TINKO | MODE | WIFI)."""
        # Graphite status bar
        renderer.draw_rect(0, 0, DISPLAY_WIDTH, 24, fill="#1C1D1F")

        # Time & Name
        time_str = time.strftime("%H:%M")
        name = state.get("name", "TINKO").upper()
        renderer.draw_text(6, 6, f"{time_str} {name}", size=9, color="#FFC928")

        # Mode Badge
        mode = state.get("mode", "auto").upper()
        renderer.draw_rect(130, 4, 70, 16, fill="#F28B24", radius=4)
        renderer.draw_text(138, 6, mode[:8], size=9, color="#FFFFFF")

        # Wi-Fi icon indicator
        renderer.draw_text(208, 6, "Wi-Fi", size=8, color="#38BDF8")

    def render_bottom_nav(self, renderer):
        """Renders Stitch-styled bottom navigation bar with 4 touch tabs."""
        y = DISPLAY_HEIGHT - 34
        renderer.draw_rect(0, y, DISPLAY_WIDTH, 34, fill="#1C1D1F")

        tab_width = DISPLAY_WIDTH // len(NAV_TABS)
        for i, tab in enumerate(NAV_TABS):
            tx = i * tab_width
            is_active = (tab["id"] == self.active_tab)

            # Active indicator
            if is_active:
                renderer.draw_rect(tx + 4, y + 2, tab_width - 8, 2, fill="#F28B24", radius=1)

            # Icon
            icon_path = ASSETS_DIR / "icons" / f"{tab['icon']}.png"
            renderer.draw_image(tx + (tab_width - 18) // 2, y + 5, icon_path, width=18, height=18)

            # Label
            label_color = "#F28B24" if is_active else "#879099"
            renderer.draw_text(tx + (tab_width - 24) // 2, y + 24, tab["label"], size=7, color=label_color)

            # Hitbox
            tab_id = tab["id"]
            renderer.register_touch_target(tx, y, tab_width, 34, lambda t=tab_id: self.switch_tab(t))
