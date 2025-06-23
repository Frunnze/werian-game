import pygame

class SpriteHandler:
    @staticmethod
    def load_sprite(path, width, height):
        """Load and scale a sprite from a file."""
        sprite = pygame.image.load(path)
        return pygame.transform.scale(sprite, (width, height))
    
    @staticmethod
    def load_sprites(paths, width, height):
        """Load multiple sprites, e.g., for animations."""
        return [SpriteHandler.load_sprite(path, width, height) for path in paths]
