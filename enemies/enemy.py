import pygame
import os
import uuid


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, cell_width, cell_height, life=100, points=10, speed=2, damage=0.5):
        # basic
        super().__init__()
        self.life = life
        self.points = points
        self.id = uuid.uuid4()
        self.damage=damage

        # path
        self.path = []
        self.collision_rects = []

        self.x = x
        self.y = y
        self.path_pos = 0
        self.cell_width = cell_width
        self.cell_height = cell_height

        # movement 
        self.speed = speed
        self.direction = pygame.math.Vector2(0,0)
        self.animation_count = 0
        self.nearest_target = None

    def load_images(self):
        pass

    def play_attack_animation(self):
            """
            Play the attack animation.
            """
            self.animation_count += 1
            if self.animation_count >= len(self.attack_imgs):
                self.animation_count = 0
                self.is_attacking = False

            self.image = self.attack_imgs[self.animation_count]

    def get_coord(self, cell_width, cell_height):
        col = int(self.rect.centerx / cell_width)
        row = int(self.rect.centery / cell_height)
        return (col, row)

    def move_towards(self, path=[]):
        """
        Move the enemy along the given path.
        :param path: List of points (pygame.math.Vector2) representing the path.
        :return: None
        """
        self.path = path if path else self.path

        self.animation_count += 1
        if self.animation_count >= len(self.imgs):
            self.animation_count = 0

        if not self.path: return
        if self.path_pos >= len(self.path):
            if self.nearest_target:
                self.attack()
                self.play_attack_animation()
            return
        
        target = pygame.math.Vector2(self.path[self.path_pos].x * self.cell_width, self.path[self.path_pos].y * self.cell_height)
        current = pygame.math.Vector2(self.pos)
        
        # Calculate direction to the target
        direction = target - current
        distance = direction.length()  # Distance to the target

        if distance == 0:
            self.path_pos += 1  # Move to the next point
            if self.path_pos < len(self.path):
                target = pygame.math.Vector2(self.path[self.path_pos].x * self.cell_width, self.path[self.path_pos].y * self.cell_height)
                direction = target - current
            else:
                return  # Reached the end of the path

        # Normalize the direction vector and move
        direction = direction.normalize()
        self.pos += direction * self.speed

        # Flip the image based on direction
        if direction.x < 0:  # Moving left
            self.image = pygame.transform.flip(self.imgs[self.animation_count], True, False)
        elif direction.x > 0:  # Moving right
            self.image = pygame.transform.flip(self.imgs[self.animation_count], False, False)

        # Update the enemy's position
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Check if close enough to the target to move to the next point
        if distance <= self.speed:
            self.path_pos += 1

    def attack(self):
        self.nearest_target.take_damage(self.damage)

    def draw(self, win):
        win.blit(self.image, self.rect.topleft)

    def take_damage(self, damage):
        self.life -= damage