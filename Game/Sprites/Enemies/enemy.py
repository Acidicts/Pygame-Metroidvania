from Game.Sprites.sprite import PhysicsSprite
import pygame


class Enemy(PhysicsSprite):
    def __init__(self,image=pygame.Surface((32, 32)), pos=(0, 0), game=None, tilemap=None, health=0):
        image.fill((255,0,0))
        super().__init__(image, pos, tilemap)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.image.fill("red")
        self.rect = self.image.get_rect(topleft=pos)
        self.health = health
        self.tilemap = tilemap
        self.game = game

        self.direction = 1
        self.speed = 1

        self.friction = -0.02
        self.gravity = 15

        self.hit = False
        self.hit_cooldown = 0

        self.stunned = False
        self.stun_duration = 0.3 * 1000
        self.stun_start_time = 0
        self.knockback_force = 150
        self.knockback_direction = 0

        self.attributes = {}

    def update(self, dt=0):
        if not self.stunned:
            self.acc.x = self.direction * self.speed * 5
        else:
            self.acc.x = 0

        super().update(dt)

        if self.hit and pygame.time.get_ticks() - self.hit >= self.hit_cooldown:
            self.hit = False
        elif self.hit:
            self.image.fill("yellow")
        elif self.stunned:
            self.image.fill("orange")
        else:
            self.image.fill("red")

        if self.stunned:
            if pygame.time.get_ticks() - self.stun_start_time >= self.stun_duration:
                self.stunned = False
            else:
                self.vel.x *= 0.9
                return

        if self.collisions["left"] or self.collisions["right"]:
            self.direction *= -1
            self.vel.x = 0

        if self.collisions["bottom"]:
            check_distance = self.rect.width + 5
            check_x = self.rect.centerx + (self.direction * check_distance)
            check_y = self.rect.bottom + 10

            ground_ahead = False
            if self.game and hasattr(self.game, 'tilemaps'):
                for tilemap in self.game.tilemaps.values():
                    if not tilemap.rendered:
                        continue

                    tile_x = int((check_x - tilemap.pos.x * tilemap.tile_size) // tilemap.tile_size)
                    tile_y = int((check_y - tilemap.pos.y * tilemap.tile_size) // tilemap.tile_size)

                    for tile_key, tile_data in tilemap.tile_map.items():
                        if (tile_data['x'] - tilemap.pos.x == tile_x and
                            tile_data['y'] - tilemap.pos.y == tile_y):
                            if 'solid' in tile_data.get('properties', []):
                                ground_ahead = True
                                break

                    if ground_ahead:
                        break

            if not ground_ahead:
                self.direction *= -1
                self.vel.x = 0


    def take_damage(self, amount):
        if not self.hit:
            self.health -= amount
            self.hit = pygame.time.get_ticks()
            self.vel.x = self.direction * -50

            self.knockback_direction = -self.direction
            self.vel.x += self.knockback_direction * self.knockback_force

            self.stunned = True
            self.stun_start_time = pygame.time.get_ticks()

    def draw(self, surface, offset=pygame.math.Vector2(0, 0)):
        surface.blit(self.image, self.rect.topleft - offset)