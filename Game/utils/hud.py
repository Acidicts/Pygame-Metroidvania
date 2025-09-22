import pygame
import random

from Game.utils.transisitions import Fadeout


class Hud:
    def __init__(self, game):
        self.game = game
        self.player = self.game.player
        self.assets = self.game.assets["hud"]

        self.hearts_assets = self.assets["heart"]
        self.heart_size = 32

        self.shine_interval = 3.0
        self.shine_duration = 1.0

        self.fadeout = Fadeout(duration=3, color=(0, 0, 0))

        self.hearts = {
            "1": {"pos": (20, 12), "state": "full", "animation_state": ("full", 0), "rect": pygame.Rect(20, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "2": {"pos": (40, 12), "state": "full", "animation_state": ("full", 0), "rect": pygame.Rect(60, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "3": {"pos": (60, 12), "state": "full", "animation_state": ("full", 0), "rect": pygame.Rect(100, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "4": {"pos": (80, 12), "state": "hidden", "animation_state": ("full", 0), "rect": pygame.Rect(140, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
            "5": {"pos": (100, 12), "state": "hidden", "animation_state": ("full", 0), "rect": pygame.Rect(180, 20, self.heart_size, self.heart_size), "shine_timer": random.uniform(0, self.shine_interval)},
        }

    def update(self, dt):
        max_health = self.player.attributes["maxhealth"]
        current_health = self.player.attributes["health"]

        for i in range(1, 5):
            heart_key = str(i)
            if i <= max_health:
                if i <= current_health:
                    if self.hearts[heart_key]["state"] != "full":
                        self.hearts[heart_key]["state"] = "full"
                        self.hearts[heart_key]["animation_state"] = ("blink", 0)
                else:
                    self.hearts[heart_key]["state"] = "empty"
                    self.hearts[heart_key]["animation_state"] = ("full", 0)
            else:
                self.hearts[heart_key]["state"] = "hidden"
                self.hearts[heart_key]["animation_state"] = ("full", 0)

        for heart_data in self.hearts.values():
            if heart_data["state"] == "full":
                heart_data["shine_timer"] -= dt

                if heart_data["shine_timer"] <= 0 and heart_data["animation_state"][0] == "full":
                    heart_data["animation_state"] = ("shine", 0)
                    heart_data["shine_timer"] = self.shine_interval + random.uniform(-0.5, 0.5)  # Add some randomness

                elif heart_data["animation_state"][0] == "shine":
                    frame_count = len(self.hearts_assets["shine"].images)
                    total_shine_frames = frame_count * 5
                    if heart_data["animation_state"][1] >= total_shine_frames - 1:
                        heart_data["animation_state"] = ("full", 0)

    def draw(self, screen):
        if self.player.attributes["health"] > 0:
            self.draw_hud(screen)
        else:
            self.fadeout.draw(screen)
            if self.fadeout.opacity >= 255:
                text_surface = self.game.font.render("You Died", True, (255, 255, 255))
                text_surface = pygame.transform.scale(text_surface, (text_surface.get_width() * 4, text_surface.get_height() * 4))
                text_rect = text_surface.get_rect(center=(self.game.screen.get_width() // 2, self.game.screen.get_height() // 2))
                screen.blit(text_surface, text_rect)

    def draw_hud(self, screen):
        if self.player.attributes["maxhealth"] >= 5:
            pygame.draw.rect(screen, (0, 0, 0), (15, 10, 130, 40), border_radius=8)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (12, 10, 90, 40), border_radius=8)
        for heart in self.hearts:
            heart_data = self.hearts[heart]

            if heart_data["state"] != "hidden":

                if heart_data["state"] == "full":

                    if heart_data["animation_state"][0] == "full":
                        image = pygame.transform.scale(self.hearts_assets["full"], (self.heart_size, self.heart_size))
                        screen.blit(image, heart_data["pos"])

                    elif heart_data["animation_state"][0] == "shine":
                        frame = heart_data["animation_state"][1] // 5
                        frame_count = len(self.hearts_assets["shine"].images)
                        if frame < frame_count:
                            image = pygame.transform.scale(self.hearts_assets["shine"].images[list(self.hearts_assets["shine"].images.keys())[frame]], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])
                        heart_data["animation_state"] = ("shine", heart_data["animation_state"][1] + 1)

                    elif heart_data["animation_state"][0] == "blink":
                        frame = heart_data["animation_state"][1] // 5
                        frame_count = len(self.hearts_assets["blink"].images)
                        if frame < frame_count:
                            image = pygame.transform.scale(self.hearts_assets["blink"].images[list(self.hearts_assets["blink"].images.keys())[frame]], (self.heart_size, self.heart_size))
                            screen.blit(image, heart_data["pos"])
                        heart_data["animation_state"] = ("blink", heart_data["animation_state"][1] + 1)

                elif heart_data["state"] == "empty":
                    image = pygame.transform.scale(self.hearts_assets["empty"], (self.heart_size, self.heart_size))
                    screen.blit(image, heart_data["pos"])
