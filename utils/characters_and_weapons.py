# Others:
import pygame

zoom_map:int = 100

######################################################################################
def _aabb_overlap(ax:float, ay:float, asize:float, bx:float, by:float, bsize:float) -> bool:
    """Retorna True se [ax,ay,asize] colide com [bx,by,bsize] (quadrados AABB)."""
    return (ax < bx + bsize and ax + asize > bx and ay < by + bsize and ay + asize > by)

#######################################################################################
class BaseEntity:
    def __init__(self, name:str, hp:float, speed:float, aceleration:float, size:float, q, e, space, q_time:int, e_time:int, space_time:int, frame:str = None, pos:list[float] = [5, 5],
                 q_function = None, e_function = None, space_function = None) -> None:

        # Atributes
        self.name:str = name
        self.hp:float = hp
        self.max_hp:float = hp
        self.speed:float = speed
        self.aceleration:float = aceleration
        self.size:float = size

        # Position
        self.pos:list[float] = pos
        self.pos_aceleration:list[float] = [0, 0]

        # Actions
        self.q = q
        self.e = e
        self.space = space
        self.times:dict = {"q":q_time, "e":e_time, "space":space_time,
                           "max_q":q_time, "max_e":e_time, "max_space":space_time}
        self.functions:dict = {"q":q_function, "e":e_function, "space":space_function}
        self.next_action:str = None
        self._lmb_prev:bool = False  # left botton mouse
        self.last_click_world:list = None

        # Frames
        self.frame:str = frame

    def action(self, colliders:list, main_pos:list[float]) -> None:
        # Moviment
        self.pos_aceleration[0] *= 0.9
        self.pos_aceleration[1] *= 0.9

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.pos_aceleration[0] -= self.aceleration
        if keys[pygame.K_d]:
            self.pos_aceleration[0] += self.aceleration
        if keys[pygame.K_w]:
            self.pos_aceleration[1] -= self.aceleration
        if keys[pygame.K_s]:
            self.pos_aceleration[1] += self.aceleration

        self.pos_aceleration[0] = max(-self.speed, min(self.speed, self.pos_aceleration[0]))
        self.pos_aceleration[1] = max(-self.speed, min(self.speed, self.pos_aceleration[1]))

        new_x = self.pos[0] + self.pos_aceleration[0]
        new_y = self.pos[1]
        collided_x = False
        for ent in colliders:
            if getattr(ent, "colision", False):
                if _aabb_overlap(new_x, new_y, self.size, ent.pos[0], ent.pos[1], ent.size):
                    collided_x = True
                    break
        if not collided_x:
            self.pos[0] = new_x
        else:
            self.pos_aceleration[0] = 0.0

        new_x = self.pos[0]
        new_y = self.pos[1] + self.pos_aceleration[1]
        collided_y = False
        for ent in colliders:
            if getattr(ent, "colision", False):
                if _aabb_overlap(new_x, new_y, self.size, ent.pos[0], ent.pos[1], ent.size):
                    collided_y = True
                    break
        if not collided_y:
            self.pos[1] = new_y
        else:
            self.pos_aceleration[1] = 0.0

        # Actions
        if keys[pygame.K_q]:
            self.next_action:str = "q"
        elif keys[pygame.K_e]:
            self.next_action:str = "e"
        elif keys[pygame.K_SPACE]:
            self.next_action:str = "space"

        # --- Mouse: clique esquerdo + posição ---
        if (self.next_action != None) and (self.times[self.next_action] == self.times[f"max_{self.next_action}"]):
            buttons = pygame.mouse.get_pressed(3)        # (L, M, R)
            lmb = bool(buttons[0])
            if lmb and (not self._lmb_prev):
                sx, sy = pygame.mouse.get_pos()
                wx = main_pos[0] + sx/zoom_map
                wy = main_pos[1] + sy/zoom_map
                self.last_click_world = (wx, wy)
                self.times[self.next_action] = 0
                self.next_action:str = None

            self._lmb_prev = lmb

    def plot(self, screen, main_pos:list[float]) -> None:
        # Entitie
        x, y, s = (self.pos[0]-main_pos[0])*zoom_map, (self.pos[1]-main_pos[1])*zoom_map, self.size*zoom_map
        box = pygame.Rect(x, y, s, s)
        pygame.draw.rect(screen, (0, 200, 255), box)
        fonte = pygame.font.SysFont(None, 12)
        text = fonte.render(f"{self.name}", True, (255, 255, 255))
        screen.blit(text, (x, y))

        # Hp
        box = pygame.Rect(10, 10, int(self.hp), 20)
        pygame.draw.rect(screen, (255, 100, 100), box)
        fonte = pygame.font.SysFont(None, 30)
        text = fonte.render(f"{self.hp}/{self.max_hp}", True, (0, 0, 0))
        screen.blit(text, (20, 10))

        # keys
        for index, key in enumerate(["q", "e", "space"]):
            box = pygame.Rect(self.max_hp + 20, 10 + index*7, int(self.times[key]), 6)
            pygame.draw.rect(screen, (150, 200, 100), box)
            self.times[key] = min(self.times[key] + 1, self.times[f"max_{key}"])

#######################################################################################
weapons:dict[dict] = {}

#######################################################################################
characters:dict[dict] = {"mage":{"name":"Mage",
                                 "hp":100, # base
                                 "speed":0.03, # pixel per frame
                                 "aceleration":0.005,
                                 "q":None,
                                 "e":None,
                                 "space":None,
                                 "q_time":30,
                                 "e_time":120,
                                 "space_time":1200,
                                 "size":0.2},
                         "archer":{"name":"Archer",
                                   "hp":100, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.01,
                                   "q":None,
                                   "e":None,
                                   "space":None,
                                   "q_time":30,
                                   "e_time":120,
                                   "space_time":1200,
                                   "size":0.2}, # 
                        }