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