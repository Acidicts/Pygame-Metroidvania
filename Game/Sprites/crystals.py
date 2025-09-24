import pygame

class Crystal:
    def __init__(self, position, value):
        self.position = position
        self.size = (8, 8)
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(topleft=position)
        self.value = value

    def draw(self, screen, offset):
        screen.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))