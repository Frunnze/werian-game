# tower.py
import pygame
from game_object.gameObject import GameObject
import math


class Tower(GameObject):
    def __init__(self, x, y, width, height, range, damage, fire_rate, sprite=None):
        super().__init__(x, y, width, height, sprite)
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

        # Target enemy's position for attack animation
        self.target_enemy_pos = None

    def load_attack_sprites(self, sprite_paths):
        """Load attack animation sprites."""
        self.attack_imgs = [pygame.image.load(path) for path in sprite_paths]

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

                # Store target enemy's center position
                self.target_enemy_pos = (
                    int(target_enemy.x + target_enemy.width / 2),
                    int(target_enemy.y + target_enemy.height / 2)
                )

    def draw(self, window):
        """Draw the tower and its range."""
        # Draw the tower's default sprite
        super().draw(window)

        # Draw the range circle centered on the tower
        pygame.draw.circle(window, (255, 0, 0),
                        (int(self.x + self.width // 2), int(self.y + self.height // 2)),
                        self.range, 1)

        # If attacking, draw attack animation at the target enemy's position
        if self.is_attacking and self.attack_imgs and self.target_enemy_pos:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_animation_time >= self.animation_speed:
                self.last_animation_time = current_time
                self.attack_animation_index += 1
                if self.attack_animation_index >= len(self.attack_imgs):
                    self.attack_animation_index = 0
                    self.is_attacking = False  # End attack animation
                    self.target_enemy_pos = None  # Clear target enemy position

            # Only proceed if target_enemy_pos is still valid
            if self.target_enemy_pos is not None:
                attack_img = self.attack_imgs[self.attack_animation_index]
                # Center the attack image on the enemy's position (cast to integers)
                attack_img_rect = attack_img.get_rect(center=(
                    int(self.target_enemy_pos[0]),
                    int(self.target_enemy_pos[1])
                ))
                window.blit(attack_img, attack_img_rect)