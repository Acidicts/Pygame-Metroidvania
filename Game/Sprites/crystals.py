from Game.utils.utils import *
from Game.Sprites.sprite import PhysicsSprite

class Crystal(PhysicsSprite):
    def __init__(self, position, value, game=None):
        self.size = (16, 16)
        self.original_image = load_image("miscellaneous/crystal.png", size=self.size)
        self.image = self.original_image.copy()

        super().__init__(self.image, position)

        self.position = position
        self.value = value

        self.game = game

        self.gravity = 0.8
        self.friction = -0.1

        self.vel.y = 0.1

        self.rotation_angle = 0

    def draw(self, screen, offset=(0, 0)):
        screen.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))

    def update(self, dt):
        super().update(dt)

        if not self.collisions["bottom"] and abs(self.vel.y) > 0.1:
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
