import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, img, pos=(0, 0), id=None):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(topleft=pos)
        self.z = 0
        self.id = id

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, surf):
        pygame.blit(surf, self.image, self.rect)

    def update(self, dt):
        pass
