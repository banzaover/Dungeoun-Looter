class Weapon:
    def __init__(self, x, y, weapon_type):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = weapon_type

    def draw(self, screen):
        if self.type == WeaponType.BATON:
            weapon_img = textures["weapon"]["baton"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))
        elif self.type == WeaponType.PISTOL:
            weapon_img = textures["weapon"]["pistol"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))
        elif self.type == WeaponType.RIFLE:
            weapon_img = textures["weapon"]["rifle"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))
        elif self.type == WeaponType.GRENADE:
            weapon_img = textures["weapon"]["grenade"]
            screen.blit(weapon_img, (self.x - weapon_img.get_width() // 2, self.y - weapon_img.get_height() // 2))