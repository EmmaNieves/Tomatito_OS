def resolve_platform_collisions(entity, platforms):
    """
    Resuelve colisiones de un rect movil contra una lista
    de plataformas. Usa la posicion previa para decidir
    de que lado viene el choque.
    """
    entity.on_ground = False

    for plat in platforms:
        if not entity.rect.colliderect(plat.rect):
            continue

        prev_bottom = entity.rect.bottom - entity.vel_y
        prev_top = entity.rect.top - entity.vel_y
        prev_right = entity.rect.right - entity.vel_x
        prev_left = entity.rect.left - entity.vel_x

        if prev_bottom <= plat.rect.top and entity.vel_y >= 0:
            entity.rect.bottom = plat.rect.top
            entity.vel_y = 0
            entity.on_ground = True
        elif prev_top >= plat.rect.bottom and entity.vel_y < 0:
            entity.rect.top = plat.rect.bottom
            entity.vel_y = 0
        elif prev_right <= plat.rect.left:
            entity.rect.right = plat.rect.left
            entity.vel_x = 0
        elif prev_left >= plat.rect.right:
            entity.rect.left = plat.rect.right
            entity.vel_x = 0
