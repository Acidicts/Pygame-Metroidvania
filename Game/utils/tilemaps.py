import pygame
from Game.utils.config import *
from Game.Sprites.Enemies.enemy import Enemy

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
    },
    "mossy": {
        "platform": {
            "0": (48, 48),
            "1": (96, 24),
            "2": (144, 48),
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
    def __init__(self, game, tile_size=48, pos=(0, 0), rendered=False):
        self.game = game
        self.tile_size = tile_size
        self.tile_map = {}
        self.off_grid_tiles = []
        self.pos = pygame.math.Vector2(*pos)
        self.sensors = {}
        self.rendered = rendered
        self.enemies = []

    def load_map(self, path):
        with open(path, 'r') as f:
            data = json.load(f)

        self.width = data['width']
        self.height = data['height']
        self.tile_size = data['tile_size']

        for layer in data['layers']:

            if layer['type'] == 'enemies':
                for enemy in layer['data']:
                    enemy_id = enemy.get("id")
                    if enemy_id is not None:
                        self.enemies.append(Enemy(pos=(int(enemy['x']) * self.tile_size + self.pos.x * self.tile_size, int(enemy['y']) * self.tile_size + self.pos.y * self.tile_size), game=self.game, tilemap=self))
                        print("Enemy added:", enemy_id)

            if layer['type'] == 'sensor_layer':
                for sensor in layer['data']:
                    sensor_id = sensor["id"]
                    if sensor_id is not None:
                        self.sensors[sensor_id] = {
                            "type": sensor['type'],
                            'x': int(sensor['x']),
                            'y': int(sensor['y']),
                            'w': int(sensor['w']),
                            'h': int(sensor['h']),
                            'properties': sensor.get('properties', []),  # Keep as list
                            'triggered': False,
                            "id": sensor_id
                        }

            if layer['type'] == 'tilelayer':
                for tile in layer['data']:
                    if "repeat" in tile["properties"]:
                        for x in range(tile["w"]):
                            for y in range(tile["h"]):
                                if tile["render_cut"][0] == 0 and x != tile["w"] - 1:
                                    world_x = int(tile['x'] + x)
                                    world_y = int(tile['y'] + y)
                                    self.tile_map[(world_x, world_y)] = {
                                        'x': world_x,
                                        'y': world_y,
                                        'z': int(tile['z']),
                                        'environment': data['environment'],
                                        'type': tile["type"],
                                        'variant': tile["variant"],
                                        'properties': tile["properties"]
                                    }
                                elif tile["render_cut"][0] != 0 and x == tile["w"] - 1:
                                    world_x = int(tile['x'] + x)
                                    world_y = int(tile['y'] + y)
                                    self.tile_map[(world_x, world_y)] = {
                                        'x': world_x,
                                        'y': world_y,
                                        'z': int(tile['z']),
                                        'environment': data['environment'],
                                        'type': tile["type"],
                                        'variant': None,
                                        'properties': tile["properties"]
                                    }
                                elif tile["render_cut"][0] != 0 and x != tile["w"] - 1:
                                    world_x = int(tile['x'] + x)
                                    world_y = int(tile['y'] + y)
                                    self.tile_map[(world_x, world_y)] = {
                                        'x': world_x,
                                        'y': world_y,
                                        'z': int(tile['z']),
                                        'environment': data['environment'],
                                        'type': tile["type"],
                                        'variant': tile["variant"],
                                        'properties': tile["properties"]
                                    }
                                if "dark" in tile["properties"]:
                                    depth = int(tile["solid_depth"])
                                    for x1 in range(tile["w"]):
                                        for y1 in range(depth):
                                            tile_x = int(tile['x'] + x1)
                                            tile_y = int(tile['y'] + y1)
                                            if (tile_x, tile_y) not in self.tile_map:
                                                self.tile_map[(tile_x, tile_y)] = {
                                                    'x': tile_x,
                                                    'y': tile_y,
                                                    'z': int(tile['z']),
                                                    'environment': data['environment'],
                                                    'type': tile["type"],
                                                    'variant': "dark",
                                                    'properties': [],
                                                }
                    else:
                        x, y, z = tile['x'], tile['y'], tile['z']
                        self.tile_map[(x, y)] = {
                            'x': int(x),
                            'y': int(y),
                            'z': int(z),
                            'environment': data['environment'],
                            'type': tile["type"],
                            'variant': tile["variant"],
                            'properties': tile["properties"]
                        }

        for pos, tile in self.tile_map.items():
            if 'solid' in tile.get('properties', []):
                pass

        for tile in self.tile_map.values():
            tile['x'] += int(self.pos.x)
            tile['y'] += int(self.pos.y)

        for sensor in self.sensors.values():
            sensor['x'] += int(self.pos.x)
            sensor['y'] += int(self.pos.y)

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
        from Game.utils.config import get_config
        config = get_config()
        screen_height = config["resolution"][1]
        for tile in self.tile_map.values():
            if tile["variant"] == "dark" or "dark" in tile.get("properties", []):
                x = tile['x'] * self.tile_size - self.game.camera.offset.x
                y = (tile['y']) * self.tile_size - self.game.camera.offset.y
                width = self.tile_size
                height = screen_height - y
                if height > 0:
                    pygame.draw.rect(surface, (0, 0, 0), (x, y, self.tile_size, self.tile_size))

        for tile in self.tile_map.values():
            if tile.get("z") != layer:
                continue

            if tile.get("variant") is None:
                continue

            env = tile.get('environment')
            ttype = tile.get('type')
            if tile.get("variant") == "dark":
                continue
            variant = int(tile.get('variant'))

            img = self.game.assets[env][ttype].get_images_list()[variant]
            if img is None:
                continue

            try:
                img = pygame.transform.scale(img, (scale_sizing[env][ttype].get(str(variant), (self.tile_size, self.tile_size))))
            except Exception as e:
                img = pygame.transform.scale(img, (self.tile_size, self.tile_size))

            world_pos = (tile['x'] * self.tile_size, tile['y'] * self.tile_size)

            screen_pos = (int(world_pos[0] - self.game.camera.offset.x), int(world_pos[1] - self.game.camera.offset.y))

            surface.blit(img, screen_pos)

        for tile in self.tile_map.values():
            world_pos = (tile['x'] * self.tile_size, tile['y'] * self.tile_size)

            screen_pos = (int(world_pos[0] - self.game.camera.offset.x), int(world_pos[1] - self.game.camera.offset.y))
            if 'solid' in tile.get('properties', []) and config.get("debug", {}).get("show_platform_hitboxes", False):
                debug_rect = pygame.Rect(
                    screen_pos[0],
                    screen_pos[1],
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(surface, (0, 255, 0), debug_rect, 1)

        for sensor in self.sensors.values():
            if config.get("debug", {}).get("show_sensors", False):
                rect = pygame.Rect(sensor["x"]*self.tile_size - self.game.camera.offset.x, sensor["y"]*self.tile_size - self.game.camera.offset.y, sensor["w"]*self.tile_size, sensor["h"]*self.tile_size)
                pygame.draw.rect(surface, (255, 0, 0), rect, 1)

    def is_solid(self, pos, offset):
        x = pos[0] // self.tile_size
        y = pos[1] // self.tile_size

        x += offset[0]
        y += offset[1]

        for i, o in self.tile_map.keys():
            if i == x and o == y:
                if "solid" in self.tile_map[x][y]["properties"]:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def update(self):
        for sensor in self.sensors.values():
            if sensor["type"] == "render":
                rect = pygame.Rect(sensor["x"] * self.tile_size,
                                   sensor["y"] * self.tile_size,
                                   sensor["w"] * self.tile_size,
                                   sensor["h"] * self.tile_size)

                player_in_sensor = rect.colliderect(self.game.player.rect)

                for prop in sensor["properties"]:
                    if "render" in prop and not sensor["triggered"] and "derender" not in prop and "toggle_render" not in prop:
                        map_name = prop.split(":")[1]
                        if player_in_sensor:
                            self.game.tilemap_current = map_name
                            self.game.tilemap = self.game.tilemaps[self.game.tilemap_current]
                            self.game.tilemaps[map_name].rendered = True
                            sensor["triggered"] = True

                    if "derender" in prop and not sensor["triggered"]:
                        map_name = prop.split(":")[1]
                        if player_in_sensor:
                            self.game.tilemap_current = map_name
                            self.game.tilemap = self.game.tilemaps[self.game.tilemap_current]
                            self.game.tilemaps[map_name].rendered = False
                            sensor["triggered"] = True

                    if "toggle_render" in prop and not sensor["triggered"]:
                        map_name = prop.split(":")[1]
                        if player_in_sensor:
                            self.game.tilemaps[map_name].rendered = not self.game.tilemaps[map_name].rendered

                            current_found = False
                            for name, tilemap in self.game.tilemaps.items():
                                if tilemap.rendered:
                                    self.game.tilemap_current = name
                                    self.game.tilemap = tilemap
                                    current_found = True
                                    break

                            if not current_found:
                                pass

                            sensor["triggered"] = True

                if sensor["triggered"] and not player_in_sensor:
                    sensor["triggered"] = False
