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