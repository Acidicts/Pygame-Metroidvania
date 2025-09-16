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

        self.sprite_group = SpriteGroup()

        self.tilemaps = {}

        self.assets = {}
        self.setup()

        self.tilemap_current = "cave"
        self.tilemap = self.tilemaps[self.tilemap_current]

        self.player = Player(pos=(get_config()["resolution"][0]/2, get_config()["resolution"][1]/2), game=self, tilemap=self.tilemap)
        self.num = 0

    def setup(self):
        self.assets = {
            "cave":
                {
                    "big_rocks": SpriteSheet("cave_tiles/Cave - BigRocks1.png", cut=load_json_as_dict("cut_tiles_json/Cave-BigRocks1.json")),
                    "floor": SpriteSheet("cave_tiles/Cave - Floor.png", cut=load_json_as_dict("cut_tiles_json/Cave-Floor.json")),
                    "platform": SpriteSheet("cave_tiles/Cave - Platforms.png", cut=load_json_as_dict("cut_tiles_json/Cave-Platforms.json")),
                },
           "mossy":
               {
                   "platform": SpriteSheet("mossy_tiles/Mossy - FloatingPlatforms.png", tile_size=512),
               }
        }

        self.tilemaps["cave"] = TileMap(self, tile_size=48, pos=(0, 0), rendered=True)
        self.tilemaps["mossy"] = TileMap(self, tile_size=48, pos=(18, 0), rendered=False)

        maps = get_config()["tilemaps"]

        for name, tilemaps in self.tilemaps.items():
            tilemaps.load_map(maps[name])

    def draw(self):
        self.screen.fill("#000F17")
        self.player.draw(self.screen)

        self.sprite_group.draw(self.screen, self.camera.offset)

        for tilemap in self.tilemaps.values():
            if tilemap.rendered:
                tilemap.render(self.screen, (0, 0), 5)

        pygame.display.flip()

    def update(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.sprite_group.update(dt)
        self.player.update(dt)
        for tilemap in self.tilemaps.values():
            self.tilemap.update()

    def run(self):
        while self.running:
            dt = pygame.time.Clock().tick(60) / 1000

            self.draw()
            self.update(dt)