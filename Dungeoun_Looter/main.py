import pygame
import random
import math
import sys
import os
from enum import Enum


pygame.init()
pygame.mixer.init()


try:
    from system_modules.WeaponType import WeaponType
    from system_modules.Enemy import Enemy
    from system_modules.Boss import Boss
    from system_modules.Player import Player
    from system_modules.Weapon import Weapon
    from system_modules.Projectile import Projectile
    from system_modules.poison_pool import PoisonPool
    from system_modules.Wall import Wall
    from system_modules.Door import Door
    from system_modules.Portal import Portal
    from system_modules.generate_level import generate_level
    from system_modules.draw_main_menu import draw_main_menu
    from system_modules.draw_floor import draw_floor
except ImportError as e:
    print(f"Failed to import module: {e}")
    pygame.quit()
    sys.exit(1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dungeon Looter")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)
DOOR_COLOR = (101, 67, 33)

FPS = 60

os.makedirs("assets", exist_ok=True)
os.makedirs("music", exist_ok=True)

def load_music(filename):
    try:
        pygame.mixer.music.load(os.path.join("music", filename))
        return True
    except:
        print(f"Failed to load music: {filename}")
        return False

def main():
    try:
        import time
        time.sleep(1)

        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        print("Checking resources...")
        print("Music files exist:",
              os.path.exists("music/menu_theme.mp3"),
              os.path.exists("music/common.mp3"),
              os.path.exists("music/boss_fight.mp3"))

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dungeon Looter")
        print("Window created successfully")

        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 24)
        big_font = pygame.font.SysFont("Arial", 48)

        if not load_music("menu_theme.mp3"):
            print("Warning: Could not load menu music")
        pygame.mixer.music.play(-1)

        in_main_menu = True
        game_started = False
        current_level = 1
        player_start_x, player_start_y = WIDTH // 4, HEIGHT // 2
        player = Player(player_start_x, player_start_y)
        walls, enemies, weapons, doors, projectiles, poison_pools, portals = generate_level(current_level, (player_start_x, player_start_y))
        running = True
        game_over = False
        level_complete = False
        victory = False
        boss_defeated = False
        boss_fight_display = False
        boss_fight_timer = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if in_main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    button_rect = draw_main_menu()
                    if button_rect.collidepoint(event.pos):
                        in_main_menu = False
                        game_started = True
                        pygame.mixer.music.stop()
                        if not load_music("common.mp3"):
                            print("Warning: Could not load game music")
                        pygame.mixer.music.play(-1)

                if game_started:
                    if event.type == pygame.KEYDOWN:
                        if game_over or victory:
                            if event.key == pygame.K_r:
                                current_level = 1
                                player = Player(WIDTH // 4, HEIGHT // 2)
                                walls, enemies, weapons, doors, projectiles, poison_pools, portals = generate_level(
                                    current_level, (WIDTH // 4, HEIGHT // 2))
                                game_over = False
                                level_complete = False
                                victory = False
                                boss_defeated = False
                                pygame.mixer.music.play(-1)
                        elif level_complete:
                            if event.key == pygame.K_SPACE:
                                current_level += 1
                                player_start_x, player_start_y = WIDTH // 2, HEIGHT // 2
                                walls, enemies, weapons, doors, projectiles, poison_pools, portals = generate_level(
                                    current_level, (player_start_x, player_start_y))
                                player.x, player.y = player_start_x, player_start_y
                                level_complete = False
                                boss_defeated = False

                                if current_level == 11:
                                    boss_fight_display = True
                                    boss_fight_timer = 90
                                    pygame.mixer.music.stop()
                                    if not load_music("boss_fight.mp3"):
                                        print("Warning: Could not load boss music")
                                    pygame.mixer.music.play(-1)

                                if current_level == 12:
                                    victory = True
                        elif event.key == pygame.K_1 and WeaponType.FISTS in player.available_weapons:
                            player.weapon = WeaponType.FISTS
                        elif event.key == pygame.K_2 and WeaponType.BATON in player.available_weapons:
                            player.weapon = WeaponType.BATON
                        elif event.key == pygame.K_3 and WeaponType.PISTOL in player.available_weapons:
                            player.weapon = WeaponType.PISTOL
                        elif event.key == pygame.K_4 and WeaponType.RIFLE in player.available_weapons:
                            player.weapon = WeaponType.RIFLE
                        elif event.key == pygame.K_5 and WeaponType.GRENADE in player.available_weapons:
                            player.weapon = WeaponType.GRENADE
                        elif event.key == pygame.K_6 and player.potions > 0:
                            player.use_potion()
                        elif event.key == pygame.K_SPACE and not level_complete:
                            player.attack(enemies, projectiles)

            if in_main_menu:
                button_rect = draw_main_menu()
                clock.tick(FPS)
                continue

            if boss_fight_display:
                boss_fight_timer -= 1
                if boss_fight_timer <= 0:
                    boss_fight_display = False

            if not game_over and not level_complete and not victory and not boss_fight_display:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    dx = -1
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx = 1
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    dy = -1
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    dy = 1
                player.move(dx, dy, walls)

                for enemy in enemies:
                    if isinstance(enemy, Boss):
                        enemy.update(player, projectiles, poison_pools, enemies)
                    else:
                        enemy.move_towards(player, walls, enemies)
                        enemy.attack(player)
                        if enemy.attack_cooldown > 0:
                            enemy.attack_cooldown -= 1

                for weapon in weapons[:]:
                    distance = math.sqrt((player.x - weapon.x) ** 2 + (player.y - weapon.y) ** 2)
                    if distance < player.radius + weapon.radius:
                        player.weapon = weapon.type
                        player.available_weapons[weapon.type] = True
                        weapons.remove(weapon)

                for door in doors:
                    distance = math.sqrt((player.x - door.x) ** 2 + (player.y - door.y) ** 2)
                    if distance < player.radius + max(door.width, door.height) // 2:
                        if not door.locked or player.keys > 0:
                            if door.locked:
                                player.keys -= 1
                            level_complete = True

                for projectile in projectiles[:]:
                    if not projectile.update():
                        if projectile.explosion_animation <= 0:
                            projectiles.remove(projectile)
                        continue

                    hit_wall = False
                    for wall in walls:
                        closest_x = max(wall.x - wall.width // 2, min(projectile.x, wall.x + wall.width // 2))
                        closest_y = max(wall.y - wall.height // 2, min(projectile.y, wall.y + wall.height // 2))
                        distance = math.sqrt((projectile.x - closest_x) ** 2 + (projectile.y - closest_y) ** 2)
                        if distance < projectile.radius + 5:
                            hit_wall = True
                            break

                    if hit_wall or projectile.lifetime <= 0:
                        if projectile.is_explosive and not projectile.has_exploded:
                            projectile.explode()
                            for enemy in enemies[:]:
                                dist = math.sqrt((projectile.x - enemy.x) ** 2 + (projectile.y - enemy.y) ** 2)
                                if dist < projectile.explosion_radius:
                                    enemy.health -= projectile.damage
                                    if enemy.health <= 0:
                                        if isinstance(enemy, Boss):
                                            boss_defeated = True
                                            portals.append(Portal(enemy.x, enemy.y))
                                        if enemy.has_key:
                                            player.keys += 1
                                        if enemy.has_potion:
                                            player.potions += 1
                                        enemies.remove(enemy)
                                        player.score += 10
                                    elif isinstance(enemy, Boss) and projectile.is_poison:
                                        enemy.blade_dance = True
                                        enemy.phase_timer = 180
                        else:
                            projectiles.remove(projectile)
                        continue

                    if not projectile.is_poison and not projectile.has_hit:
                        for enemy in enemies[:]:
                            dist = math.sqrt((projectile.x - enemy.x) ** 2 + (projectile.y - enemy.y) ** 2)
                            if dist < enemy.radius + projectile.radius:
                                enemy.health -= projectile.damage
                                projectile.has_hit = True
                                if enemy.health <= 0:
                                    if isinstance(enemy, Boss):
                                        boss_defeated = True
                                        portals.append(Portal(enemy.x, enemy.y))
                                    if enemy.has_key:
                                        player.keys += 1
                                    if enemy.has_potion:
                                        player.potions += 1
                                    enemies.remove(enemy)
                                    player.score += 10
                                elif isinstance(enemy, Boss) and projectile.is_poison:
                                    enemy.blade_dance = True
                                    enemy.phase_timer = 180
                                if not projectile.is_explosive:
                                    projectiles.remove(projectile)
                                break

                    if projectile.is_poison:
                        dist = math.sqrt((projectile.x - player.x) ** 2 + (projectile.y - player.y) ** 2)
                        if dist < player.radius + projectile.radius:
                            player.health -= 10
                            player.poison_effect = 180
                            player.slow_effect = 180
                            projectiles.remove(projectile)

                for pool in poison_pools[:]:
                    pool.update()
                    dist = math.sqrt((pool.x - player.x) ** 2 + (pool.y - player.y) ** 2)
                    if dist < player.radius + pool.radius:
                        player.health -= 0.2
                        player.poison_effect = 60
                    if pool.lifetime <= 0:
                        poison_pools.remove(pool)

                for portal in portals[:]:
                    portal.update()
                    dist = math.sqrt((portal.x - player.x) ** 2 + (portal.y - player.y) ** 2)
                    if dist < player.radius + portal.width // 2:
                        level_complete = True
                        if current_level == 11:
                            victory = True

                if player.health <= 0:
                    game_over = True

            draw_floor(screen)
            for pool in poison_pools:
                pool.draw(screen)
            for wall in walls:
                wall.draw(screen)
            for door in doors:
                door.draw(screen)
            for weapon in weapons:
                weapon.draw(screen)
            for projectile in projectiles:
                projectile.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            for portal in portals:
                portal.draw(screen)
            player.draw(screen)

            score_text = font.render(f"Score: {player.score}", True, WHITE)
            health_text = font.render(f"Health: {int(player.health)}/{player.max_health}", True, WHITE)
            keys_text = font.render(f"Keys: {player.keys}", True, WHITE)
            level_text = font.render(f"Level: {min(current_level, 11)}/11", True, WHITE)
            weapon_text = font.render(f"Weapon: {player.weapon.name}", True, WHITE)
            potions_text = font.render(f"Potions: {player.potions}", True, GREEN)

            screen.blit(score_text, (10, 10))
            screen.blit(health_text, (10, 40))
            screen.blit(keys_text, (10, 70))
            screen.blit(level_text, (10, 100))
            screen.blit(weapon_text, (10, 130))
            screen.blit(potions_text, (10, 160))

            y_offset = 10
            for i, weapon_type in enumerate(
                    [WeaponType.FISTS, WeaponType.BATON, WeaponType.PISTOL, WeaponType.RIFLE, WeaponType.GRENADE]):
                if weapon_type in player.available_weapons:
                    color = GREEN if player.weapon == weapon_type else WHITE
                    screen.blit(font.render(f"{i + 1}: {weapon_type.name}", True, color), (WIDTH - 150, y_offset))
                    y_offset += 30

            if player.potions > 0:
                potion_button = font.render("6: Use Potion", True, GREEN)
                screen.blit(potion_button, (WIDTH - 150, y_offset))

            if game_over:
                game_over_text = big_font.render("GAME OVER", True, RED)
                restart_text = font.render("Press R to restart", True, WHITE)
                screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

            if level_complete and current_level < 11:
                complete_text = big_font.render("LEVEL COMPLETE!", True, GREEN)
                next_text = font.render("Press SPACE to continue", True, WHITE)
                screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, HEIGHT // 2 + 10))

            if victory or (level_complete and current_level == 11):
                victory_text = big_font.render("VICTORY!", True, YELLOW)
                score_text = big_font.render(f"Final Score: {player.score}", True, WHITE)
                restart_text = font.render("Press R to restart", True, WHITE)
                screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 80))
                screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))

            if boss_fight_display:
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                screen.blit(s, (0, 0))

                boss_text = big_font.render("BOSS FIGHT", True, RED)
                screen.blit(boss_text,
                            (WIDTH // 2 - boss_text.get_width() // 2, HEIGHT // 2 - boss_text.get_height() // 2))

            pygame.display.flip()
            clock.tick(FPS)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()