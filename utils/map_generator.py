# Others:
from random import randint
import pygame

# My:
from utils.characters_and_weapons import zoom_map, characters, BaseEntity

size_map:int = 1024
entities_number:int = 100
_NUMER_ENEMIES_:int = 100

############################################################
class StaticObject:
    def __init__(self, x:int, y:int, size = 1, sprite:str = None, colision:bool = True):
        self._id:str = f"{randint(0, 999_999_999):09}"

        self.pos = (x, y)
        self.sprite = sprite
        self.size = size
        self.colision = colision

    def plot(self, screen, main_pos:list[float]) -> None:
        x, y, s = (self.pos[0]-main_pos[0])*zoom_map[0], (self.pos[1]-main_pos[1])*zoom_map[0], self.size*zoom_map[0]
        box = pygame.Rect(x, y, s, s)
        pygame.draw.rect(screen, (200, 100, 100), box)

        fonte = pygame.font.SysFont(None, 12)

############################################################
def close_entities(entities:list[StaticObject], pos:list[float]) -> list[StaticObject]:
    def euclidean(p1, p2) -> float:
        return ((p1[0] - p2[0])*(p1[0] - p2[0]) + (p1[1] - p2[1])*(p1[1] - p2[1]))**(0.5)

    new_list:list[StaticObject] = []
    for ent in entities:
        if euclidean(ent.pos, pos) < 2*1600/zoom_map[0]:
            new_list.append(ent)

    return new_list

def generate_enemies(_ACTIONS_):
    pass

# Statics
STATIC_ENTITIES:list = []
for _ in range(entities_number):
    STATIC_ENTITIES.append(StaticObject(x = randint(1, size_map - 1), y = randint(1, size_map - 1)))
STATIC_ENTITIES.append(StaticObject(x = 8, y = 8))


# Enemies
#for _ in range(_NUMER_ENEMIES_):
#    enemy_temp:dict = characters["slime"]
#    enemy_temp["pos"] = [randint(1, size_map - 1), randint(1, size_map - 1)]
#    enemy_temp["enemy"] = True
#    enemy_temp["colision"] = True
#    STATIC_ENTITIES.append(BaseEntity(**enemy_temp))


enemy_temp:dict = characters["slime"].copy()
enemy_temp["pos"] = [3, 3]
enemy_temp["enemy"] = True
enemy_temp["colision"] = True
enemy_temp["exp"] = 60
enemy_temp["coin"] = 10
STATIC_ENTITIES.append(BaseEntity(**enemy_temp))

enemy_temp:dict = characters["wolf"].copy()
enemy_temp["pos"] = [4, 3]
enemy_temp["enemy"] = True
enemy_temp["colision"] = True
enemy_temp["exp"] = 60
STATIC_ENTITIES.append(BaseEntity(**enemy_temp))

enemy_temp:dict = characters["mage"].copy()
enemy_temp["pos"] = [2, 4]
enemy_temp["enemy"] = True
enemy_temp["colision"] = True
enemy_temp["exp"] = 60
enemy_temp["coin"] = 10
STATIC_ENTITIES.append(BaseEntity(**enemy_temp))

enemy_temp:dict = characters["archer"].copy()
enemy_temp["pos"] = [2, 4]
enemy_temp["enemy"] = True
enemy_temp["colision"] = True
enemy_temp["exp"] = 60
STATIC_ENTITIES.append(BaseEntity(**enemy_temp))

"""
enemy_temp:dict = characters["the_randonnes"].copy()
enemy_temp["pos"] = [1, 1]
enemy_temp["enemy"] = True
enemy_temp["colision"] = True
enemy_temp["exp"] = 60
STATIC_ENTITIES.append(BaseEntity(**enemy_temp))
"""