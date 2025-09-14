import pygame
import json
from Game.utils.config import get_config

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8
}

NEIGHBOR_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = ['solid']

scale_sizing = {
    "cave": {
        "platform": {
            "0": (54, 48),
            "1": (96, 24),
            "2": (154, 48),
            "3": (48, 24),
            "4": (24, 24),
            "5": (48, 24),
            "6": (24, 24),
            "7": (48, 24),
            "8": (48, 48),
        },
    }
}

class TileMap:
    def __init__(self, game, tile_size=48):
        self.game = game
        self.tile_size = tile_size
        self.tile_map = {}
        self.off_grid_tiles = []

    def load_map(self, path):
        with open(path, 'r') as f:
            data = json.load(f)

        self.width = data['width']
        self.height = data['height']
        self.tile_size = data['tile_size']

        for layer in data['layers']:
            if layer['type'] == 'tilelayer':
                for tile in layer['data']:
                    x, y, z = tile['x'], tile['y'], tile['z']
                    tile_type = tile['type']
                    variant = tile.get('variant', 0)
                    self.tile_map[(x, y)] = {
                        'x': int(x),
                        'y': int(y),
                        'z': int(z),
                        'environment': data['environment'],
                        'type': tile_type,
                        'variant': variant,
                        'properties': tile["properties"]
                    }

            elif layer['type'] == 'objectgroup':
                for obj in layer['objects']:
                    tile = {
                        'id': obj.get('gid', 0),
                        'x': int(obj['x']),
                        'y': int(obj['y']),
                        'z': obj['z'],
                        'width': obj.get('width', self.tile_size),
                        'height': obj.get('height', self.tile_size),
                        'properties': obj.get('properties', {})
                    }
                    self.off_grid_tiles.append(tile)

    def get_tiles_around(self, pos):
        x, y = pos
        grid_x = x // self.tile_size
        grid_y = y // self.tile_size

        tiles = {}
        for dx, dy in NEIGHBOR_OFFSET:
            neighbor_pos = (grid_x + dx, grid_y + dy)
            if neighbor_pos in self.tile_map:
                neighbor_tile = self.tile_map[neighbor_pos]
                props = neighbor_tile.get('properties', [])
                try:
                    is_solid = ('solid' in props)
                except Exception:
                    is_solid = False

                if is_solid:
                    tiles[(dx, dy)] = neighbor_tile
                else:
                    tiles[(dx, dy)] = None
            else:
                tiles[(dx, dy)] = None
        return tiles

    def render(self, surface, camera_offset, layer):
        for tile in self.tile_map.values():
            if tile.get("z") != layer:
                continue

            env = tile.get('environment')
            ttype = tile.get('type')
            variant = str(tile.get('variant', 0))

            tile_assets = self.game.assets.get(env, {})
            type_assets = tile_assets.get(ttype) if tile_assets else None
            if not type_assets:
                continue

            img = type_assets.images.get(variant)
            if img is None:
                continue

            img = pygame.transform.scale(img, scale_sizing.get(env, {}).get(ttype, {}).get(variant, (self.tile_size, self.tile_size)))

            pos = (tile['x'] * self.tile_size - camera_offset[0], tile['y'] * self.tile_size - camera_offset[1])
            pos = (int(pos[0]) + self.game.camera.offset.x, int(pos[1]) + self.game.camera.offset.y)
            surface.blit(img, pos)
