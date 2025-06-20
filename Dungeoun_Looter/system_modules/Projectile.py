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
