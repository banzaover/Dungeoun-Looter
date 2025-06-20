import pygame
import random
import math
import sys
import os
from enum import Enum

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon Looter")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
LIGHT_BLUE = (100, 200, 255)
DARK_GRAY = (50, 50, 50)
DOOR_COLOR = (101, 67, 33)

FPS = 60


def load_image(name, scale=1.0, default_size=(50, 50)):
    try:
        image_path = os.path.join("assets", f"{name}.png")
        image = pygame.image.load(image_path).convert_alpha()
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except:
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        pygame.draw.rect(surf, color, (0, 0, default_size[0], default_size[1]))
        pygame.draw.line(surf, BLACK, (0, 0), (default_size[0], default_size[1]), 2)
        pygame.draw.line(surf, BLACK, (default_size[0], 0), (0, default_size[1]), 2)
        return surf


os.makedirs("assets", exist_ok=True)
os.makedirs("music", exist_ok=True)

try:
    pygame.mixer.music.load(os.path.join("music", "common.mp3"))
    boss_music_loaded = True
except:
    boss_music_loaded = False

textures = {
    "wall": load_image("wall"),
    "floor": load_image("floor"),
    "player": load_image("player", 4),
    "enemy": load_image("enemy", 0.05),
    "boss": load_image("boss", 0.4),
    "explosion": load_image("boom", 0.5) if os.path.exists(os.path.join("assets", "boom.png")) else load_image(
        "explosion"),
    "stairs": load_image("stairs"),
    "punch": load_image("punch", 0.1),
    "portal": load_image("portal", 0.5),
    "weapon": {
        "baton": load_image("baton", 0.06),
        "pistol": load_image("pistol", 0.03),
        "rifle": load_image("rifle", 0.08),
        "grenade": load_image("grenade", 0.05)
    },
    "potion": load_image("potion", 0.05)
}


class WeaponType(Enum):
    FISTS = 0
    BATON = 1
    PISTOL = 2
    RIFLE = 3
    GRENADE = 4


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.attack_damage = 20
        self.attack_cooldown = 0
        self.attack_range = 50
        self.score = 0
        self.keys = 0
        self.weapon = WeaponType.FISTS
        self.weapon_cooldown = 0
        self.slow_effect = 0
        self.poison_effect = 0
        self.direction = 0
        self.attack_animation = 0
        self.attack_angle = 0
        self.shoot_animation = 0
        self.available_weapons = {WeaponType.FISTS: True}
        self.fists_cooldown = 1 * FPS
        self.baton_cooldown = 1 * FPS
        self.pistol_cooldown = int(0.5 * FPS)
        self.rifle_cooldown = int(0.1 * FPS)
        self.grenade_cooldown = 1 * FPS
        self.potions = 0
        self.heal_animation = 0

    def move(self, dx, dy, walls):
        actual_speed = self.speed * (0.5 if self.slow_effect > 0 else 1)
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        if dx > 0:
            self.direction = 0
        elif dx < 0:
            self.direction = 1
        elif dy < 0:
            self.direction = 2
        elif dy > 0:
            self.direction = 3
        new_x = self.x + dx * actual_speed
        new_y = self.y + dy * actual_speed
        for wall in walls:
            closest_x = max(wall.x - wall.width // 2, min(new_x, wall.x + wall.width // 2))
            closest_y = max(wall.y - wall.height // 2, min(new_y, wall.y + wall.height // 2))
            distance = math.sqrt((new_x - closest_x) ** 2 + (new_y - closest_y) ** 2)
            if distance < self.radius:
                if abs(new_x - closest_x) > abs(new_y - closest_y):
                    new_x = self.x
                else:
                    new_y = self.y
        self.x = new_x
        self.y = new_y
        if self.slow_effect > 0:
            self.slow_effect -= 1
        if self.poison_effect > 0:
            self.health -= 0.5
            self.poison_effect -= 1
        if self.attack_animation > 0:
            self.attack_animation -= 1
            self.attack_angle = (self.attack_angle + 30) % 360
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.shoot_animation > 0:
            self.shoot_animation -= 1
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1
        if self.heal_animation > 0:
            self.heal_animation -= 1

    def use_potion(self):
        if self.potions > 0 and self.heal_animation <= 0:
            self.health = min(self.max_health, self.health + 75)
            self.potions -= 1
            self.heal_animation = 30

    def attack(self, enemies, projectiles):
        if self.weapon == WeaponType.FISTS:
            if self.attack_cooldown <= 0:
                self.attack_animation = 10
                for enemy in enemies[:]:
                    distance = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
                    if distance < self.attack_range + enemy.radius:
                        enemy.health -= self.attack_damage
                        if enemy.health <= 0:
                            if enemy.has_key:
                                self.keys += 1
                            if enemy.has_potion:
                                self.potions += 1
                            enemies.remove(enemy)
                            self.score += 10
                self.attack_cooldown = self.fists_cooldown
        elif self.weapon == WeaponType.BATON:
            if self.attack_cooldown <= 0:
                self.attack_animation = 15
                for enemy in enemies[:]:
                    distance = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
                    if distance < self.attack_range + enemy.radius + 20:
                        enemy.health -= self.attack_damage * 1.5
                        if enemy.health <= 0:
                            if enemy.has_key:
                                self.keys += 1
                            if enemy.has_potion:
                                self.potions += 1
                            enemies.remove(enemy)
                            self.score += 10
                self.attack_cooldown = self.baton_cooldown
        elif self.weapon == WeaponType.PISTOL:
            if self.weapon_cooldown <= 0:
                if self.direction == 0:
                    dx, dy = 10, 0
                elif self.direction == 1:
                    dx, dy = -10, 0
                elif self.direction == 2:
                    dx, dy = 0, -10
                else:
                    dx, dy = 0, 10
                projectiles.append(Projectile(self.x, self.y, dx, dy, 30, 1, False))
                self.weapon_cooldown = self.pistol_cooldown
                self.shoot_animation = 5
        elif self.weapon == WeaponType.RIFLE:
            if self.weapon_cooldown <= 0:
                for i in range(3):
                    if self.direction == 0:
                        dx, dy = 10 + random.uniform(-1, 1), random.uniform(-1, 1)
                    elif self.direction == 1:
                        dx, dy = -10 + random.uniform(-1, 1), random.uniform(-1, 1)
                    elif self.direction == 2:
                        dx, dy = random.uniform(-1, 1), -10 + random.uniform(-1, 1)
                    else:
                        dx, dy = random.uniform(-1, 1), 10 + random.uniform(-1, 1)
                    projectiles.append(Projectile(self.x, self.y, dx, dy, 20, 0.7, False))
                self.weapon_cooldown = self.rifle_cooldown
                self.shoot_animation = 5
        elif self.weapon == WeaponType.GRENADE:
            if self.weapon_cooldown <= 0:
                if self.direction == 0:
                    dx, dy = 5, 0
                elif self.direction == 1:
                    dx, dy = -5, 0
                elif self.direction == 2:
                    dx, dy = 0, -5
                else:
                    dx, dy = 0, 5
                projectiles.append(Projectile(self.x, self.y, dx, dy, 50, 3, True))
                self.weapon_cooldown = self.grenade_cooldown
                self.shoot_animation = 10

    def draw(self, screen):
        player_img = pygame.transform.flip(textures["player"], self.direction == 1, False)
        if self.poison_effect > 0:
            player_img.fill(PURPLE, special_flags=pygame.BLEND_MULT)
        if self.heal_animation > 0:
            heal_alpha = min(150, self.heal_animation * 5)
            heal_surf = pygame.Surface((player_img.get_width(), player_img.get_height()), pygame.SRCALPHA)
            heal_surf.fill((0, 255, 0, heal_alpha))
            player_img.blit(heal_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(player_img, (int(self.x) - player_img.get_width() // 2, int(self.y) - player_img.get_height() // 2))

        if self.weapon == WeaponType.FISTS and self.attack_animation > 0:
            punch_img = pygame.transform.flip(textures["punch"], self.direction == 1, False)
            offset_x = -30 if self.direction == 1 else 30
            offset_y = -30 if self.direction == 2 else (30 if self.direction == 3 else 0)
            screen.blit(punch_img, (
            self.x - punch_img.get_width() // 2 + offset_x, self.y - punch_img.get_height() // 2 + offset_y))
        elif self.weapon == WeaponType.BATON:
            weapon_img = textures["weapon"]["baton"]
            if self.direction == 0:
                offset_x, offset_y = 25, -5
                angle = 0
            elif self.direction == 1:
                offset_x, offset_y = -25, -5
                angle = 180
            elif self.direction == 2:
                offset_x, offset_y = -5, -25
                angle = 90
            else:
                offset_x, offset_y = -5, 25
                angle = 270
            if self.attack_animation > 0:
                angle += self.attack_angle if self.direction in [0, 2] else -self.attack_angle
            rotated_weapon = pygame.transform.rotate(weapon_img, angle)
            screen.blit(rotated_weapon, (
            self.x - rotated_weapon.get_width() // 2 + offset_x, self.y - rotated_weapon.get_height() // 2 + offset_y))
        elif self.weapon in [WeaponType.PISTOL, WeaponType.RIFLE, WeaponType.GRENADE]:
            weapon_img = textures["weapon"][self.weapon.name.lower()]
            if self.direction == 0:
                offset_x, offset_y = 25, -5
                angle = 0
            elif self.direction == 1:
                offset_x, offset_y = -25, -5
                angle = 180
            elif self.direction == 2:
                offset_x, offset_y = -5, -25
                angle = 90
            else:
                offset_x, offset_y = -5, 25
                angle = 270
            rotated_weapon = pygame.transform.rotate(weapon_img, angle)
            if self.shoot_animation > 0:
                kick_offset = random.randint(-2, 2)
                screen.blit(rotated_weapon, (self.x - rotated_weapon.get_width() // 2 + offset_x + kick_offset,
                                             self.y - rotated_weapon.get_height() // 2 + offset_y + random.randint(-2,
                                                                                                                   2)))
            else:
                screen.blit(rotated_weapon, (self.x - rotated_weapon.get_width() // 2 + offset_x,
                                             self.y - rotated_weapon.get_height() // 2 + offset_y))

        health_bar_length = 40
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - health_bar_length // 2, self.y - 30, health_bar_length, 5))
        pygame.draw.rect(screen, GREEN,
                         (self.x - health_bar_length // 2, self.y - 30, health_bar_length * health_ratio, 5))
        if self.attack_cooldown > 0:
            max_cooldown = self.fists_cooldown if self.weapon == WeaponType.FISTS else self.baton_cooldown
            cooldown_ratio = self.attack_cooldown / max_cooldown
            pygame.draw.rect(screen, ORANGE, (self.x - health_bar_length // 2, self.y - 35, health_bar_length, 3))
            pygame.draw.rect(screen, YELLOW, (
            self.x - health_bar_length // 2, self.y - 35, health_bar_length * (1 - cooldown_ratio), 3))


class Enemy:
    def __init__(self, x, y, enemy_type="normal", has_key=False, has_potion=False):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 1.6
        self.health = 30
        self.damage = 10
        self.attack_cooldown = 0
        self.type = enemy_type
        self.direction = 0
        self.has_key = has_key
        self.has_potion = has_potion
        self.repulsion_timer = 0
        self.repulsion_dx = 0
        self.repulsion_dy = 0

    def move_towards(self, player, walls, enemies=None):
        if enemies is None:
            enemies = []
        if self.repulsion_timer > 0:
            self.x += self.repulsion_dx
            self.y += self.repulsion_dy
            self.repulsion_timer -= 1
            return
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dx > 0:
            self.direction = 0
        elif dx < 0:
            self.direction = 1
        if dist != 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            for wall in walls:
                closest_x = max(wall.x - wall.width // 2, min(new_x, wall.x + wall.width // 2))
                closest_y = max(wall.y - wall.height // 2, min(new_y, wall.y + wall.height // 2))
                distance = math.sqrt((new_x - closest_x) ** 2 + (new_y - closest_y) ** 2)
                if distance < self.radius:
                    if abs(new_x - closest_x) > abs(new_y - closest_y):
                        new_x = self.x
                        dy = -dy * 0.5
                    else:
                        new_y = self.y
                        dx = -dx * 0.5
            for enemy in enemies:
                if enemy != self:
                    dist_to_enemy = math.sqrt((new_x - enemy.x) ** 2 + (new_y - enemy.y) ** 2)
                    if dist_to_enemy < self.radius + enemy.radius:
                        angle = math.atan2(new_y - enemy.y, new_x - enemy.x)
                        repulsion_force = 2.0
                        self.repulsion_dx = math.cos(angle) * repulsion_force
                        self.repulsion_dy = math.sin(angle) * repulsion_force
                        self.repulsion_timer = 10
                        return
            self.x = new_x
            self.y = new_y

    def attack(self, player):
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        if distance < self.radius + player.radius and self.attack_cooldown <= 0:
            player.health -= self.damage
            self.attack_cooldown = 30

    def draw(self, screen):
        enemy_img = pygame.transform.flip(textures["enemy"], self.direction == 1, False)
        screen.blit(enemy_img, (int(self.x) - enemy_img.get_width() // 2, int(self.y) - enemy_img.get_height() // 2))
        if self.has_key:
            pygame.draw.rect(screen, GOLD, (self.x - 8, self.y + 15, 16, 3))
            pygame.draw.circle(screen, GOLD, (self.x + 8, self.y + 16), 5)
        if self.has_potion:
            potion_img = textures["potion"]
            screen.blit(potion_img, (self.x - potion_img.get_width() // 2, self.y + 15))
        health_bar_length = 30
        health_ratio = self.health / 30
        pygame.draw.rect(screen, RED, (self.x - health_bar_length // 2, self.y - 25, health_bar_length, 3))
        pygame.draw.rect(screen, GREEN,
                         (self.x - health_bar_length // 2, self.y - 25, health_bar_length * health_ratio, 3))


class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "boss")
        self.radius = 25
        self.health = 500
        self.max_health = 500
        self.speed = 0.5  # Медленная базовая скорость
        self.blade_dance_speed = 2.0  # Скорость в режиме Blade Dance
        self.damage = 20
        self.attack_timer = 0
        self.attack_phase = 0
        self.phase_timer = 0
        self.blade_dance = False
        self.stunned = 0
        self.defeated = False
        self.poison_knives_cooldown = 0

    def update(self, player, projectiles, poison_pools, enemies):
        if self.defeated:
            return
        if self.stunned > 0:
            self.stunned -= 1
            return

        if self.poison_knives_cooldown > 0:
            self.poison_knives_cooldown -= 1

        self.attack_timer += 1

        if self.phase_timer <= 0:
            self.attack_phase = random.randint(1, 3)
            self.phase_timer = 120
            if self.attack_phase == 3 and self.poison_knives_cooldown <= 0:
                self.blade_dance = True
                self.phase_timer = 180
        else:
            self.phase_timer -= 1

        current_speed = self.blade_dance_speed if self.blade_dance else self.speed

        if not self.blade_dance:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist != 0:
                dx = dx / dist * current_speed
                dy = dy / dist * current_speed
                self.x += dx
                self.y += dy

        if self.blade_dance:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist != 0:
                dx = dx / dist * current_speed
                dy = dy / dist * current_speed
                self.x += dx
                self.y += dy
            if self.phase_timer <= 0:
                self.blade_dance = False
                self.stunned = 180

        if self.attack_timer >= 60 and not self.blade_dance:
            self.attack_timer = 0
            if self.attack_phase == 1:
                # Атака токсичными лужами
                for _ in range(3):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(50, 150)
                    pool_x = self.x + math.cos(angle) * distance
                    pool_y = self.y + math.sin(angle) * distance
                    poison_pools.append(PoisonPool(pool_x, pool_y, lifetime=600))
            elif self.attack_phase == 2 and self.poison_knives_cooldown <= 0:
                # Атака ядовитыми ножами
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    dx = math.cos(rad) * 5
                    dy = math.sin(rad) * 5
                    projectiles.append(Projectile(self.x, self.y, dx, dy, 15, 1, False, is_poison=True))
                self.poison_knives_cooldown = 300  # 5 секунд кулдауна

    def draw(self, screen):
        if self.defeated:
            return
        boss_img = textures["boss"]
        if self.stunned > 0:
            boss_img = boss_img.copy()
            boss_img.fill((100, 100, 100, 150), special_flags=pygame.BLEND_MULT)
        if self.blade_dance:
            boss_img_copy = boss_img.copy()
            boss_img_copy.fill((255, 0, 0, 50), special_flags=pygame.BLEND_ADD)
            screen.blit(boss_img_copy,
                        (int(self.x) - boss_img_copy.get_width() // 2, int(self.y) - boss_img_copy.get_height() // 2))
        screen.blit(boss_img, (int(self.x) - boss_img.get_width() // 2, int(self.y) - boss_img.get_height() // 2))

        health_bar_length = 60
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - health_bar_length // 2, self.y - 40, health_bar_length, 5))
        pygame.draw.rect(screen, GREEN,
                         (self.x - health_bar_length // 2, self.y - 40, health_bar_length * health_ratio, 5))

        if self.stunned > 0:
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y - 30)), 5)


class Projectile:
    def __init__(self, x, y, dx, dy, damage, speed, is_explosive, is_poison=False):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.speed = speed
        self.radius = 5
        self.lifetime = 90
        self.is_explosive = is_explosive
        self.is_poison = is_poison
        self.explosion_radius = 250 if is_explosive and not is_poison else 40
        self.explosion_animation = 0
        self.has_hit = False
        self.has_exploded = False

    def update(self):
        if self.explosion_animation > 0:
            self.explosion_animation -= 1
            return False
        if self.has_exploded:
            return False
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.lifetime -= 1
        if self.is_explosive and not self.is_poison:
            self.dy += 0.1
        return True

    def explode(self):
        if not self.has_exploded:
            self.has_exploded = True
            self.explosion_animation = 10
            return True
        return False

    def draw(self, screen):
        if self.explosion_animation > 0:
            explosion_size = int(self.explosion_radius * 2 * (1 - self.explosion_animation / 10))
            explosion_img = pygame.transform.scale(textures["explosion"], (explosion_size, explosion_size))
            screen.blit(explosion_img, (int(self.x) - explosion_size // 2, int(self.y) - explosion_size // 2))
            return
        if self.is_poison:
            pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius)
        elif self.is_explosive:
            grenade_img = textures["weapon"]["grenade"]
            screen.blit(grenade_img,
                        (int(self.x) - grenade_img.get_width() // 2, int(self.y) - grenade_img.get_height() // 2))
        else:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)


class PoisonPool:
    def __init__(self, x, y, lifetime=300):
        self.x = x
        self.y = y
        self.radius = 60  # Увеличенный радиус
        self.lifetime = lifetime

    def update(self):
        self.lifetime -= 1

    def draw(self, screen):
        alpha = min(150, self.lifetime // 2)
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*PURPLE, alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))


class Weapon:
    def __init__(self, x, y, weapon_type):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = weapon_type

    def draw(self, screen):
        if self.type == WeaponType.BATON:
            weapon_img = textures["weapon"]["baton"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))
        elif self.type == WeaponType.PISTOL:
            weapon_img = textures["weapon"]["pistol"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))
        elif self.type == WeaponType.RIFLE:
            weapon_img = textures["weapon"]["rifle"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))
        elif self.type == WeaponType.GRENADE:
            weapon_img = textures["weapon"]["grenade"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))


class Door:
    def __init__(self, x, y, locked=False):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.locked = locked

    def draw(self, screen):
        if self.locked:
            stairs_img = pygame.transform.scale(textures["stairs"], (self.width, self.height))
            stairs_img.fill(DOOR_COLOR, special_flags=pygame.BLEND_MULT)
            screen.blit(stairs_img, (self.x - self.width // 2, self.y - self.height // 2))
            pygame.draw.rect(screen, YELLOW, (self.x - 5, self.y - 15, 10, 10))
        else:
            stairs_img = pygame.transform.scale(textures["stairs"], (self.width, self.height))
            screen.blit(stairs_img, (self.x - self.width // 2, self.y - self.height // 2))


class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.animation_frame = 0

    def update(self):
        self.animation_frame = (self.animation_frame + 1) % 60

    def draw(self, screen):
        portal_img = pygame.transform.scale(textures["portal"], (
        self.width + int(5 * math.sin(self.animation_frame * 0.1)),
        self.height + int(5 * math.sin(self.animation_frame * 0.1))))
        screen.blit(portal_img, (self.x - portal_img.get_width() // 2, self.y - portal_img.get_height() // 2))


class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        tile_width = textures["wall"].get_width()
        tile_height = textures["wall"].get_height()
        for i in range(0, self.width, tile_width):
            for j in range(0, self.height, tile_height):
                screen.blit(textures["wall"], (self.x - self.width // 2 + i, self.y - self.height // 2 + j))


def draw_floor(screen):
    floor_img = textures["floor"]
    tile_width = floor_img.get_width()
    tile_height = floor_img.get_height()
    for x in range(0, WIDTH, tile_width):
        for y in range(0, HEIGHT, tile_height):
            screen.blit(floor_img, (x, y))


def generate_level(level, player_pos):
    walls = []
    enemies = []
    weapons = []
    doors = []
    projectiles = []
    poison_pools = []
    portals = []

    # Границы уровня
    walls.append(Wall(WIDTH // 2, 20, WIDTH, 40))
    walls.append(Wall(WIDTH // 2, HEIGHT - 20, WIDTH, 40))
    walls.append(Wall(20, HEIGHT // 2, 40, HEIGHT))
    walls.append(Wall(WIDTH - 20, HEIGHT // 2, 40, HEIGHT))

    # Генерация стен
    for _ in range(5 + level):
        valid = False
        attempts = 0
        while not valid and attempts < 100:
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            width = random.choice([50, 80, 100, 120])
            height = random.choice([50, 80, 100, 120])
            dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
            if dist_to_player < 150:
                attempts += 1
                continue
            valid = True
            for wall in walls:
                if (abs(x - wall.x) < (width + wall.width) // 2 + 40 and abs(y - wall.y) < (
                        height + wall.height) // 2 + 40):
                    valid = False
                    break
            attempts += 1
        if valid:
            walls.append(Wall(x, y, width, height))

    # Генерация врагов
    if level < 11:
        enemy_count = min(3 + level * 2, 12)
        key_enemy_index = random.randint(0, enemy_count - 1)
        potion_enemy_index = random.randint(0, enemy_count - 1)
        while potion_enemy_index == key_enemy_index:
            potion_enemy_index = random.randint(0, enemy_count - 1)
        for i in range(enemy_count):
            valid = False
            attempts = 0
            while not valid and attempts < 100:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
                dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
                if dist_to_player < 100:
                    attempts += 1
                    continue
                valid = True
                for wall in walls:
                    closest_x = max(wall.x - wall.width // 2, min(x, wall.x + wall.width // 2))
                    closest_y = max(wall.y - wall.height // 2, min(y, wall.y + wall.height // 2))
                    if math.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2) < 30:
                        valid = False
                        break
                attempts += 1
            if valid:
                has_key = (i == key_enemy_index)
                has_potion = (i == potion_enemy_index)
                enemies.append(Enemy(x, y, "normal", has_key, has_potion))
    elif level == 11:
        # Генерация босса справа от игрока, но не в стене
        boss_x = player_pos[0] + 150
        boss_y = player_pos[1]
        if boss_x > WIDTH - 100:
            boss_x = WIDTH - 100
        if boss_y < 100:
            boss_y = 100
        if boss_y > HEIGHT - 100:
            boss_y = HEIGHT - 100

        # Проверка, что босс не в стене
        in_wall = False
        for wall in walls:
            if (abs(boss_x - wall.x) < wall.width // 2 + 50 and abs(boss_y - wall.y) < wall.height // 2 + 50):
                in_wall = True
                break
        if not in_wall:
            enemies.append(Boss(boss_x, boss_y))
        else:
            # Если попал в стену, размещаем в правой части экрана
            enemies.append(Boss(WIDTH - 100, HEIGHT // 2))

    # Генерация оружия
    weapon_types = [
        (2, WeaponType.BATON),
        (4, WeaponType.PISTOL),
        (6, WeaponType.RIFLE),
        (8, WeaponType.GRENADE)
    ]
    for min_level, weapon_type in weapon_types:
        if level >= min_level and level < min_level + 2 and weapon_type not in [w.type for w in weapons]:
            weapon_placed = False
            attempts = 0
            while not weapon_placed and attempts < 100:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
                in_wall = False
                for wall in walls:
                    if (abs(x - wall.x) < wall.width // 2 + 20 and abs(y - wall.y) < wall.height // 2 + 20):
                        in_wall = True
                        break
                dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
                if not in_wall and dist_to_player > 100:
                    weapons.append(Weapon(x, y, weapon_type))
                    weapon_placed = True
                attempts += 1

    # Генерация дверей
    if level < 11:
        door_placed = False
        attempts = 0
        while not door_placed and attempts < 100:
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            in_wall = False
            for wall in walls:
                if (abs(x - wall.x) < wall.width // 2 + 40 and abs(y - wall.y) < wall.height // 2 + 40):
                    in_wall = True
                    break
            dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
            if not in_wall and dist_to_player > 150:
                doors.append(Door(x, y, locked=True))
                door_placed = True
            attempts += 1
        if not door_placed:
            doors.append(Door(WIDTH - 50, HEIGHT // 2, locked=True))

    return walls, enemies, weapons, doors, projectiles, poison_pools, portals


def draw_main_menu():
    screen.fill(BLACK)

    # Рисуем вход в подземелье (темный прямоугольник)
    dungeon_width, dungeon_height = 200, 150
    pygame.draw.rect(screen, DARK_GRAY, (
    WIDTH // 2 - dungeon_width // 2, HEIGHT // 2 - dungeon_height // 2, dungeon_width, dungeon_height))



    # Кнопка "Войти в подземелье"
    button_width, button_height = 200, 50
    button_x, button_y = WIDTH // 2 - button_width // 2, HEIGHT // 2 + dungeon_height // 2 + 30
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    mouse_pos = pygame.mouse.get_pos()
    button_hover = button_rect.collidepoint(mouse_pos)

    button_color = (70, 70, 70) if not button_hover else (100, 100, 100)
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)

    button_text = pygame.font.SysFont("Arial", 24).render("Войти в подземелье", True, WHITE)
    screen.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2,
                              button_y + button_height // 2 - button_text.get_height() // 2))

    # Название игры
    title_font = pygame.font.SysFont("Arial", 48)
    title_text = title_font.render("Dungeon Looter", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

    pygame.display.flip()

    return button_rect


def main():
    try:
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 24)
        big_font = pygame.font.SysFont("Arial", 48)

        # Состояния игры
        in_main_menu = True
        game_started = False
        current_level = 1
        player_start_x, player_start_y = WIDTH // 4, HEIGHT // 2
        player = Player(player_start_x, player_start_y)
        walls, enemies, weapons, doors, projectiles, poison_pools, portals = generate_level(current_level, (
        player_start_x, player_start_y))
        running = True
        game_over = False
        level_complete = False
        victory = False
        boss_defeated = False
        boss_fight_display = False
        boss_fight_timer = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if in_main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    button_rect = draw_main_menu()
                    if button_rect.collidepoint(event.pos):
                        in_main_menu = False
                        game_started = True
                        pygame.mixer.music.play(-1)

                if game_started:
                    if event.type == pygame.KEYDOWN:
                        if game_over or victory:
                            if event.key == pygame.K_r:
                                current_level = 1
                                player = Player(WIDTH // 4, HEIGHT // 2)
                                walls, enemies, weapons, doors, projectiles, poison_pools, portals = generate_level(
                                    current_level, (WIDTH // 4, HEIGHT // 2))
                                game_over = False
                                level_complete = False
                                victory = False
                                boss_defeated = False
                                pygame.mixer.music.play(-1)
                        elif level_complete:
                            if event.key == pygame.K_SPACE:
                                current_level += 1
                                player_start_x, player_start_y = WIDTH // 2, HEIGHT // 2
                                walls, enemies, weapons, doors, projectiles, poison_pools, portals = generate_level(
                                    current_level, (player_start_x, player_start_y))
                                player.x, player.y = player_start_x, player_start_y
                                level_complete = False
                                boss_defeated = False

                                if current_level == 11:
                                    boss_fight_display = True
                                    boss_fight_timer = 90  # 1.5 секунды при 60 FPS
                                    if boss_music_loaded:
                                        pygame.mixer.music.stop()
                                        pygame.mixer.music.load(os.path.join("music", "boss_fight.mp3"))
                                        pygame.mixer.music.play(-1)

                                if current_level == 12:
                                    victory = True
                        elif event.key == pygame.K_1 and WeaponType.FISTS in player.available_weapons:
                            player.weapon = WeaponType.FISTS
                        elif event.key == pygame.K_2 and WeaponType.BATON in player.available_weapons:
                            player.weapon = WeaponType.BATON
                        elif event.key == pygame.K_3 and WeaponType.PISTOL in player.available_weapons:
                            player.weapon = WeaponType.PISTOL
                        elif event.key == pygame.K_4 and WeaponType.RIFLE in player.available_weapons:
                            player.weapon = WeaponType.RIFLE
                        elif event.key == pygame.K_5 and WeaponType.GRENADE in player.available_weapons:
                            player.weapon = WeaponType.GRENADE
                        elif event.key == pygame.K_6 and player.potions > 0:
                            player.use_potion()
                        elif event.key == pygame.K_SPACE and not level_complete:
                            player.attack(enemies, projectiles)

            if in_main_menu:
                button_rect = draw_main_menu()
                clock.tick(FPS)
                continue

            if boss_fight_display:
                boss_fight_timer -= 1
                if boss_fight_timer <= 0:
                    boss_fight_display = False

            if not game_over and not level_complete and not victory and not boss_fight_display:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    dx = -1
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx = 1
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    dy = -1
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    dy = 1
                player.move(dx, dy, walls)

                for enemy in enemies:
                    if isinstance(enemy, Boss):
                        enemy.update(player, projectiles, poison_pools, enemies)
                    else:
                        enemy.move_towards(player, walls, enemies)
                        enemy.attack(player)
                        if enemy.attack_cooldown > 0:
                            enemy.attack_cooldown -= 1

                for weapon in weapons[:]:
                    distance = math.sqrt((player.x - weapon.x) ** 2 + (player.y - weapon.y) ** 2)
                    if distance < player.radius + weapon.radius:
                        player.weapon = weapon.type
                        player.available_weapons[weapon.type] = True
                        weapons.remove(weapon)

                for door in doors:
                    distance = math.sqrt((player.x - door.x) ** 2 + (player.y - door.y) ** 2)
                    if distance < player.radius + max(door.width, door.height) // 2:
                        if not door.locked or player.keys > 0:
                            if door.locked:
                                player.keys -= 1
                            level_complete = True

                for projectile in projectiles[:]:
                    if not projectile.update():
                        if projectile.explosion_animation <= 0:
                            projectiles.remove(projectile)
                        continue

                    hit_wall = False
                    for wall in walls:
                        closest_x = max(wall.x - wall.width // 2, min(projectile.x, wall.x + wall.width // 2))
                        closest_y = max(wall.y - wall.height // 2, min(projectile.y, wall.y + wall.height // 2))
                        distance = math.sqrt((projectile.x - closest_x) ** 2 + (projectile.y - closest_y) ** 2)
                        if distance < projectile.radius + 5:
                            hit_wall = True
                            break

                    if hit_wall or projectile.lifetime <= 0:
                        if projectile.is_explosive and not projectile.has_exploded:
                            projectile.explode()
                            for enemy in enemies[:]:
                                dist = math.sqrt((projectile.x - enemy.x) ** 2 + (projectile.y - enemy.y) ** 2)
                                if dist < projectile.explosion_radius:
                                    enemy.health -= projectile.damage
                                    if enemy.health <= 0:
                                        if isinstance(enemy, Boss):
                                            boss_defeated = True
                                            portals.append(Portal(enemy.x, enemy.y))
                                        if enemy.has_key:
                                            player.keys += 1
                                        if enemy.has_potion:
                                            player.potions += 1
                                        enemies.remove(enemy)
                                        player.score += 10
                                    elif isinstance(enemy, Boss) and projectile.is_poison:
                                        enemy.blade_dance = True
                                        enemy.phase_timer = 180
                        else:
                            projectiles.remove(projectile)
                        continue

                    if not projectile.is_poison and not projectile.has_hit:
                        for enemy in enemies[:]:
                            dist = math.sqrt((projectile.x - enemy.x) ** 2 + (projectile.y - enemy.y) ** 2)
                            if dist < enemy.radius + projectile.radius:
                                enemy.health -= projectile.damage
                                projectile.has_hit = True
                                if enemy.health <= 0:
                                    if isinstance(enemy, Boss):
                                        boss_defeated = True
                                        portals.append(Portal(enemy.x, enemy.y))
                                    if enemy.has_key:
                                        player.keys += 1
                                    if enemy.has_potion:
                                        player.potions += 1
                                    enemies.remove(enemy)
                                    player.score += 10
                                elif isinstance(enemy, Boss) and projectile.is_poison:
                                    enemy.blade_dance = True
                                    enemy.phase_timer = 180
                                if not projectile.is_explosive:
                                    projectiles.remove(projectile)
                                break

                    if projectile.is_poison:
                        dist = math.sqrt((projectile.x - player.x) ** 2 + (projectile.y - player.y) ** 2)
                        if dist < player.radius + projectile.radius:
                            player.health -= 10
                            player.poison_effect = 180
                            player.slow_effect = 180
                            projectiles.remove(projectile)

                for pool in poison_pools[:]:
                    pool.update()
                    dist = math.sqrt((pool.x - player.x) ** 2 + (pool.y - player.y) ** 2)
                    if dist < player.radius + pool.radius:
                        player.health -= 0.2
                        player.poison_effect = 60
                    if pool.lifetime <= 0:
                        poison_pools.remove(pool)

                for portal in portals[:]:
                    portal.update()
                    dist = math.sqrt((portal.x - player.x) ** 2 + (portal.y - player.y) ** 2)
                    if dist < player.radius + portal.width // 2:
                        level_complete = True
                        if current_level == 11:
                            victory = True

                if player.health <= 0:
                    game_over = True

            # Отрисовка
            draw_floor(screen)
            for pool in poison_pools:
                pool.draw(screen)
            for wall in walls:
                wall.draw(screen)
            for door in doors:
                door.draw(screen)
            for weapon in weapons:
                weapon.draw(screen)
            for projectile in projectiles:
                projectile.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            for portal in portals:
                portal.draw(screen)
            player.draw(screen)

            # Интерфейс
            score_text = font.render(f"Score: {player.score}", True, WHITE)
            health_text = font.render(f"Health: {int(player.health)}/{player.max_health}", True, WHITE)
            keys_text = font.render(f"Keys: {player.keys}", True, WHITE)
            level_text = font.render(f"Level: {min(current_level, 11)}/11", True, WHITE)
            weapon_text = font.render(f"Weapon: {player.weapon.name}", True, WHITE)
            potions_text = font.render(f"Potions: {player.potions}", True, GREEN)

            screen.blit(score_text, (10, 10))
            screen.blit(health_text, (10, 40))
            screen.blit(keys_text, (10, 70))
            screen.blit(level_text, (10, 100))
            screen.blit(weapon_text, (10, 130))
            screen.blit(potions_text, (10, 160))

            # Отображение доступного оружия
            y_offset = 10
            for i, weapon_type in enumerate(
                    [WeaponType.FISTS, WeaponType.BATON, WeaponType.PISTOL, WeaponType.RIFLE, WeaponType.GRENADE]):
                if weapon_type in player.available_weapons:
                    color = GREEN if player.weapon == weapon_type else WHITE
                    screen.blit(font.render(f"{i + 1}: {weapon_type.name}", True, color), (WIDTH - 150, y_offset))
                    y_offset += 30

            # Отображение кнопки для использования зелий
            if player.potions > 0:
                potion_button = font.render("6: Use Potion", True, GREEN)
                screen.blit(potion_button, (WIDTH - 150, y_offset))

            # Сообщения о состоянии игры
            if game_over:
                game_over_text = big_font.render("GAME OVER", True, RED)
                restart_text = font.render("Press R to restart", True, WHITE)
                screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

            if level_complete and current_level < 11:
                complete_text = big_font.render("LEVEL COMPLETE!", True, GREEN)
                next_text = font.render("Press SPACE to continue", True, WHITE)
                screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 10))

            if victory or (level_complete and current_level == 11):
                victory_text = big_font.render("VICTORY!", True, YELLOW)
                score_text = big_font.render(f"Final Score: {player.score}", True, WHITE)
                restart_text = font.render("Press R to restart", True, WHITE)
                screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 80))
                screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))

            if boss_fight_display:
                # Затемнение экрана
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                screen.blit(s, (0, 0))

                # Текст "BOSS FIGHT"
                boss_text = big_font.render("BOSS FIGHT", True, RED)
                screen.blit(boss_text,
                            (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT // 2 - boss_text.get_height() // 2))

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()