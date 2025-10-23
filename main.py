# Others:
import pygame

# My:
from utils.map_generator import STATIC_ENTITIES, StaticObject, close_entities
from utils.characters_and_weapons import BaseEntity, BaseWeapon, weapons, characters, zoom_map, W, H
from utils.functions import suavization


###############################################################################

###############################################################################
if __name__ == "__main__":
    player = BaseEntity(**characters["mage"])
    player.player = True
    player.colision = True
    player.put_in_inventory(BaseWeapon(**weapons["fire_staff"].copy()))
    player.put_in_inventory(BaseWeapon(**weapons["simple_bow"].copy()))

    main_pos:list = [0, 0]
    _TO_RENDER_:list[StaticObject] = close_entities(STATIC_ENTITIES, main_pos)
    _ACTIONS_:list = []

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("RPG")
    clock = pygame.time.Clock()

    # fonte padrao
    fonte = pygame.font.SysFont(None, 32)
    

    _TICK_:int = 0
    while True:
        _TICK_ = (_TICK_ + 1)%(30*3600)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))

        # Player:
        player.action(_TO_RENDER_, main_pos, _ACTIONS_, player)
        player.plot(screen, main_pos)
        
        for act in _TO_RENDER_:
            if type(act) == BaseEntity:
                temporary_TO_RENDER_ = _TO_RENDER_.copy()
                temporary_TO_RENDER_.remove(act)
                act.action(temporary_TO_RENDER_, main_pos, _ACTIONS_, player)
        _TO_RENDER_ = [a for a in _TO_RENDER_ if getattr(a, "alive", True)]

        if not player._in_invetory:
            # Others:
            for act in _ACTIONS_:
                act.action(_TO_RENDER_, _ACTIONS_, player)
                act.plot(screen, main_pos)
            _ACTIONS_ = [a for a in _ACTIONS_ if getattr(a, "alive", True)] # Remove not actions have end

            for ent in _TO_RENDER_:
                ent.plot(screen, main_pos)

        pygame.display.flip()
        clock.tick(30)

        ###########################################################################################
        
        suavization(main_pos, [player.pos[0] - W//(zoom_map*2), player.pos[1] - H//(zoom_map*2)]) # Pos screen

        if (_TICK_ % 60) == 0:
            for index in range(len(_TO_RENDER_)):
                if not _TO_RENDER_[index] in STATIC_ENTITIES:
                    STATIC_ENTITIES.append(_TO_RENDER_[index])
            _TO_RENDER_:list[StaticObject] = close_entities(STATIC_ENTITIES, main_pos)
            #print(f"{len(_TO_RENDER_) = } | {main_pos = }")
            #print(len(_ACTIONS_))
            #print(player.inventory)
