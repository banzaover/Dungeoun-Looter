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