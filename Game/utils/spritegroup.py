
class SpriteGroup:
    def __init__(self):
        self.sprite_dict = {}

    def add(self, *sprites):
        for sprite in sprites:
            if hasattr(sprite, 'id'):
                self.sprite_dict[sprite.id] = sprite

    def remove(self, *sprites):
        for sprite in sprites:
            if hasattr(sprite, 'id') and sprite.id in self.sprite_dict:
                del self.sprite_dict[sprite.id]

    def get_by_id(self, sprite_id):
        return self.sprite_dict.get(sprite_id)

    def empty(self):
        self.sprite_dict.clear()

    def draw(self, surface, offset):
        for sprite in self.sprite_dict.values():
            x, y = sprite.rect.topleft
            x -= offset[0]
            y -= offset[1]
            surface.blit(sprite.image, x, y)

    def update(self, dt):
        for sprite in self.sprite_dict.values():
            sprite.update(dt)