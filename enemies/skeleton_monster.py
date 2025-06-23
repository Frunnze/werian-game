import pygame
import os
from .enemy import Enemy


class SkeletonMonster(Enemy):
    def __init__(self, x, y, cell_width, cell_height, life=3000, points=300, speed=3, damage=1):
        super().__init__(x, y, cell_width, cell_height, life, points, speed, damage)

        # Load and scale the image
        original_image = pygame.image.load('assets/boss-monster-game-sprites/boss_3/PNG/0_boss_attack_000.png').convert_alpha()
        self.scaled_size = (original_image.get_width() // 5, original_image.get_height() // 5)
        self.image = pygame.transform.scale(original_image, self.scaled_size)
        self.rect = self.image.get_rect(center=(self.x * self.cell_width, self.y * self.cell_height))
        self.width, self.height = self.rect.size  
        self.load_images()
        self.pos = pygame.math.Vector2(self.rect.center)

    def load_images(self):
        self.imgs = []
        self.attack_imgs = []
        for i in range(20):
            path = os.path.join("assets/boss-monster-game-sprites/boss_3/PNG/",
                                f"0_boss_run_0{i:02}.png")
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, self.scaled_size)
            self.imgs.append(img)

        for i in range(20):
            attack_path = os.path.join("assets/boss-monster-game-sprites/boss_3/PNG/", f"0_boss_attack_0{i:02}.png")
            img = pygame.image.load(attack_path).convert_alpha()
            img = pygame.transform.scale(img, self.scaled_size)
            self.attack_imgs.append(img)