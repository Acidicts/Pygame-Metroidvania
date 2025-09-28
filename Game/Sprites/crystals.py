from Game.utils.utils import *
from Game.Sprites.sprite import PhysicsSprite
import random

class Crystal(PhysicsSprite):
    def __init__(self, position, value, game=None):
        self.size = (16, 16)
        self.original_image = load_image("miscellaneous/crystal.png", size=self.size)
        self.image = self.original_image.copy()

        super().__init__(self.image, position)

        self.position = position
        self.value = value

        self.game = game
        self.tilemap = None

        self.gravity = 0.8
        self.friction = -0.1

        max_distance = 96

        self.vel.x = random.uniform(-4, 4)

        self.vel.y = random.uniform(-6, -3)

        self.rotation_angle = 0

    def draw(self, screen, offset=(0, 0)):
        screen.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))

    def update(self, dt):
        super().update(dt)

        if not self.collisions["bottom"] and abs(self.vel.y) > 0.1:
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        
        if self.rect.colliderect(self.game.player.rect):
            self.game.player.crystals += self.value
            # Remove from the tilemap's crystals group
            if self.tilemap:
                self.tilemap.crystals.remove(self)
            return True