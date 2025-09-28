import pygame
from Game.Sprites.sprite import Sprite

class Item(Sprite):
    def __init__(self, pos, game, tilemap, item):
        img = pygame.surface.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(img, (255, 255, 255, 100), (8, 8), 8)
        pygame.draw.aacircle(img, (255, 255, 255), (8, 8), 6)

        super().__init__(img, pos)
        self.item = item
        self.rect = pygame.Rect(pos[0] + 2, pos[1] + 2, 12, 12)
        self.collected = False

        self.game = game
        self.tilemap = tilemap

    def collect(self):
        if not self.collected:
            if "crystal" in self.item[0].lower():
                self.game.player.crystals += int(self.item[0].split(" ")[1])
            self.collected = True
            self.tilemap.items.remove(self)
            return True

    def update(self, dt):
        if self.rect.colliderect(self.game.player.rect):
            if self.collect():
                return True