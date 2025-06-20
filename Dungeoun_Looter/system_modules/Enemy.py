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