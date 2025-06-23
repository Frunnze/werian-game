import pygame
import math


class FireTower(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, attack_range=1000, damage=1, fire_rate=1, sprite=None):
        super().__init__()
        self.life = 100
        self.max_life = 100
        self.price = 50
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.attack_range = attack_range  # How far the tower can attack
        self.damage = damage  # Damage per attack
        self.fire_rate = fire_rate  # Attacks per second
        self.last_shot_time = 0  # Time since the last attack

        # Attack animation attributes
        self.attack_imgs = []  # List to hold attack animation frames
        self.attack_animation_index = 0
        self.animation_speed = 100  # Time in milliseconds between frames
        self.last_animation_time = 0  # Time since the last frame change

        # Target enemy's position for attack animation
        self.enemies_to_attack = []
        self.enemy_positions = {}

        # Load and scale the tower image
        tower_image = pygame.image.load("assets/magic-tower-game-assets/PNG/3.png")
        self.sprite = pygame.transform.scale(tower_image, (self.width, self.height))

        # Create the rectangle for collision and positioning
        self.rect = self.sprite.get_rect()
        self.rect.topleft = (self.x, self.y)

        # Load attack sprites specific to MainTower
        attack_sprite_paths = []
        for i in range(0, 19):
            attack_sprite_paths.append(
                f"assets/magic-effects-game-sprite/PNG/fire/1_effect_fire_0{i:02}.png"
            )
        self.attack_imgs = [pygame.image.load(path) for path in attack_sprite_paths]

        # Scale down the fire animation frames to make them smaller
        self.attack_imgs = [pygame.transform.scale(img, (int(img.get_width() // 10), int(img.get_height() // 10))) for img in self.attack_imgs]

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
        self.life += self.max_life
        print(self.life, "self.life")
        self.damage += 1
        tower_image = pygame.image.load("assets/magic-tower-game-assets/PNG/4.png")
        self.sprite = pygame.transform.scale(tower_image, (self.width, self.height))

    def get_coord(self, cell_width, cell_height):
        col = int(self.rect.centerx / cell_width)
        row = int(self.rect.centery / cell_height)
        return (col, row)
    
    def enemy_in_range(self, enemy):
        distance = math.sqrt((self.x - enemy.pos.x) ** 2 + (self.y - enemy.pos.y) ** 2)
        return distance <= self.attack_range

    def attack(self, enemies, current_time):
        # Determine which enemies to attack
        self.enemies_to_attack = []
        for enemy in enemies:
            if self.enemy_in_range(enemy):
                self.enemies_to_attack.append(enemy)
        
        # Attack the enemies
        for enemy in self.enemies_to_attack:
            if enemy.id in self.enemy_positions:
                if (enemy.pos.x - enemy.pos.x * 0.1 <= self.enemy_positions[enemy.id][0] <= enemy.pos.x + enemy.pos.x * 0.1) or \
                    (enemy.pos.y - enemy.pos.y * 0.1 <= self.enemy_positions[enemy.id][1] <= enemy.pos.y + enemy.pos.y * 0.1):
                    enemy.take_damage(self.damage)

    def throw_fireball(self, enemy, window, current_time):
        if current_time - self.last_animation_time >= self.animation_speed:
            self.attack_animation_index = (self.attack_animation_index + 1) % len(self.attack_imgs)
            self.last_animation_time = current_time

        if enemy.id not in self.enemy_positions:
            self.enemy_positions[enemy.id] = (enemy.pos.x, enemy.pos.y)
        else:
            if self.attack_animation_index == 18:
                self.enemy_positions[enemy.id] = (enemy.pos.x, enemy.pos.y)

        fireball_image = self.attack_imgs[self.attack_animation_index]
        x = self.enemy_positions[enemy.id][0]
        y = self.enemy_positions[enemy.id][1] - self.attack_imgs[0].get_height()

        window.blit(fireball_image, (x, y))

        # dot_color = (255, 0, 0)  # Red color for the dot
        # dot_radius = 5  # Radius of the dot
        # pygame.draw.circle(window, dot_color, (x, y), dot_radius)


    def draw(self, window, current_time=None):
        for enemy in self.enemies_to_attack:
            self.throw_fireball(enemy, window, current_time)

        window.blit(self.sprite, (self.x, self.y))

        # Draw the range circle centered on the tower
        # pygame.draw.circle(window, (255, 0, 0),
        #                     (int(self.x + self.width // 2), int(self.y + self.height // 2)),
        #                     self.attack_range, 1)

    def take_damage(self, damage):
        self.life -= damage