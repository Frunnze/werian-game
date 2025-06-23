class GameObject:
    def __init__(self, x, y, width, height, sprite=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = sprite

    def set_sprite(self, sprite):
        self.sprite = sprite

    def draw(self, window):
        if self.sprite:
            window.blit(self.sprite, (self.x, self.y))