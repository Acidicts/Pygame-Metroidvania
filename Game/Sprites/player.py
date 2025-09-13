import pygame
from Game.Sprites.sprite import Sprite

class Player(Sprite):
    def __init__(self, img=pygame.surface.Surface((16, 16)), pos=(0, 0), id=None, game=None, tilemap=None):
        super().__init__(img, pos, id)
        self.speed = 400
        self.velocity = pygame.math.Vector2(0, 0)

        self.tilemap = tilemap
        self.game = game

        self.animations = {}
        self.animation = "idle"

        self.attributes = {
            "max_jumps": 1,
            "jumps": 1,
            "falling": False,
            "damaged": False,
            "attacking": False,
            "cutscene": False
        }

    def controls(self):
        keys = pygame.key.get_pressed()
        self.velocity = pygame.math.Vector2(0, 1)

        self.velocity.x += int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])

        if keys[pygame.K_SPACE] and self.attributes["jumps"] >= 1:
            self.velocity.y = -10
            self.attributes["jumps"] -= 1

    def update(self, dt):
        self.controls()

        self.rect.x += self.velocity.x * dt * self.speed
        self.rect.y += self.velocity.y * dt * self.speed

    def collision(self):
        self.tilemap.collision()

    def draw(self, surf):
        surf.blit(self.image, self.rect)
