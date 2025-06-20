def generate_level(level, player_pos):
    walls = []
    enemies = []
    weapons = []
    doors = []
    projectiles = []
    poison_pools = []
    portals = []

    walls.append(Wall(WIDTH // 2, 20, WIDTH, 40))
    walls.append(Wall(WIDTH // 2, HEIGHT - 20, WIDTH, 40))
    walls.append(Wall(20, HEIGHT // 2, 40, HEIGHT))
    walls.append(Wall(WIDTH - 20, HEIGHT // 2, 40, HEIGHT))

    for _ in range(5 + level):
        valid = False
        attempts = 0
        while not valid and attempts < 100:
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            width = random.choice([50, 80, 100, 120])
            height = random.choice([50, 80, 100, 120])
            dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
            if dist_to_player < 150:
                attempts += 1
                continue
            valid = True
            for wall in walls:
                if (abs(x - wall.x) < (width + wall.width) // 2 + 40 and abs(y - wall.y) < (
                        height + wall.height) // 2 + 40):
                    valid = False
                    break
            attempts += 1
        if valid:
            walls.append(Wall(x, y, width, height))

    if level < 11:
        enemy_count = min(3 + level * 2, 12)
        key_enemy_index = random.randint(0, enemy_count - 1)
        potion_enemy_index = random.randint(0, enemy_count - 1)
        while potion_enemy_index == key_enemy_index:
            potion_enemy_index = random.randint(0, enemy_count - 1)
        for i in range(enemy_count):
            valid = False
            attempts = 0
            while not valid and attempts < 100:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
                dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
                if dist_to_player < 100:
                    attempts += 1
                    continue
                valid = True
                for wall in walls:
                    closest_x = max(wall.x - wall.width // 2, min(x, wall.x + wall.width // 2))
                    closest_y = max(wall.y - wall.height // 2, min(y, wall.y + wall.height // 2))
                    if math.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2) < 30:
                        valid = False
                        break
                attempts += 1
            if valid:
                has_key = (i == key_enemy_index)
                has_potion = (i == potion_enemy_index)
                enemies.append(Enemy(x, y, "normal", has_key, has_potion))
    elif level == 11:
        boss_x = player_pos[0] + 150
        boss_y = player_pos[1]
        if boss_x > WIDTH - 100:
            boss_x = WIDTH - 100
        if boss_y < 100:
            boss_y = 100
        if boss_y > HEIGHT - 100:
            boss_y = HEIGHT - 100

        in_wall = False
        for wall in walls:
            if (abs(boss_x - wall.x) < wall.width // 2 + 50 and abs(boss_y - wall.y) < wall.height // 2 + 50):
                in_wall = True
                break
        if not in_wall:
            enemies.append(Boss(boss_x, boss_y))
        else:
            enemies.append(Boss(WIDTH - 100, HEIGHT // 2))

    weapon_types = [
        (2, WeaponType.BATON),
        (4, WeaponType.PISTOL),
        (6, WeaponType.RIFLE),
        (8, WeaponType.GRENADE)
    ]
    for min_level, weapon_type in weapon_types:
        if level >= min_level and level < min_level + 2 and weapon_type not in [w.type for w in weapons]:
            weapon_placed = False
            attempts = 0
            while not weapon_placed and attempts < 100:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
                in_wall = False
                for wall in walls:
                    if (abs(x - wall.x) < wall.width // 2 + 20 and abs(y - wall.y) < wall.height // 2 + 20):
                        in_wall = True
                        break
                dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
                if not in_wall and dist_to_player > 100:
                    weapons.append(Weapon(x, y, weapon_type))
                    weapon_placed = True
                attempts += 1

    if level < 11:
        door_placed = False
        attempts = 0
        while not door_placed and attempts < 100:
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            in_wall = False
            for wall in walls:
                if (abs(x - wall.x) < wall.width // 2 + 40 and abs(y - wall.y) < wall.height // 2 + 40):
                    in_wall = True
                    break
            dist_to_player = math.sqrt((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2)
            if not in_wall and dist_to_player > 150:
                doors.append(Door(x, y, locked=True))
                door_placed = True
            attempts += 1
        if not door_placed:
            doors.append(Door(WIDTH - 50, HEIGHT // 2, locked=True))

    return walls, enemies, weapons, doors, projectiles, poison_pools, portals