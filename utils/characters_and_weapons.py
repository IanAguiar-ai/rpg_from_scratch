# Others:
import pygame
import math

zoom_map:int = 100

######################################################################################
def _aabb_overlap(ax:float, ay:float, asize:float, bx:float, by:float, bsize:float) -> bool:
    """Retorna True se [ax,ay,asize] colide com [bx,by,bsize] (quadrados AABB)."""
    return (ax < bx + bsize and ax + asize > bx and ay < by + bsize and ay + asize > by)

#######################################################################################
class BaseEntity:
    def __init__(self, name:str, hp:float, speed:float, aceleration:float, size:float, q, e, space, q_time:int, e_time:int, space_time:int, frame:str = None, pos:list[float] = [5, 5]) -> None:

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
        self.times:dict = {"q":q_time, "e":e_time, "space":space_time,
                           "max_q":q_time, "max_e":e_time, "max_space":space_time}
        self.functions:dict = {"q":q, "e":e, "space":space}
        self.next_action:str = None
        self._lmb_prev:bool = False  # left botton mouse
        self.last_click_world:list = None

        # Frames
        self.frame:str = frame

    def action(self, colliders:list, main_pos:list[float], actions:list) -> None:
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
                if self.functions[self.next_action] != None:
                    if self.next_action == "space": # Ability
                        temp_actions = self.functions[self.next_action](player = self, target = (wx, wy))
                    else: # Atack
                        temp_actions = self.functions[self.next_action](owner = self.pos, target = (wx, wy))
                    if type(temp_actions) != list:
                        temp_actions:list = [temp_actions]
                    if temp_actions[0] != None:
                        actions.extend(temp_actions)
                #self.next_action:str = None

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
            box = pygame.Rect(self.max_hp + 20, 10 + index*7, int(self.times[key]/self.times[f"max_{key}"]*50), 6)
            pygame.draw.rect(screen, (200, 200, 150) if key == self.next_action else (150, 200, 100), box)
            self.times[key] = min(self.times[key] + 1, self.times[f"max_{key}"])

#######################################################################################
class BaseAtk:
    def __init__(self, damage:int, speed:float, pos:list[float], pos_final:list[float], poison:int = None, size:float = 0.01, life_span:int = 10, dead = None, dead_collision = None) -> None:
        self.damage:int = damage
        self.speed:float = speed
        self.poison:int = poison
        self.pos_final:list[float] = pos_final
        self.pos = pos.copy()
        self.size:float = size
        self.life_span:int = life_span
        self.alive:bool = True
        self.dead = dead
        self.dead_collision = dead_collision

        # Normalized velocity
        dx = self.pos_final[0] - self.pos[0]
        dy = self.pos_final[1] - self.pos[1]
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        self.vx = ux * self.speed
        self.vy = uy * self.speed

    def _reached_target(self) -> bool:
        tx = self.pos_final[0] - self.pos[0]
        ty = self.pos_final[1] - self.pos[1]
        if (tx * tx + ty * ty) <= (self.speed * self.speed): # If the distance is small, consider that you have arrived
            return True
        return (tx * self.vx + ty * self.vy) <= 0.0 # If the movement in the opposite direction to the target, passed the point

    def action(self, colliders:list, actions:list) -> None:
        if not self.alive:
            if self.dead != None:
                temp_action = self.dead(self.pos, self.pos)
                if type(temp_action) != list:
                    temp_action:list = [temp_action]
                actions.extend(temp_action)
            return

        self.pos[0] += self.vx
        self.pos[1] += self.vy

        self.life_span -= 1
        if self.life_span <= 0 or self._reached_target():
            self.alive = False
            if self.dead != None:
                temp_action = self.dead(self.pos, self.pos)
                if type(temp_action) != list:
                    temp_action:list = [temp_action]
                actions.extend(temp_action)
            return

        for ent in colliders:
            if getattr(ent, "colision", False):
                if _aabb_overlap(self.pos[0], self.pos[1], self.size,
                                 ent.pos[0], ent.pos[1], ent.size):
                    # aplicar dano se tiver hp
                    if hasattr(ent, "hp"):
                        ent.hp = max(0, float(ent.hp) - self.damage)
                        if ent.hp <= 0 and hasattr(ent, "die"):
                            try:
                                ent.die()
                            except Exception:
                                pass

                    self.alive = False
                    if self.dead_collision != None:
                        temp_action = self.dead_collision(self.pos, self.pos)
                        if type(temp_action) != list:
                           temp_action:list = [temp_action]
                        actions.extend(temp_action)
                    break


    def plot(self, screen, main_pos:list[float]) -> None:
        if not self.alive:
            return

        x = int((self.pos[0] - main_pos[0]) * zoom_map)
        y = int((self.pos[1] - main_pos[1]) * zoom_map)
        s = int(self.size * zoom_map)
        pygame.draw.rect(screen, (255, 230, 120), pygame.Rect(x, y, s, s))

class BaseWeapon:
    pass


#######################################################################################
def simple_projectile(owner, target, damage:int = 20, speed:float = 0.25, size = 0.03, life_span = 25, player = None):
    """More simple projectile"""
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span)

def fragmentation(owner, target, damage:int = 25, speed:float = 0.07, size = 0.04, life_span = 20, player = None):
    return [BaseAtk(damage = damage, speed = speed, pos = [owner[0]+x/20, owner[1]+y/20], pos_final = [target[0] + x, target[1] + y],
                    size = size, life_span = life_span) for x, y in ((-3, -3), (-3, 3), (3, -3), (3, 3), (3, 0), (0, 3), (-3, 0), (0, -3))]

def projectile_with_fragmentation(owner, target, damage:int = 50, speed:float = 0.15, size = 0.06, life_span = 40, player = None):
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, dead = fragmentation, dead_collision = None)

def ability_transportation(player:BaseEntity, target:list[float]):
    player.pos = [target[0], target[1]]

weapons:dict[dict] = {}

#######################################################################################
characters:dict[dict] = {"mage":{"name":"Mage",
                                 "hp":100, # base
                                 "speed":0.03, # pixel per frame
                                 "aceleration":0.005,
                                 "q":projectile_with_fragmentation,
                                 "e":simple_projectile,
                                 "space":ability_transportation,
                                 "q_time":120,
                                 "e_time":30,
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