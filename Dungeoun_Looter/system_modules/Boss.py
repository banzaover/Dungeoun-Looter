from system_modules.Enemy import Enemy

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "boss")
        self.radius = 25
        self.health = 500
        self.max_health = 500
        self.speed = 0.5
        self.blade_dance_speed = 2.0
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
                for _ in range(3):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(50, 150)
                    pool_x = self.x + math.cos(angle) * distance
                    pool_y = self.y + math.sin(angle) * distance
                    poison_pools.append(PoisonPool(pool_x, pool_y, lifetime=600))
            elif self.attack_phase == 2 and self.poison_knives_cooldown <= 0:
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    dx = math.cos(rad) * 5
                    dy = math.sin(rad) * 5
                    projectiles.append(Projectile(self.x, self.y, dx, dy, 15, 1, False, is_poison=True))
                self.poison_knives_cooldown = 300

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
