import pygame

class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.sprite_dict = {}

    def add(self, *sprites):
        for sprite in sprites:
            if hasattr(sprite, 'id'):
                self.sprite_dict[sprite.id] = sprite
        super().add(*sprites)

    def remove(self, *sprites):
        for sprite in sprites:
            if hasattr(sprite, 'id') and sprite.id in self.sprite_dict:
                del self.sprite_dict[sprite.id]
        super().remove(*sprites)

    def get_by_id(self, sprite_id):
        return self.sprite_dict.get(sprite_id, None)

    def clear(self, surface, bgd):
        self.sprite_dict.clear()
        super().clear(surface, bgd)

    def empty(self):
        self.sprite_dict.clear()
        super().empty()