# Others:
from random import randint
import pygame

# My:
from utils.characters_and_weapons import zoom_map

size_map:int = 1024
entities_number:int = 100

############################################################
class StaticObject:
    def __init__(self, x:int, y:int, size = 1, sprite:str = None, colision:bool = True):
        self.pos = (x, y)
        self.sprite = sprite
        self.size = size
        self.colision = colision

    def plot(self, screen, main_pos:list[float]) -> None:
        x, y, s = (self.pos[0]-main_pos[0])*zoom_map, (self.pos[1]-main_pos[1])*zoom_map, self.size*zoom_map
        box = pygame.Rect(x, y, s, s)
        pygame.draw.rect(screen, (200, 100, 100), box)

        fonte = pygame.font.SysFont(None, 12)

############################################################
def close_entities(entities:list[StaticObject], pos:list[float]) -> list[StaticObject]:
    def euclidean(p1, p2) -> float:
        return ((p1[0] - p2[0])*(p1[0] - p2[0]) + (p1[1] - p2[1])*(p1[1] - p2[1]))**(0.5)

    new_list:list[StaticObject] = []
    for ent in entities:
        if euclidean(ent.pos, pos) < 2*1600/zoom_map:
            new_list.append(ent)

    return new_list


static_entities:list = []
for _ in range(entities_number):
    static_entities.append(StaticObject(x = randint(1, size_map - 1), y = randint(1, size_map - 1)))
static_entities.append(StaticObject(x = 12, y = 12))