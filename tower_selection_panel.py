import pygame
import os

from towers.archer_tower import ArcherTower
from towers.fire_tower import FireTower

class TowerSelectionPanel:
    def __init__(self, screen_width, screen_height):
        """
        Dynamically create a bottom-center panel. 
        It sizes itself based on how many tower types we have.
        """

        # Tower data list: we store everything we need in each dict
        # - name:  to display on panel
        # - price: tower's cost
        # - icon:  tower icon image
        # - cls:   actual Tower class (e.g., ArcherTower)
        self.tower_data = [
            {
                "name": "Archer",
                "price": 50,
                "icon_path": os.path.join("assets/archer-tower-game-assets/PNG", "10.png"),
                "cls": ArcherTower
            },
            {
                "name": "Fire",
                "price": 50,
                "icon_path": "assets/magic-tower-game-assets/PNG/3.png",
                "cls": FireTower
            },
            # Add more towers here if desired
        ]

        # -- LOAD and SCALE icons; store them back to tower_data
        #   so we only do the scaling once:
        # For demonstration, we'll just load them from "icon_path".
        for t in self.tower_data:
            if not os.path.exists(t["icon_path"]):
                raise FileNotFoundError(f"Missing icon: {t['icon_path']}")
            # Load
            icon = pygame.image.load(t["icon_path"]).convert_alpha()
            t["icon"] = icon

        # Scale factor to make the panel 1.5 times larger than the old ~100×300
        self.scale_factor = 1.5

        # Icon size
        self.icon_size = int(64 * self.scale_factor)

        # Font for tower name/price
        # Adjust size as you wish
        self.font = pygame.font.SysFont(None, int(20 * self.scale_factor))

        # Panel padding around edges
        self.panel_padding = int(10 * self.scale_factor)

        # Spacing between icons
        self.icon_spacing = int(10 * self.scale_factor)

        # We'll create a scaled icon for each tower
        for t in self.tower_data:
            t["scaled_icon"] = pygame.transform.scale(t["icon"], (self.icon_size, self.icon_size))

        self.num_towers = len(self.tower_data)

        # Calculate panel width: each tower = (icon_size + spacing), plus side padding
        self.width = (self.num_towers * (self.icon_size + self.icon_spacing)) + self.panel_padding
        # Make sure we have final spacing accounted for:
        # e.g., if you want the same spacing on the right side, add self.icon_spacing

        # Panel height: let's give enough room for icon + text
        # Original was ~100; we do 1.5× => 150, 
        # but also ensure there's space for the tower name/price
        # We'll do ~150 or so:
        self.height = int(100 * self.scale_factor)

        # Position the panel in the bottom-center:
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height

        # Create rects for each tower icon
        self.icon_rects = []
        current_x = self.x + self.panel_padding
        current_y = self.y + self.panel_padding
        for t in self.tower_data:
            rect = t["scaled_icon"].get_rect(topleft=(current_x, current_y))
            self.icon_rects.append({
                "rect": rect,
                "tower_info": t
            })
            current_x += self.icon_size + self.icon_spacing

        self.selected_tower = None

    def draw(self, surface):
        # Draw panel background
        pygame.draw.rect(
            surface, 
            (60, 60, 60), 
            (self.x, self.y, self.width, self.height)
        )
        # Optional border
        pygame.draw.rect(
            surface, 
            (0, 0, 0), 
            (self.x, self.y, self.width, self.height), 
            2
        )

        # Draw each icon + text
        for icon_data in self.icon_rects:
            rect = icon_data["rect"]
            tower_info = icon_data["tower_info"]

            # Draw the icon
            surface.blit(tower_info["scaled_icon"], (rect.x, rect.y))

            # Name + price
            text_str = f"{tower_info['name']} ({tower_info['price']})"
            text_surf = self.font.render(text_str, True, (255, 255, 255))

            # Position it below the icon
            text_x = rect.centerx - text_surf.get_width() // 2
            text_y = rect.bottom + 2
            surface.blit(text_surf, (text_x, text_y))

    def handle_event(self, event):
        """
        Return (panel_handled, tower_cls, tower_price).
        - panel_handled: True if the click was inside the panel area.
        - tower_cls: The class of the selected tower if an icon was clicked, else None.
        - tower_price: The price of that tower if an icon was clicked, else None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # left-click
            mx, my = event.pos
            # Check if click is anywhere in the panel
            if (self.x <= mx <= self.x + self.width) and (self.y <= my <= self.y + self.height):
                # It's inside the panel area. Let's see if it hits an icon
                for icon_data in self.icon_rects:
                    rect = icon_data["rect"]
                    if rect.collidepoint(mx, my):
                        tower_info = icon_data["tower_info"]
                        self.selected_tower = tower_info["cls"]
                        price = tower_info["price"]
                        return (True, self.selected_tower, price)
                # If we clicked the panel but not an icon
                return (True, None, None)
        return (False, None, None)