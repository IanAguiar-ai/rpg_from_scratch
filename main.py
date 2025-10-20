# Others:
import pygame

# My:
from utils.map_generator import static_entities, StaticObject, close_entities
from utils.characters_and_weapons import BaseEntity, weapons, characters, zoom_map
from utils.functions import suavization


###############################################################################

###############################################################################
if __name__ == "__main__":
    player = BaseEntity(**characters["mage"])
    main_pos:list = [0, 0]
    to_render:list[StaticObject] = close_entities(static_entities, main_pos)

    pygame.init()
    W, H = 1600, 900
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("RPG")
    clock = pygame.time.Clock()

    # fonte padrao
    fonte = pygame.font.SysFont(None, 32)

    _TICK_:int = 0
    while True:
        _TICK_ = (_TICK_ + 1)%(30*3600) # 1 hour

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))                 # fundo preto

        player.action(to_render, main_pos)
        player.plot(screen, main_pos)

        for ent in to_render:
            ent.plot(screen, main_pos)

        pygame.display.flip()
        clock.tick(30)                       # 30 FPS

        ###########################################################################################
        
        suavization(main_pos, [player.pos[0] - W//(zoom_map*2), player.pos[1] - H//(zoom_map*2)]) # Pos screen

        if (_TICK_ % 60) == 0:
            to_render:list[StaticObject] = close_entities(static_entities, main_pos)
            #print(f"{len(to_render) = } | {main_pos = }")

