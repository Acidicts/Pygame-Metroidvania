import pygame

from Game.Sprites.sprite import Sprite

class FlyingEnemy(Sprite):
    def __init__(self, game, pos, image=pygame.Surface((32, 32)), tilemaps=[], move_axis=pygame.Vector2(0, 0)):
        super().__init__(image, pos)
        self.game = game
        self.tilemaps = tilemaps
        self.speed = 2
        self.movement_range = 300
        self.start_x = pos[0]
        self.start_y = pos[1]
        self.z = 1

        self.move_axis = move_axis
        self.attributes = {"flying": True}
        self.health = 3

        self.hit = False
        self.hit_cooldown = 500
        self.last_hit_time = 0

        self.stunned = False
        self.stun_duration = 1000
        self.stun_start_time = 0

        self.knockback_force = 5
        self.knockback_direction = 0

        self.hitbox = self.rect.inflate(-10, -10)
        self.hitbox.center = self.rect.center

        self.camera_offset = pygame.Vector2(0, 0)
        self.screen_pos = pygame.Vector2(0, 0)

        self.direction_x = 1
        self.direction_y = 1

    def tilemap_collisions(self):
        for tilemap in self.tilemaps:
            if not tilemap.rendered:
                continue
            left_tile = int(self.hitbox.left - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            right_tile = int(self.hitbox.right - 1 - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size
            top_tile = int(self.hitbox.top - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size
            bottom_tile = int(self.hitbox.bottom - 1 - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size

            for tile_key, tile_data in tilemap.tile_map.items():
                if "solid" in tile_data["properties"]:
                    tile_x = tile_data["x"] - tilemap.pos.x
                    tile_y = tile_data["y"] - tilemap.pos.y

                    if (left_tile <= tile_x <= right_tile and
                        top_tile <= tile_y <= bottom_tile):

                        tile_world_x = tile_x * tilemap.tile_size + tilemap.pos.x * tilemap.tile_size
                        tile_world_y = tile_y * tilemap.tile_size + tilemap.pos.y * tilemap.tile_size
                        tile_rect = pygame.Rect(tile_world_x, tile_world_y, tilemap.tile_size, tilemap.tile_size)

                        if self.hitbox.colliderect(tile_rect):
                            overlap_left = self.hitbox.right - tile_rect.left
                            overlap_right = tile_rect.right - self.hitbox.left
                            overlap_top = self.hitbox.bottom - tile_rect.top
                            overlap_bottom = tile_rect.bottom - self.hitbox.top

                            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                            if min_overlap == overlap_left:
                                self.hitbox.right = tile_rect.left - 2
                                self.rect.right = self.hitbox.right - 5
                                if self.move_axis.x > 0:
                                    self.direction_x *= -1
                            elif min_overlap == overlap_right:
                                self.hitbox.left = tile_rect.right + 2
                                self.rect.left = self.hitbox.left + 5
                                if self.move_axis.x > 0:
                                    self.direction_x *= -1
                            elif min_overlap == overlap_top:
                                self.hitbox.bottom = tile_rect.top - 2
                                self.rect.bottom = self.hitbox.bottom - 5
                                if self.move_axis.y > 0:
                                    self.direction_y *= -1
                            elif min_overlap == overlap_bottom:
                                self.hitbox.top = tile_rect.bottom + 2
                                self.rect.top = self.hitbox.top + 5
                                if self.move_axis.y > 0:
                                    self.direction_y *= -1

                            return

    def update(self, dt):
        if self.hit >= pygame.time.get_ticks() + self.hit_cooldown:
            self.hit = False

        if self.stunned:
            if pygame.time.get_ticks() - self.stun_start_time >= self.stun_duration:
                self.stunned = False
            else:
                return

        if self.hit and pygame.time.get_ticks() - self.last_hit_time >= self.hit_cooldown:
            self.hit = False
        elif self.hit:
            self.image.fill("yellow")
        else:
            self.image.fill("purple")

        movement_vector = self.move_axis * self.speed
        self.rect.x += movement_vector.x * self.direction_x
        self.rect.y += movement_vector.y * self.direction_y

        self.tilemap_collisions()

        if self.move_axis.x != 0:
            left_boundary = self.start_x - self.movement_range
            right_boundary = self.start_x + self.movement_range

            if self.rect.x <= left_boundary:
                self.rect.x = left_boundary
                self.direction_x = 1
            elif self.rect.x >= right_boundary:
                self.rect.x = right_boundary
                self.direction_x = -1

        if self.move_axis.y != 0:
            top_boundary = self.start_y - self.movement_range
            bottom_boundary = self.start_y + self.movement_range

            if self.rect.y <= top_boundary:
                self.rect.y = top_boundary
                self.direction_y = 1
            elif self.rect.y >= bottom_boundary:
                self.rect.y = bottom_boundary
                self.direction_y = -1

        self.hitbox.center = self.rect.center

    def take_damage(self, amount):
        if not self.hit:
            self.health -= amount
            self.hit = True
            self.last_hit_time = pygame.time.get_ticks()
            self.stunned = True
            self.stun_start_time = pygame.time.get_ticks()
            self.knockback_direction = self.move_axis

            self.move_axis.x *= -1
            self.move_axis.y *= -1

            if self.health <= 0:
                self.kill()

    def update_camera_position(self, camera_offset):
        self.camera_offset = camera_offset
        self.screen_pos.x = self.rect.x - camera_offset.x
        self.screen_pos.y = self.rect.y - camera_offset.y

    def draw(self, surf, offset=pygame.Vector2(0, 0)):
        draw_pos = (self.rect.x - offset.x, self.rect.y - offset.y)
        surf.blit(self.image, draw_pos)

        if hasattr(self.game, 'config') and self.game.config.get('debug', {}).get('show_hitboxes', False):
            debug_hitbox_pos = (self.hitbox.x - offset.x, self.hitbox.y - offset.y)
            pygame.draw.rect(surf, (255, 0, 0), (*debug_hitbox_pos, self.hitbox.width, self.hitbox.height), 2)
