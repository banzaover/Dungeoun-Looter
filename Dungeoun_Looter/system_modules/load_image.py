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

textures = {
    "wall": load_image("wall"),
    "floor": load_image("floor"),
    "player": load_image("player", 4),
    "enemy": load_image("enemy", 0.05),
    "boss": load_image("boss", 0.4),
    "explosion": load_image("boom", 0.5) if os.path.exists(os.path.join("assets", "boom.png")) else load_image("explosion"),
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