import json
import pygame
from pygame.transform import scale

from Game.Sprites.player import Player

from Game.utils.camera import Camera
from Game.utils.config import get_config
from Game.utils.utils import *
from Game.utils.spritegroup import SpriteGroup
from Game.utils.tilemaps import TileMap


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(tuple(get_config()["resolution"]))
        pygame.display.set_caption("Metroidvania Game")
        self.running = True

        self.camera = Camera(*get_config()["resolution"])
        self.tilemap = TileMap(self, tile_size=48)
        self.sprite_group = SpriteGroup()

        # Load assets after pygame display is initialized
        self.assets = {}
        self.setup()

        self.player = Player(pos=(get_config()["resolution"][0]/2, get_config()["resolution"][1]/2), game=self, tilemap=self.tilemap)
        self.num = 0

        self.tilemap.load_map("Game/assets/level/test.json")

    def setup(self):
        self.assets = {"cave":
            {"big_rocks": SpriteSheet("cave_tiles/Cave - BigRocks1.png", cut=load_json_as_dict("cut_tiles_json/Cave-BigRocks1.json")),
             "floor": SpriteSheet("cave_tiles/Cave - Floor.png", cut=load_json_as_dict("cut_tiles_json/Cave-Floor.json")),
             "platform": SpriteSheet("cave_tiles/Cave - Platforms.png", cut=load_json_as_dict("cut_tiles_json/Cave-Platforms.json")),
             }
        }

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.player.draw(self.screen)

        self.sprite_group.draw(self.screen, self.camera.offset)

        self.tilemap.render(self.screen, (0, 0), 5)

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