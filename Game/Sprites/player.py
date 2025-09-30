import pygame
from Game.Sprites.sprite import Sprite
from Game.Sprites.crystals import Crystal
from Game.utils.utils import SpriteSheet
from Game.utils.timer import Timer


class Player(Sprite):
    def __init__(self, img=pygame.surface.Surface((32, 32)), pos=(0, 0), identifier=None, game=None, tilemap=None):
        super().__init__(img, pos, identifier)
        self.max_speed = 200
        self.acceleration = 1000
        self.friction = 1200
        self.velocity = pygame.math.Vector2(0, 0)

        self.tilemap = tilemap
        self.game = game

        self.animations = {
            "idle": (SpriteSheet("little_riven/Idle.png", tile_size=144, colorkey=(0, 0, 0)), 15, True),
            "death": (SpriteSheet("little_riven/Death.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
            "double_slash": (SpriteSheet("little_riven/Double Slash.png", tile_size=144, colorkey=(0, 0, 0)), 30, False),
            "fall": (SpriteSheet("little_riven/Fall.png", tile_size=144, colorkey=(0, 0, 0)), 15, True),
            "hurt": (SpriteSheet("little_riven/Hurt.png", tile_size=144, colorkey=(0, 0, 0)), 15, False),
            "idle_break": (SpriteSheet("little_riven/Idle Break.png", tile_size=144, colorkey=(0, 0, 0)), 30, False),
            "jump": (SpriteSheet("little_riven/Jump.png", tile_size=144, colorkey=(0, 0, 0)), 5, True),
            "run": (SpriteSheet("little_riven/Run.png", tile_size=144, colorkey=(0, 0, 0)), 10, True),
            "slash": (SpriteSheet("little_riven/Slash.png", tile_size=144, colorkey=(0, 0, 0)), 30, False),
            "smoke_in": (SpriteSheet("little_riven/Smoke In.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
            "smoke_out": (SpriteSheet("little_riven/Smoke Out.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
            "special_skill": (SpriteSheet("little_riven/Special Skill.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
        }

        self.crystals = 0

        self.animation = "idle"
        self.frame = 0

        self.visual_scale = 2
        self.scaled_sprite_size = 144 * self.visual_scale

        char_bounds = self.calculate_character_bounds()
        char_width = char_bounds['width']
        char_height = char_bounds['height']

        self.char_offset_x = char_bounds['offset_x']
        self.char_offset_y = char_bounds['offset_y']

        self.rect = pygame.Rect(pos[0], pos[1], char_width, char_height)
        self.visual_rect = pygame.Rect(0, 0, self.scaled_sprite_size, self.scaled_sprite_size)

        self.attributes = {
            "max_jumps": 1,
            "jumps": 1,
            "falling": False,
            "damaged": False,
            "attacking": False,
            "cutscene": False,
            "idle_timer": 0,
            "jumping": False,
            "can_move": True,
            "flipped": False,
            "jump_strength": 500,

            "health": 3,
            "maxhealth": 3,

            "stun": False,
            "stun_cooldown": 200,
            "dead": False,
            "death_animation_complete": False,
            "visible": True,
        }

        self.timers = {
            "damage": 0,
            "invulnerability": 0,
            "attack_cooldown": Timer(1),
        }

        self.collisions = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False,
        }

        self.gravity = 15
        self.max_fall_speed = 400
        self.double_slash_hold_ms = 250

        self.attributes.update({
            "slashing": False,
            "double_slashing": False,
            "attack_press_time": 0,
            "slash_damage_frames": 0,
            "max_slash_damage_frames": 1,
            "max_double_slash_damage_frames": 2,
            "last_x_press_time": 0,
            "double_tap_window": 500,
        })
        self.attacking_hitboxes = {
            "slash_right": pygame.Rect(self.game.screen.get_width()//2, self.game.screen.get_height()//2 + 10, 70, 15),
            "slash_left": pygame.Rect(self.game.screen.get_width()//2 - 70, self.game.screen.get_height()//2 + 10, 70, 15),
        }
        self.attacking_boolean = {
            "slash": False,
            "double_slash": False,
        }

    def controls(self):
        keys = pygame.key.get_pressed()

        if self.attributes["can_move"] and not (self.attributes.get("slashing") or self.attributes.get("double_slashing")):
            input_direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            if input_direction != 0:
                self.velocity.x += input_direction * self.acceleration * (1/60)
                self.velocity.x = max(-self.max_speed, min(self.max_speed, int(self.velocity.x)))
            else:
                if abs(self.velocity.x) > self.friction * (1/60):
                    friction_direction = -1 if self.velocity.x > 0 else 1
                    self.velocity.x += friction_direction * self.friction * (1/60)
                else:
                    self.velocity.x = 0

        if keys[pygame.K_SPACE] and self.attributes["jumps"] >= 1 and self.attributes["can_move"]:
            self.velocity.y = -self.attributes["jump_strength"]
            self.attributes["jumps"] -= 1
            self.attributes["jumping"] = True
        elif not keys[pygame.K_SPACE] and self.velocity.y < 0:
            self.velocity.y *= 0.5

        if self.velocity.x > 0:
            self.attributes["flipped"] = False
        elif self.velocity.x < 0:
            self.attributes["flipped"] = True

        if self.attributes["jumping"] and self.velocity.y < 0:
            self.attributes["jumping"] = False

    def handle_x_key_press(self):
        current_time = pygame.time.get_ticks()

        if not self.attributes.get("slashing") and not self.attributes.get("double_slashing"):
            time_since_last_press = current_time - self.attributes["last_x_press_time"]

            if time_since_last_press <= self.attributes["double_tap_window"] and self.attributes["last_x_press_time"] > 0:
                if not self.timers["attack_cooldown"].active:
                    self.attributes["double_slashing"] = True
                    self.attributes["slashing"] = False
                    self.attributes["slash_damage_frames"] = 0
                    self.frame = 0
                    self.velocity.x = 0
                    self.animation = "double_slash"
                    self.timers["attack_cooldown"].activate()
                else:
                    pass
            else:
                if not self.timers["attack_cooldown"].active:
                    self.attributes["slashing"] = True
                    self.attributes["double_slashing"] = False
                    self.attributes["attack_press_time"] = current_time
                    self.attributes["slash_damage_frames"] = 0
                    self.frame = 0
                    self.velocity.x = 0
                    self.animation = "slash"
                    self.timers["attack_cooldown"].activate()
                else:
                    pass

            self.attributes["last_x_press_time"] = current_time

    def update(self, dt, events=None):
        self.timers["attack_cooldown"].update()

        if self.timers["damage"] > 0:
            self.timers["damage"] -= dt * 1000
        if self.timers["invulnerability"] > 0:
            self.timers["invulnerability"] -= dt * 1000

        if self.timers["invulnerability"] <= 0 and self.attributes["damaged"]:
            self.attributes["damaged"] = False

        if self.animation == "hurt":
            sprite_sheet, frame_duration, is_looping = self.animations["hurt"]
            images = sprite_sheet.get_images_list()
            if int(self.frame) >= len(images) - 1:
                self.attributes["can_move"] = True
                self.attributes["stun"] = False
                self.animation = "idle"
                self.frame = 0
                if self.timers["invulnerability"] <= 0:
                    self.timers["invulnerability"] = 500

        if self.animation == "smoke_out" and self.attributes["dead"]:
            sprite_sheet, frame_duration, is_looping = self.animations["smoke_out"]
            images = sprite_sheet.get_images_list()
            if int(self.frame) >= len(images) - 1:
                self.attributes["death_animation_complete"] = True
                self.attributes["visible"] = False
                return

        if self.attributes["stun"] and isinstance(self.attributes["stun"], (int, float)):
            if pygame.time.get_ticks() - self.attributes["stun"] >= self.attributes["stun_cooldown"]:
                self.attributes["stun"] = False
                self.attributes["can_move"] = True

        self.controls()

        if self.timers["invulnerability"] <= 0 and not self.attributes["damaged"]:
            for tilemap in self.game.tilemaps.values():
                if not tilemap.rendered:
                    continue
                for enemy in tilemap.enemies.sprite_dict.values():
                    if self.rect.colliderect(enemy.rect):
                        self.attributes["health"] -= 1
                        self.attributes["damaged"] = True
                        self.timers["damage"] = 500

                        self.timers["invulnerability"] = 2000

                        if self.attributes["health"] <= 0:
                            self.attributes["dead"] = True
                            self.animation = "smoke_out"
                            self.frame = 0
                            self.velocity.x = 0
                            self.velocity.y = 0
                            self.attributes["can_move"] = False
                        else:
                            self.animation = "hurt"
                            self.frame = 0
                            enemy_center_x = enemy.rect.centerx
                            player_center_x = self.rect.centerx
                            knockback_direction = -1 if player_center_x > enemy_center_x else 1
                            self.velocity.x = knockback_direction * 150
                            self.velocity.y = -200
                            self.attributes["can_move"] = False
                            self.attributes["stun"] = pygame.time.get_ticks()
                        break


        if self.attributes.get("slashing") or self.attributes.get("double_slashing"):
            max_damage_frames = self.attributes["max_double_slash_damage_frames"] if self.attributes.get("double_slashing") else self.attributes["max_slash_damage_frames"]

            if self.attributes["slash_damage_frames"] == 0:
                pass

            if self.attributes["slash_damage_frames"] < max_damage_frames:
                if self.attributes["flipped"]:
                    for tilemap in self.game.tilemaps.values():
                        if tilemap.rendered:
                            for enemy in tilemap.enemies.sprite_dict.values():
                                rect = enemy.rect.copy()
                                rect.topleft -= self.game.camera.offset
                                if self.attacking_hitboxes["slash_left"].colliderect(rect):
                                    enemy.take_damage(1)
                                    if enemy.health <= 0:
                                        crystal = Crystal((enemy.rect.x, enemy.rect.y), enemy.drop, self.game)
                                        crystal.tilemap = enemy.tilemap
                                        enemy.tilemap.crystals.append(crystal)
                                        tilemap.enemies.remove(enemy)
                                        break

                            for breakable in tilemap.breakables.sprite_dict.values():
                                rect = breakable.rect.copy()
                                rect.topleft -= self.game.camera.offset
                                if self.attacking_hitboxes["slash_left"].colliderect(rect):
                                    breakable.take_damage(1)
                                    break
                else:
                    for tilemap in self.game.tilemaps.values():
                        if tilemap.rendered:
                            for enemy in tilemap.enemies.sprite_dict.values():
                                rect = enemy.rect.copy()
                                rect.topleft -= self.game.camera.offset
                                if self.attacking_hitboxes["slash_right"].colliderect(rect):
                                    enemy.take_damage(1)
                                    if enemy.health <= 0:
                                        crystal = Crystal((enemy.rect.x, enemy.rect.y), enemy.drop, self.game)
                                        crystal.tilemap = enemy.tilemap
                                        enemy.tilemap.crystals.append(crystal)
                                        tilemap.enemies.remove(enemy)
                                        break

                            for breakable in tilemap.breakables.sprite_dict.values():
                                rect = breakable.rect.copy()
                                rect.topleft -= self.game.camera.offset
                                if self.attacking_hitboxes["slash_right"].colliderect(rect):
                                    breakable.take_damage(1)
                                    break

                self.attributes["slash_damage_frames"] += 1

        if events:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        self.handle_x_key_press()

        if self.attributes.get("slashing") or self.attributes.get("double_slashing"):
            current_anim_key = "double_slash" if self.attributes.get("double_slashing") else "slash"
            sprite_sheet, frame_duration, is_looping = self.animations[current_anim_key]
            images = sprite_sheet.get_images_list()
            if images:
                if int(self.frame) < len(images):
                    self.image = images[int(self.frame)]
                else:
                    if self.attributes.get("double_slashing"):
                        self.attributes["double_slashing"] = False
                        self.attributes["slashing"] = False
                    else:
                        self.attributes["slashing"] = False
                    self.animation = "idle"
                    self.frame = 0
                    if self.image:
                        self.image = pygame.transform.scale(self.image, (self.scaled_sprite_size, self.scaled_sprite_size))
                        self.image.set_colorkey((0,0,0))
                        self.update_visual_rect()
                    return
            self.frame += frame_duration / 60
            if self.image:
                self.image = pygame.transform.scale(self.image, (self.scaled_sprite_size, self.scaled_sprite_size))
                self.image.set_colorkey((0,0,0))
                self.update_visual_rect()
            return

        if not self.collisions["bottom"]:
            self.velocity.y += self.gravity * dt * 60
            self.velocity.y = min(self.velocity.y, self.max_fall_speed)

        old_x = self.rect.x
        self.move(dt)
        actually_moved_x = abs(self.rect.x - old_x) > 0.1

        if self.collisions["bottom"]:
            self.attributes["jumps"] = self.attributes["max_jumps"]
            self.attributes["falling"] = False
            if self.attributes["can_move"]:
                if actually_moved_x:
                    if self.animation != "run":
                        self.animation = "run"
                        self.frame = 0
                    self.attributes["idle_timer"] = 0
                else:
                    if self.animation not in ["idle_break"] and self.animation != "idle":
                        self.animation = "idle"
                        self.frame = 0
        else:
            if self.velocity.y > 0 and self.animation != "fall":
                self.animation = "fall"
                self.frame = 0
                self.attributes["idle_timer"] = 0
            elif self.velocity.y < 0 and self.animation != "jump":
                self.animation = "jump"
                self.frame = 0

        sprite_sheet, frame_duration, is_looping = self.animations[self.animation]
        images = sprite_sheet.get_images_list()
        if images:
            if is_looping:
                self.image = images[int(self.frame) % len(images)]
            elif int(self.frame) < len(images):
                self.image = images[int(self.frame)]
            else:
                self.animation = "idle"
                self.frame = 0
                return

        if self.image:
            self.image = pygame.transform.scale(self.image, (self.scaled_sprite_size, self.scaled_sprite_size))
            self.image.set_colorkey((0,0,0))
            self.update_visual_rect()

        self.frame += frame_duration / 60

        if (self.animation == "idle" and self.collisions["bottom"] and
            self.velocity.x == 0 and self.attributes["can_move"]):
            if self.attributes["idle_timer"] >= 180:
                self.animation = "idle_break"
                self.frame = 0
                self.attributes["idle_timer"] = 0
            else:
                self.attributes["idle_timer"] += 1

    def calculate_character_bounds(self):
        idle_spritesheet = self.animations["idle"][0]
        idle_images = idle_spritesheet.get_images_list()

        if not idle_images:
            return {
                'width': 40,
                'height': 60,
                'offset_x': 72,
                'offset_y': 100
            }

        sprite = idle_images[0]

        scaled_sprite = pygame.transform.scale(sprite, (self.scaled_sprite_size, self.scaled_sprite_size))

        bounds = self.get_sprite_bounds(scaled_sprite)

        char_width = 40
        char_height = 70

        center_x = (bounds['left'] + bounds['width'] // 2)
        bottom_y = bounds['top'] + bounds['height']

        offset_x = center_x - (char_width // 2)
        offset_y = bottom_y - char_height - 3

        return {
            'width': char_width,
            'height': char_height,
            'offset_x': offset_x,
            'offset_y': offset_y
        }

    @staticmethod
    def get_sprite_bounds(surface):
        width, height = surface.get_size()

        left = width
        right = 0
        top = height
        bottom = 0

        found_pixel = False

        try:
            surface.lock()

            for y in range(height):
                for x in range(width):
                    pixel = surface.get_at((x, y))

                    if pixel[3] > 0 and pixel[:3] != (0, 0, 0):
                        found_pixel = True
                        left = min(left, x)
                        right = max(right, x)
                        top = min(top, y)
                        bottom = max(bottom, y)
        finally:
            surface.unlock()

        if not found_pixel:
            return {
                'left': width // 4,
                'top': height // 4,
                'width': width // 2,
                'height': height // 2
            }

        return {
            'left': left,
            'top': top,
            'width': right - left + 1,
            'height': bottom - top + 1
        }

    def update_visual_rect(self):
        self.visual_rect.x = self.rect.x - self.char_offset_x
        self.visual_rect.y = self.rect.y - self.char_offset_y

    def move(self, dt):
        old_x, old_y = self.rect.x, self.rect.y

        if abs(self.velocity.x) > 0.1:
            self.rect.x += self.velocity.x * dt
            if self.check_wall_collisions():
                self.rect.x = old_x
                self.velocity.x = 0

        if abs(self.velocity.y) > 0.1:
            self.rect.y += self.velocity.y * dt
            collision_result = self.check_ground_collisions()
            if collision_result:
                if self.velocity.y > 0:
                    self.collisions["bottom"] = True
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.collisions["top"] = True
                    self.velocity.y = 0
            else:
                self.collisions["top"] = False

        if not self.is_on_ground():
            self.collisions["bottom"] = False

        if hasattr(self.game, 'camera'):
            self.game.camera.update(self)

    def is_on_ground(self):
        for tilemap in self.game.tilemaps.values():
            if not tilemap.rendered:
                continue

            left_tile = int(self.rect.left - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            right_tile = int(self.rect.right - 1 - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            bottom_tile = int (self.rect.bottom - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size

            # Check tiles
            for tile_x in range(left_tile, right_tile + 1):
                original_tile_x = tile_x
                original_tile_y = bottom_tile

                for tile_key, tile_data in tilemap.tile_map.items():
                    if (tile_data['x'] - tilemap.pos.x == original_tile_x and
                        tile_data['y'] - tilemap.pos.y == original_tile_y):
                        if 'solid' in tile_data.get('properties', []):
                            tile_top = tile_data['y'] * tilemap.tile_size
                            if abs(self.rect.bottom - tile_top) <= 2:
                                return True

            # Check breakables
            for breakable in tilemap.breakables.sprite_dict.values():
                if breakable.is_solid():
                    if abs(self.rect.bottom - breakable.rect.top) <= 2:
                        # Check if player is actually above the breakable
                        if (self.rect.right > breakable.rect.left and
                            self.rect.left < breakable.rect.right):
                            return True
        return False

    def check_wall_collisions(self):
        for tilemap in self.game.tilemaps.values():
            if not tilemap.rendered:
                continue

            left_tile = int(self.rect.left - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            right_tile = int(self.rect.right - 1 - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            top_tile = int(self.rect.top - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size
            bottom_tile = int(self.rect.bottom - 1 - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size

            for tile_y in range(top_tile, bottom_tile + 1):
                for tile_key, tile_data in tilemap.tile_map.items():
                    if (tile_data['x'] - tilemap.pos.x == left_tile and
                        tile_data['y'] - tilemap.pos.y == tile_y):
                        if 'solid' in tile_data.get('properties', []):
                            tile_right = (tile_data['x'] + 1) * tilemap.tile_size
                            if self.rect.left < tile_right and self.rect.right > tile_data['x'] * tilemap.tile_size:
                                return True

            for tile_y in range(top_tile, bottom_tile + 1):
                for tile_key, tile_data in tilemap.tile_map.items():
                    if (tile_data['x'] - tilemap.pos.x == right_tile and
                        tile_data['y'] - tilemap.pos.y == tile_y):
                        if 'solid' in tile_data.get('properties', []):
                            tile_left = tile_data['x'] * tilemap.tile_size
                            if self.rect.right > tile_left and self.rect.left < (tile_data['x'] + 1) * tilemap.tile_size:
                                return True

            # Check breakable wall collisions
            for breakable in tilemap.breakables.sprite_dict.values():
                if breakable.is_solid() and self.rect.colliderect(breakable.rect):
                    return True
        return False

    def check_ground_collisions(self):
        for tilemap in self.game.tilemaps.values():
            if not tilemap.rendered:
                continue

            left_tile = int(self.rect.left - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            right_tile = int(self.rect.right - 1 - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            top_tile = int(self.rect.top - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size
            bottom_tile = int(self.rect.bottom - 1 - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size

            if self.velocity.y >= 0:
                for tile_x in range(left_tile, right_tile + 1):
                    for tile_key, tile_data in tilemap.tile_map.items():
                        x = tile_data['x'] - tilemap.pos.x == tile_x
                        y = tile_data['y'] - tilemap.pos.y >= bottom_tile
                        y_off = tile_data['y'] - tilemap.pos.y <= bottom_tile + 1
                        if x and y and y_off:
                            if 'solid' in tile_data.get('properties', []):
                                tile_top = tile_data['y'] * tilemap.tile_size
                                tile_bottom = tile_top + tilemap.tile_size
                                tile_left = tile_data['x'] * tilemap.tile_size
                                tile_right = tile_left + tilemap.tile_size

                                if (self.rect.bottom > tile_top and
                                    self.rect.top < tile_bottom and
                                    self.rect.right > tile_left and
                                    self.rect.left < tile_right):
                                    self.rect.bottom = tile_top
                                    return True

            if self.velocity.y < 0:
                for tile_x in range(left_tile, right_tile + 1):
                    for tile_key, tile_data in tilemap.tile_map.items():
                        if (tile_data['x'] - tilemap.pos.x == tile_x and
                            tile_data['y'] - tilemap.pos.y == top_tile):
                            if 'solid' in tile_data.get('properties', []):
                                tile_bottom = (tile_data['y'] + 1) * tilemap.tile_size
                                tile_left = tile_data['x'] * tilemap.tile_size
                                tile_right = tile_left + tilemap.tile_size

                                if (self.rect.top <= tile_bottom and
                                    self.rect.right > tile_left and
                                    self.rect.left < tile_right):
                                    self.rect.top = tile_bottom
                                    return True

            for breakable in tilemap.breakables.sprite_dict.values():
                if breakable.is_solid() and self.rect.colliderect(breakable.rect):
                    if self.velocity.y > 0 and self.rect.bottom > breakable.rect.top and self.rect.top < breakable.rect.top:
                        self.rect.bottom = breakable.rect.top
                        return True
                    elif self.velocity.y < 0 and self.rect.top < breakable.rect.bottom and self.rect.bottom > breakable.rect.bottom:
                        self.rect.top = breakable.rect.bottom
                        return True
        return False

    def check_collisions(self):
        wall_collision = self.check_wall_collisions()
        ground_collision = self.check_ground_collisions()
        return wall_collision or ground_collision

    def draw(self, surf, offset=(0, 0)):
        if not self.attributes["visible"]:
            return

        if hasattr(self, 'image') and self.image:
            display_image = self.image

            if self.attributes["flipped"]:
                display_image = pygame.transform.flip(self.image, True, False)

            screen_pos = (self.visual_rect.x - self.game.camera.offset.x,
                         self.visual_rect.y - self.game.camera.offset.y)
            surf.blit(display_image, screen_pos)

            from Game.utils.config import get_config
            config = get_config()
            if config.get("debug", {}).get("show_collision_boxes", False):
                screen_collision_rect = (self.rect.x - self.game.camera.offset.x,
                                       self.rect.y - self.game.camera.offset.y,
                                       self.rect.width, self.rect.height)
                screen_visual_rect = (self.visual_rect.x - self.game.camera.offset.x,
                                    self.visual_rect.y - self.game.camera.offset.y,
                                    self.visual_rect.width, self.visual_rect.height)
                pygame.draw.rect(surf, (255, 0, 0), screen_collision_rect, 2)
                pygame.draw.rect(surf, (0, 0, 255), screen_visual_rect, 1)
