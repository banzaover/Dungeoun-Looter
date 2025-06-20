def draw_floor(screen):
    floor_img = textures["floor"]
    tile_width = floor_img.get_width()
    tile_height = floor_img.get_height()
    for x in range(0, WIDTH, tile_width):
        for y in range(0, HEIGHT, tile_height):
            screen.blit(floor_img, (x, y))