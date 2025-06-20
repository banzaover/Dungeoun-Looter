def draw_main_menu():
    screen.fill(BLACK)

    title_font = pygame.font.SysFont("Arial", 48)
    title_text = title_font.render("Dungeon Looter", True, RED)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

    button_width, button_height = 200, 50
    button_x, button_y = WIDTH // 2 - button_width // 2, HEIGHT // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    mouse_pos = pygame.mouse.get_pos()
    button_hover = button_rect.collidepoint(mouse_pos)

    button_color = (70, 70, 70) if not button_hover else (100, 100, 100)
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)

    button_text = pygame.font.SysFont("Arial", 24).render("Войти в подземелье", True, WHITE)
    screen.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2,
                              button_y + button_height // 2 - button_text.get_height() // 2))

    pygame.display.flip()
    return button_rect
