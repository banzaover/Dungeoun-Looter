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