import pygame
import math


class MainTower(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, range=300, damage=100, fire_rate=1, sprite=None):
        super().__init__()
        self.life = 1000
        self.max_life = 1000
        self.price = 1000
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.range = range  # How far the tower can attack
        self.damage = damage  # Damage per attack
        self.fire_rate = fire_rate  # Attacks per second
        self.last_shot_time = 0  # Time since the last attack

        # Attack animation attributes
        self.is_attacking = False
        self.attack_imgs = []  # List to hold attack animation frames
        self.attack_animation_index = 0
        self.animation_speed = 100  # Time in milliseconds between frames
        self.last_animation_time = 0  # Time since the last frame change

        # Load and scale the tower image
        tower_image = pygame.image.load("assets/support-tower-game-assets/PNG/5.png")
        self.sprite = pygame.transform.scale(tower_image, (self.width, self.height))  # Set the sprite

        # Create the rectangle for collision and positioning
        self.rect = self.sprite.get_rect()
        self.rect.topleft = (self.x, self.y)

        # Load attack sprites specific to MainTower
        attack_sprite_paths = [
            "assets/magic-tower-game-assets/PNG/19.png",
            "assets/magic-tower-game-assets/PNG/20.png",
            # Add all attack frames
        ]
        self.load_attack_sprites(attack_sprite_paths)

        # Scale attack images if necessary
        self.attack_imgs = [pygame.transform.scale(img, (50, 50)) for img in self.attack_imgs]

        self.upgrade_button_visible = False
        self.upgrade_button_rect = None

    def clicked_for_upgrade(self):
        """
        Checks if the tower is clicked for an upgrade.
        Returns True if the tower is clicked, else False.
        """ 
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(mouse_pos):
                self.upgrade_button_visible = True
                return True
            else:
                self.upgrade_button_visible = False
                return False
        else:
            return self.upgrade_button_visible

    def draw_upgrade_button(self, window):
        """
        Draws the upgrade button on the screen above the tower with a brown background,
        grey contour, and styled 'Upgrade' text.
        """
        # Define the upgrade button rect dimensions
        button_width, button_height = 100, 30
        button_x = self.rect.centerx - button_width // 2
        button_y = self.rect.top - button_height - 5  # Position above the tower
        self.upgrade_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        # Draw the button background (brown)
        pygame.draw.rect(window, (139, 69, 19), self.upgrade_button_rect)  # Brown background
        # Add a border (grey contour)
        pygame.draw.rect(window, (128, 128, 128), self.upgrade_button_rect, 2)  # Grey border
        # Initialize the font and render the text
        try:
            font = pygame.font.Font(None, 24)  # Slightly larger font for better readability
        except pygame.error as e:
            print(f"Font initialization error: {e}")
            return  # Skip drawing if the font fails to load
        # Render the 'Upgrade' text in white with anti-aliasing for smoothness
        text_surface = font.render("Upgrade", True, (255, 255, 255))  # White text
        text_rect = text_surface.get_rect(center=self.upgrade_button_rect.center)
        window.blit(text_surface, text_rect)

    def clicked_plus_rect_upgrade_button(self):
        """
        Checks if the upgrade button is clicked.
        Returns True if the button is clicked, else False.
        """
        if self.upgrade_button_visible and self.upgrade_button_rect:
            mouse_pos = pygame.mouse.get_pos()
            mouse_over = self.upgrade_button_rect.collidepoint(mouse_pos)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    if mouse_over:
                        print("Button clicked!")
                        return True
        return False

    def hide_display_upgrade_button(self):
        """
        Hides the upgrade button by resetting its visibility and rectangle.
        """
        self.upgrade_button_visible = False
        self.upgrade_button_rect = None

    def upgrade(self):
        self.max_life += 1000
        self.life += 1000
        self.damage += 1
        tower_image = pygame.image.load("assets/support-tower-game-assets/PNG/6.png")
        self.sprite = pygame.transform.scale(tower_image, (self.width, self.height))  # Set the sprite

    def load_attack_sprites(self, sprite_paths):
        """Load attack animation sprites."""
        self.attack_imgs = [pygame.image.load(path) for path in sprite_paths]

    def get_coord(self, cell_width, cell_height):
        """Return the column and row based on the tower's position."""
        col = int(self.rect.centerx / cell_width)
        row = int(self.rect.centery / cell_height)
        return (col, row)

    def is_in_range(self, enemy):
        """Check if an enemy is within range."""
        # Calculate center positions
        tower_center_x = self.x + self.width // 2
        tower_center_y = self.y + self.height // 2
        enemy_center_x = enemy.pos.x
        enemy_center_y = enemy.pos.y

        distance = math.hypot(tower_center_x - enemy_center_x, tower_center_y - enemy_center_y)
        return distance <= self.range

    def attack(self, enemies, current_time):
        """Attack an enemy if enough time has passed."""
        # Find enemies in range
        enemies_in_range = [enemy for enemy in enemies if self.is_in_range(enemy)]

        if enemies_in_range:
            # Attack the first enemy in the list (you can change targeting logic)
            target_enemy = enemies_in_range[0]
            if current_time - self.last_shot_time >= 1000 / self.fire_rate:
                target_enemy.take_damage(self.damage)
                self.last_shot_time = current_time
                self.is_attacking = True  # Start attack animation
                self.attack_animation_index = 0  # Reset animation index

    def draw(self, window, current_time=None):
        """Draw the tower and its health bar."""
        # Draw the tower's sprite at the correct position
        window.blit(self.sprite, (self.x, self.y))

        # Draw the health bar
        health_bar_width = self.width
        health_bar_height = 10
        health_bar_x = self.x
        health_bar_y = self.y - health_bar_height - 2  # Position above the tower

        # Calculate health bar fill based on current life
        fill_width = int((self.life / self.max_life) * health_bar_width)

        # Draw the contour (black border) of the health bar
        pygame.draw.rect(window, (0, 0, 0), (health_bar_x - 1, health_bar_y - 1, health_bar_width + 2, health_bar_height + 2))

        # Draw the background (red) and foreground (green) of the health bar
        pygame.draw.rect(window, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(window, (0, 255, 0), (health_bar_x, health_bar_y, fill_width, health_bar_height))



    def take_damage(self, damage):
        self.life -= damage
