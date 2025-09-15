import pygame
from Game.Sprites.sprite import Sprite
from Game.utils.utils import SpriteSheet


class Player(Sprite):
    def __init__(self, img=pygame.surface.Surface((32, 32)), pos=(0, 0), id=None, game=None, tilemap=None):
        super().__init__(img, pos, id)
        self.max_speed = 200
        self.acceleration = 1000  # Increased for more responsive acceleration
        self.friction = 1200      # Increased for less slippery deceleration
        self.velocity = pygame.math.Vector2(0, 0)

        self.tilemap = tilemap
        self.game = game

        self.animations = {
            "idle": (SpriteSheet("little_riven/Idle.png", tile_size=144, colorkey=(0, 0, 0)), 15, True),
            "death": (SpriteSheet("little_riven/Death.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
            "double_slash": (SpriteSheet("little_riven/Double Slash.png", tile_size=144, colorkey=(0, 0, 0)), 20, False),
            "fall": (SpriteSheet("little_riven/Fall.png", tile_size=144, colorkey=(0, 0, 0)), 15, True),
            "hurt": (SpriteSheet("little_riven/Hurt.png", tile_size=144, colorkey=(0, 0, 0)), 15, False),
            "idle_break": (SpriteSheet("little_riven/Idle Break.png", tile_size=144, colorkey=(0, 0, 0)), 30, False),
            "jump": (SpriteSheet("little_riven/Jump.png", tile_size=144, colorkey=(0, 0, 0)), 5, True),
            "run": (SpriteSheet("little_riven/Run.png", tile_size=144, colorkey=(0, 0, 0)), 10, True),
            "slash": (SpriteSheet("little_riven/Slash.png", tile_size=144, colorkey=(0, 0, 0)), 20, False),
            "smoke_in": (SpriteSheet("little_riven/Smoke In.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
            "smoke_out": (SpriteSheet("little_riven/Smoke Out.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
            "special_skill": (SpriteSheet("little_riven/Special Skill.png", tile_size=144, colorkey=(0, 0, 0)), 10, False),
        }
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
        }

        self.collisions = {
            "top": False,
            "bottom": False,
            "left": False,
            "right": False,
        }

        self.gravity = 15
        self.max_fall_speed = 400

    def controls(self):
        keys = pygame.key.get_pressed()

        if self.attributes["can_move"]:
            # Get input direction
            input_direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])

            # Apply acceleration or friction
            if input_direction != 0:
                # Accelerate in the input direction
                self.velocity.x += input_direction * self.acceleration * (1/60)  # Assuming 60 FPS
                # Clamp to max speed
                self.velocity.x = max(-self.max_speed, min(self.max_speed, self.velocity.x))
            else:
                # Apply friction when no input
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

        if self.velocity.y < 0 and self.animation != "jump":
            self.animation = "jump"
            self.frame = 0

        if self.velocity.x > 0:
            self.attributes["flipped"] = False
        elif self.velocity.x < 0:
            self.attributes["flipped"] = True

        if self.attributes["jumping"] and self.velocity.y < 0:
            self.attributes["jumping"] = False

    def update(self, dt):
        self.controls()

        if not self.collisions["bottom"]:
            self.velocity.y += self.gravity * dt * 60
            self.velocity.y = min(self.velocity.y, self.max_fall_speed)

        # Store position before movement to check if we actually moved
        old_x = self.rect.x

        self.move(dt)

        # Check if we actually moved horizontally (not just had velocity)
        actually_moved_x = abs(self.rect.x - old_x) > 0.1

        # Handle animations based on player state
        if self.collisions["bottom"]:
            self.attributes["jumps"] = self.attributes["max_jumps"]
            self.attributes["falling"] = False

            # Ground-based animations - always update when on ground
            if self.attributes["can_move"]:
                if actually_moved_x:
                    if self.animation != "run":
                        self.animation = "run"
                        self.frame = 0
                    self.attributes["idle_timer"] = 0
                else:
                    # Only switch to idle if not in a special animation
                    if self.animation not in ["idle_break"]:
                        if self.animation != "idle":
                            self.animation = "idle"
                            self.frame = 0
        else:
            # Air-based animations
            if self.velocity.y > 0:
                # Falling
                if self.animation != "fall":
                    self.animation = "fall"
                    self.frame = 0
                self.attributes["idle_timer"] = 0
            elif self.velocity.y < 0:
                # Jumping up
                if self.animation != "jump":
                    self.animation = "jump"
                    self.frame = 0

        anim_data = self.animations[self.animation]
        sprite_sheet, frame_duration, is_looping = anim_data

        images = sprite_sheet.get_images_list()
        if images:
            if is_looping:
                self.image = images[int(self.frame) % len(images)]
            elif int(self.frame) < len(images):
                self.image = images[min(int(self.frame), len(images) - 1)]
            else:
                if self.animation == "idle_break":
                    self.animation = "idle"
                    self.frame = 0
                    self.attributes["idle_timer"] = 0
                else:
                    self.animation = "idle"
                    self.frame = 0
                return

        if hasattr(self, 'image') and self.image:
            scaled_size = (self.scaled_sprite_size, self.scaled_sprite_size)
            self.image = pygame.transform.scale(self.image, scaled_size)
            self.image.set_colorkey((0, 0, 0))

            self.update_visual_rect()

        self.frame += frame_duration / 60

        if self.animation == "idle" and self.collisions["bottom"] and self.velocity.x == 0 and self.attributes["can_move"]:
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

    def get_sprite_bounds(self, surface):
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

        # Move horizontally first
        if abs(self.velocity.x) > 0.1:
            self.rect.x += self.velocity.x * dt
            # Check for wall collisions
            if self.check_wall_collisions():
                self.rect.x = old_x
                self.velocity.x = 0

        # Then move vertically
        if abs(self.velocity.y) > 0.1:
            old_y = self.rect.y
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

        # Always check if we're still on solid ground (even when not moving vertically)
        if not self.is_on_ground():
            self.collisions["bottom"] = False

        # Update camera to follow player
        if hasattr(self.game, 'camera'):
            self.game.camera.update(self)

    def is_on_ground(self):
        """Check if the player is currently standing on solid ground"""
        # Convert player's world position to tile coordinates
        left_tile = self.rect.left // self.tilemap.tile_size
        right_tile = (self.rect.right - 1) // self.tilemap.tile_size
        bottom_tile = self.rect.bottom // self.tilemap.tile_size

        # Check if there's solid ground directly below the player
        for tile_x in range(left_tile, right_tile + 1):
            if (tile_x, bottom_tile) in self.tilemap.tile_map:
                tile = self.tilemap.tile_map[(tile_x, bottom_tile)]
                if 'solid' in tile.get('properties', []):
                    # Calculate the exact top of the tile
                    tile_top = bottom_tile * self.tilemap.tile_size

                    # Check if player's bottom is touching or very close to the tile top
                    if abs(self.rect.bottom - tile_top) <= 2:  # Small tolerance for floating point errors
                        return True

        return False

    def check_wall_collisions(self):
        """Check for wall collisions specifically"""
        # Convert player's world position to tile coordinates
        left_tile = self.rect.left // self.tilemap.tile_size
        right_tile = (self.rect.right - 1) // self.tilemap.tile_size
        top_tile = self.rect.top // self.tilemap.tile_size
        bottom_tile = (self.rect.bottom - 1) // self.tilemap.tile_size

        # Check for wall collisions on the sides
        for tile_y in range(top_tile, bottom_tile + 1):
            # Check left wall
            if (left_tile, tile_y) in self.tilemap.tile_map:
                tile = self.tilemap.tile_map[(left_tile, tile_y)]
                if 'solid' in tile.get('properties', []):
                    tile_right = (left_tile + 1) * self.tilemap.tile_size
                    if self.rect.left < tile_right:
                        return True

            # Check right wall
            if (right_tile, tile_y) in self.tilemap.tile_map:
                tile = self.tilemap.tile_map[(right_tile, tile_y)]
                if 'solid' in tile.get('properties', []):
                    tile_left = right_tile * self.tilemap.tile_size
                    if self.rect.right > tile_left:
                        return True

        return False

    def check_ground_collisions(self):
        """Check for ground and ceiling collisions specifically"""
        # Convert player's world position to tile coordinates
        left_tile = self.rect.left // self.tilemap.tile_size
        right_tile = (self.rect.right - 1) // self.tilemap.tile_size
        top_tile = self.rect.top // self.tilemap.tile_size
        bottom_tile = (self.rect.bottom - 1) // self.tilemap.tile_size

        # Check ground collision when falling
        if self.velocity.y >= 0:
            for tile_x in range(left_tile, right_tile + 1):
                for tile_y in range(bottom_tile, bottom_tile + 2):
                    if (tile_x, tile_y) in self.tilemap.tile_map:
                        tile = self.tilemap.tile_map[(tile_x, tile_y)]
                        if 'solid' in tile.get('properties', []):
                            tile_top = tile_y * self.tilemap.tile_size
                            tile_bottom = tile_top + self.tilemap.tile_size

                            if (self.rect.bottom > tile_top and
                                self.rect.top < tile_bottom and
                                self.rect.right > tile_x * self.tilemap.tile_size and
                                self.rect.left < (tile_x + 1) * self.tilemap.tile_size):

                                self.rect.bottom = tile_top
                                return True

        # Check ceiling collision when jumping
        if self.velocity.y < 0:
            for tile_x in range(left_tile, right_tile + 1):
                if (tile_x, top_tile) in self.tilemap.tile_map:
                    tile = self.tilemap.tile_map[(tile_x, top_tile)]
                    if 'solid' in tile.get('properties', []):
                        tile_bottom = (top_tile + 1) * self.tilemap.tile_size
                        if self.rect.top <= tile_bottom:
                            return True

        return False

    def check_collisions(self):
        """Legacy method - now just calls the specific collision methods"""
        wall_collision = self.check_wall_collisions()
        ground_collision = self.check_ground_collisions()
        return wall_collision or ground_collision

    def draw(self, surf):
        if hasattr(self, 'image') and self.image:
            display_image = self.image
            if self.attributes["flipped"]:
                display_image = pygame.transform.flip(self.image, True, False)

            # Apply camera offset to the visual rect position for screen rendering
            screen_pos = (self.visual_rect.x - self.game.camera.offset.x,
                         self.visual_rect.y - self.game.camera.offset.y)
            surf.blit(display_image, screen_pos)

            # Debug: draw collision boxes with camera offset applied (only if enabled in config)
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
