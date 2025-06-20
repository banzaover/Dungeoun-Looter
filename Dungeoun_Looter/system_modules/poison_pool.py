class PoisonPool:
    def __init__(self, x, y, lifetime=300):
        self.x = x
        self.y = y
        self.radius = 60
        self.lifetime = lifetime

    def update(self):
        self.lifetime -= 1

    def draw(self, screen):
        alpha = min(150, self.lifetime // 2)
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*PURPLE, alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))