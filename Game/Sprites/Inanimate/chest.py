import pygame

from Game.Sprites.sprite import Sprite
from Game.Sprites.Inanimate.item import Item

class Chest(Sprite):
    def __init__(self, pos, game, tilemap, contains=None):
        self.image_closed = pygame.surface.Surface((32, 32))
        self.image_closed.fill((139,69,19))
        self.image_opened = pygame.surface.Surface((32, 32))
        self.image_opened.fill((150,75,0))

        super().__init__(self.image_closed, pos)

        self.game = game
        self.tilemap = tilemap

        self.contains = contains
        self.image = self.image_closed

        self.rect = self.image.get_rect()
        self.rect.topright = pos
        self.opened = False

    def open(self):
        if not self.opened:
            self.opened = True
            self.image = self.image_opened
            for item in self.contains:
                self.tilemap.items.append(Item(self.rect.center + pygame.Vector2((0, -32)), self.game, self.tilemap, [item]))

    def update(self, dt):
        if self.rect.colliderect(self.game.player.rect):
            self.open()