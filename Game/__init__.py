import json
import pygame
from pygame.transform import scale

from Game.Sprites.player import Player

from Game.utils.utils import *
from Game.utils.spritegroup import SpriteGroup
from Game.utils.tilemaps import TileMap


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Metroidvania Game")
        self.running = True

        self.assets = {}
        self.setup()

        self.tilemap = TileMap(self)
        self.sprite_group = SpriteGroup()
        self.player = Player(pos=(100, 100), game=self, tilemap=self.tilemap)
        self.num = 0

    def setup(self):
        self.assets = {"cave":
            {"big_rocks": SpriteSheet("cave_tiles/Cave - BigRocks1.png", cut=load_json_as_dict("cut_tiles_json/Cave-BigRocks1.json")),
             "floor": SpriteSheet("cave_tiles/Cave - Floor.png", cut=load_json_as_dict("cut_tiles_json/Cave-Floor.json")),
             }
        }

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.player.draw(self.screen)

        rect = self.assets["cave"]["big_rocks"].get_debug_image().get_rect()
        self.screen.blit(pygame.transform.scale(self.assets["cave"]["big_rocks"].get_debug_image(), (rect.width//4, rect.height//4)), (0, 0))
        pygame.display.flip()

    def update(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.sprite_group.update(dt)
        self.player.update(dt)

    def run(self):
        while self.running:
            dt = pygame.time.Clock().tick(60) / 1000

            self.draw()
            self.update(dt)