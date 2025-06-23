import pygame
import math
import os

class Arrow(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_x, target_y, damage, speed=10):
        super().__init__()
        self.image = pygame.image.load(os.path.join("assets/archer-tower-game-assets/PNG", "37.png"))
        self.image = pygame.transform.scale(self.image, (20, 10))  # Adjust size as needed
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.damage = damage  # Arrow damage
        
        # Calculate trajectory
        angle = math.atan2(target_y - start_y, target_x - start_x)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        
        # Rotate the arrow to face its direction
        self.image = pygame.transform.rotate(self.image, -math.degrees(angle))
        self.target_x = target_x
        self.target_y = target_y

    def update(self, enemies):
        # Move the arrow
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Check for collision with enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage*0.5)  # Apply damage from the arrow
                self.kill()  # Remove the arrow
                break

        # Remove arrow if it goes out of bounds
        if not pygame.display.get_surface().get_rect().contains(self.rect):
            self.kill()

class ArcherTower(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, attack_range=150, damage=25, fire_rate=1):
        super().__init__()
        self.life = 100
        self.x = x
        self.y = y
        self.max_life = 100
        self.price = 50
        self.width = width
        self.height = height
        self.attack_range = attack_range  # How far the tower can attack
        self.damage = damage  # Damage per attack
        self.fire_rate = fire_rate  # Attacks per second
        self.last_shot_time = 0  # Time since the last attack

        # Initialize animation attributes
        self.archer_imgs = []  # List to hold archer animation frames
        self.archer_animation_index = 0
        self.animation_speed = 100  # Time in milliseconds between frames
        self.last_animation_time = 0  # Initialize this attribute here

        # Load archer image for idle state (default)
        self.archer_idle_img = pygame.image.load(os.path.join("assets/archer-tower-game-assets/PNG", "38.png"))
        self.archer_idle_img = pygame.transform.scale(self.archer_idle_img, (int(self.width * 0.2), int(self.height * 0.2)))

        # Target enemy's position for attack animation
        self.enemies_to_attack = []
        self.left = True  # Direction the archer is facing

        # Load and scale the tower base image
        self.tower_base = pygame.image.load(os.path.join("assets/archer-tower-game-assets/PNG", "10.png"))
        self.tower_base = pygame.transform.scale(self.tower_base, (self.width * 0.8, self.height * 0.8))

        # Load archer animation sprites
        for i in range(38, 43):  # Example frame indices
            archer_image = pygame.image.load(os.path.join("assets/archer-tower-game-assets/PNG", f"{i}.png"))
            self.archer_imgs.append(pygame.transform.scale(archer_image, (int(self.width * 0.2), int(self.height * 0.2))))

        # Create the rectangle for collision and positioning
        self.rect = self.tower_base.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.arrows = pygame.sprite.Group()

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
        self.damage += 25
        self.tower_base = pygame.image.load(os.path.join("assets/archer-tower-game-assets/PNG", "12.png"))
        self.tower_base = pygame.transform.scale(self.tower_base, (self.width * 0.8, self.height * 0.8))

    def get_coord(self, cell_width, cell_height):
        col = int(self.rect.centerx / cell_width)
        row = int(self.rect.centery / cell_height)
        return (col, row)

    def enemy_in_range(self, enemy):
        distance = math.sqrt((self.x - enemy.pos.x) ** 2 + (self.y - enemy.pos.y) ** 2)
        return distance <= self.attack_range

    def attack(self, enemies, current_time):
        self.enemies_to_attack = [enemy for enemy in enemies if self.enemy_in_range(enemy)]
        if self.enemies_to_attack:
            enemy = self.enemies_to_attack[0]
            if current_time - self.last_shot_time >= 1000 / self.fire_rate:
                # Pass self.damage when creating the arrow
                arrow = Arrow(self.x + self.width // 2, self.y + self.height // 4, enemy.rect.centerx, enemy.rect.centery, self.damage)
                self.arrows.add(arrow)
                self.last_shot_time = current_time

                # Adjust archer's facing direction
                if enemy.rect.centerx > self.x and not self.left:
                    self.left = True
                    self._flip_archer_imgs()
                elif enemy.rect.centerx < self.x and self.left:
                    self.left = False
                    self._flip_archer_imgs()
                    
    def _flip_archer_imgs(self):
        self.archer_imgs = [pygame.transform.flip(img, True, False) for img in self.archer_imgs]

    def draw(self, window, current_time, enemies):
        # Draw the tower base
        window.blit(self.tower_base, (self.x, self.y))

        # Update and draw archer animation
        if current_time - self.last_animation_time >= self.animation_speed:
            self.archer_animation_index = (self.archer_animation_index + 1) % len(self.archer_imgs)
            self.last_animation_time = current_time
        archer_image = self.archer_imgs[self.archer_animation_index]
        archer_x = self.x + (self.width // 2 - archer_image.get_width() // 2) - 30
        archer_y = self.y + (self.height // 10) - 30
        window.blit(archer_image, (archer_x, archer_y))

        # Update arrows and check collisions with enemies
        self.arrows.update(enemies)
        self.arrows.draw(window)

        # Draw the range circle
        #pygame.draw.circle(window, (0, 255, 0), (int(self.x + self.width // 2), int(self.y + self.height // 2)), self.attack_range, 1)
        
    def take_damage(self, damage):
        self.life -= damage
        if self.life <= 0:
            self.kill()
