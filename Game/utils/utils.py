import pygame
import os
import json

BASE_IMG_PATH = "Game/assets/"


def load_image(path, colorkey=(0, 0, 0)):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey(colorkey)
    if "icon_" in path:
        img = pygame.transform.scale(img, (16, 16))
    return img


def load_images(path):
    images = []
    for img_name in os.listdir(BASE_IMG_PATH + path):
        images.append(load_image(path + '/' + str(img_name)))
    return images

def load_json_as_dict(path):
    with open(BASE_IMG_PATH + path, 'r') as f:
        data = json.load(f)
    return data

class SpriteSheet:
    def __init__(self, path, tile_size=None, cut={"0":(0, 0, 64, 64)}):
        self.images = {}
        self.path = path
        self.tile_size = tile_size

        if tile_size:
            self.get_images()
        else:
            self.cut = cut
            self.cut_images()

    def get_images(self):
        base = load_image(self.path, colorkey=(255, 255, 255))
        rect = base.get_rect()

        for y in range(0, rect.height, self.tile_size):
            for x in range(0, rect.width, self.tile_size):
                temp = pygame.Surface((self.tile_size, self.tile_size))
                temp.blit(base, (0, 0), pygame.Rect(x, y, self.tile_size, self.tile_size))
                self.images[(x, y)] = temp

    def cut_images(self):
        base = load_image(self.path, colorkey=(255, 255, 255))
        for key, (x, y, w, h) in self.cut.items():
            if w > 0 and h > 0:
                temp = pygame.Surface((w, h))
                temp.blit(base, (0, 0), pygame.Rect(x, y, w, h))
                temp.set_colorkey((255, 255, 255))
                self.images[key] = temp

    def get_image(self, index):
        pass

    def get_debug_image(self):
        base = load_image(self.path, colorkey=(255, 255, 255))
        rect = base.get_rect()
        pygame.draw.rect(base, (255, 0, 0), rect, 4)

        for key, (x, y, w, h) in self.cut.items():
            if w > 0 and h > 0:
                temp = pygame.Surface((w, h))
                temp.blit(base, (0, 0), pygame.Rect(x, y, w, h))
                temp.set_colorkey((255, 255, 255))
                temp_rect = pygame.Rect(x, y, w, h)
                pygame.draw.rect(base, (255, 0, 0), temp_rect, 4)

        return base

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images))
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]
