import pygame.font

from Game.Sprites.player import Player

from Game.utils.camera import Camera
from Game.utils.config import get_config
from Game.utils.utils import *
from Game.utils.spritegroup import SpriteGroup
from Game.utils.tilemaps import TileMap
from Game.Sprites.Enemies.enemy import Enemy
from Game.utils.hud import Hud


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

        self.hud = Hud(self)

        pygame.font.init()
        self.fonts = {
            "workbench": pygame.font.Font("Game/assets/fonts/workbench.ttf", 36),
            "Arial": pygame.font.SysFont("Arial", 16)
        }

    def setup(self):
        self.assets = {
            "hud":
                {
                    "heart": {
                        "full": load_image("hud/Heart Container Silver/heart_silver_full.png"),
                        "half": load_image("hud/Heart Container Silver/heart_silver_half.png"),
                        "shine": SpriteSheet("hud/Heart Container Silver/heart_silver_shine_full.png", tile_size=16),
                        "blink": SpriteSheet("hud/Heart Container Silver/heart_silver_blink_full.png", tile_size=16),
                        "empty": load_image("hud/Heart Container General/heart_empty.png"),
                    },
                },
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

                for enemy in tilemap.enemies:
                    enemy.draw(self.screen, self.camera.offset)

        self.hud.draw(self.screen)

        pygame.display.flip()

    def update(self, dt):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            events.append(event)

        self.sprite_group.update(dt)
        self.player.update(dt, events)
        self.hud.update(dt)  # Add HUD update for shine animations
        for tilemap in self.tilemaps.values():
            tilemap.update()
            if tilemap.rendered:
                for enemy in tilemap.enemies:
                    enemy.update(dt)

    def run(self):
        while self.running:
            dt = pygame.time.Clock().tick(60) / 1000

            self.draw()
            self.update(dt)