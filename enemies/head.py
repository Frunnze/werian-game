import pygame
import os
from .enemy import Enemy

class HeadMonster(Enemy):
    def __init__(self, x, y, cell_width, cell_height, life=125, points=20, speed=3, damage=1):
        super().__init__(x, y, cell_width, cell_height, life, points, speed, damage)

        # Load and scale the image
        original_image = pygame.image.load('assets/monster-character-2d-sprites/PNG/8/2_enemies_1_ATTACK_000.png').convert_alpha()
        scaled_size = (original_image.get_width() // 4, original_image.get_height() // 4)
        self.image = pygame.transform.scale(original_image, scaled_size)
        self.rect = self.image.get_rect(center=(self.x * self.cell_width, self.y * self.cell_height))
        self.width, self.height = self.rect.size  
        self.load_images()
        self.pos = pygame.math.Vector2(self.rect.center)

    def load_images(self):
        self.imgs = []
        self.attack_imgs = []
        for i in range(10):
            path = os.path.join("assets/monster-character-2d-sprites/PNG/8",
                                f"2_enemies_1_RUN_00{i}.png")
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (100, 100))
            self.imgs.append(img)

        for i in range(10):  # Assuming 10 attack frames
            attack_path = os.path.join("assets/monster-character-2d-sprites/PNG/8", f"2_enemies_1_ATTACK_00{i}.png")
            img = pygame.image.load(attack_path).convert_alpha()
            img = pygame.transform.scale(img, (100, 100))
            self.attack_imgs.append(img)