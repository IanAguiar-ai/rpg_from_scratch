# Others:
import pygame
import math
from random import random, randint

zoom_map:int = 100

#######################################################################################
class BaseEntity:
    def __init__(self, name:str, hp:float, speed:float, aceleration:float, size:float,
                 q = None, e = None, space = None, q_time:int = 120, e_time:int = 30, space_time:int = 1200,
                 frame:str = None, pos:list[float] = [5, 5], colision:bool = False, 
                 player:bool = False, enemy:bool = False, enemy_movement = None, enemy_atk = None) -> None:
        self._id:str = f"{randint(0, 999_999_999):09}"

        # Atributes
        self.name:str = name
        self.hp:float = hp
        self.max_hp:float = hp
        self.speed:float = speed
        self.aceleration:float = aceleration
        self.size:float = size
        self.player:bool = player
        self.enemy:bool = enemy
        self.colision:bool = colision
        self.alive:bool = True

        # Position
        self.pos:list[float] = pos
        self.pos_aceleration:list[float] = [0, 0]
        self.enemy_movement = enemy_movement
        self.enemy_atk = enemy_atk

        # Actions
        self.times:dict = {"q":q_time, "e":e_time, "space":space_time,
                           "max_q":q_time, "max_e":e_time, "max_space":space_time}
        self.functions:dict = {"q":q, "e":e, "space":space}
        self.next_action:str = None
        self._lmb_prev:bool = False  # left botton mouse
        self.last_click_world:list = None

        # Frames
        self.frame:str = frame

    def action(self, colliders:list, main_pos:list[float], actions:list, player) -> None:
        # movement
        if self.hp <= 0:
            self.alive:bool = False
            return None

        self.pos_aceleration[0] *= 0.9
        self.pos_aceleration[1] *= 0.9

        if (self.player) or (self.enemy):
            if self.player:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    self.pos_aceleration[0] -= self.aceleration
                if keys[pygame.K_d]:
                    self.pos_aceleration[0] += self.aceleration
                if keys[pygame.K_w]:
                    self.pos_aceleration[1] -= self.aceleration
                if keys[pygame.K_s]:
                    self.pos_aceleration[1] += self.aceleration

            elif self.enemy:
                key_enemy:str = self.enemy_movement(self, colliders, main_pos, actions, player)
                if key_enemy == "a":
                    self.pos_aceleration[0] -= self.aceleration
                if key_enemy == "d":
                    self.pos_aceleration[0] += self.aceleration
                if key_enemy == "w":
                    self.pos_aceleration[1] -= self.aceleration
                if key_enemy == "s":
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

        # Inside a object
        for _ in range(1):  # Iterations to push
            pushed = False
            for ent in colliders:
                if not getattr(ent, "colision", False):
                    continue

                # testa overlap atual
                if _aabb_overlap(self.pos[0], self.pos[1], self.size,
                                ent.pos[0], ent.pos[1], ent.size):
                    # centros
                    acx = self.pos[0] + self.size * 0.5
                    acy = self.pos[1] + self.size * 0.5
                    bcx = ent.pos[0] + ent.size * 0.5
                    bcy = ent.pos[1] + ent.size * 0.5

                    # diferencas de centro
                    dx = acx - bcx
                    dy = acy - bcy

                    # quanto esta "enfiado" em cada eixo
                    overlap_x = (self.size * 0.5 + ent.size * 0.5) - abs(dx)
                    overlap_y = (self.size * 0.5 + ent.size * 0.5) - abs(dy)

                    if overlap_x > 0 and overlap_y > 0:
                        if overlap_x < overlap_y:
                            # empurra no eixo X, para fora do centro do collider
                            shift = overlap_x if dx > 0 else -overlap_x
                            self.pos[0] += shift
                            self.pos_aceleration[0] = 0.0
                        else:
                            # empurra no eixo Y
                            shift = overlap_y if dy > 0 else -overlap_y
                            self.pos[1] += shift
                            self.pos_aceleration[1] = 0.0
                        pushed = True
            if not pushed:
                break

        if self.player:
            # Actions
            if keys[pygame.K_q]:
                self.next_action:str = "q"
            elif keys[pygame.K_e]:
                self.next_action:str = "e"
            elif keys[pygame.K_SPACE]:
                self.next_action:str = "space"

            # Mouse
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
                            temp_actions = self.functions[self.next_action](player = self, target = (wx, wy), colliders = colliders)
                        else: # Atack
                            temp_actions = self.functions[self.next_action](owner = self.pos, target = (wx, wy), _id = self._id)
                        if type(temp_actions) != list:
                            temp_actions:list = [temp_actions]
                        if temp_actions[0] != None:
                            actions.extend(temp_actions)
                    #self.next_action:str = None

                self._lmb_prev = lmb
        elif self.enemy:
             # Actions
            self.next_action, mouse_pos = self.enemy_atk(self, colliders, main_pos, actions, player)

            # Mouse
            if (self.next_action != None) and (self.times[self.next_action] == self.times[f"max_{self.next_action}"]):
                #print(self.next_action, mouse_pos)
                wx, wy = mouse_pos[0], mouse_pos[1]
                self.last_click_world = (wx, wy)
                self.times[self.next_action] = 0
                if self.functions[self.next_action] != None:
                    if self.next_action == "space": # Ability
                        temp_actions = self.functions[self.next_action](player = self, target = (wx, wy), colliders = colliders)
                    else: # Atack
                        temp_actions = self.functions[self.next_action](owner = self.pos, target = (wx, wy), _id = self._id)
                    if type(temp_actions) != list:
                        temp_actions:list = [temp_actions]
                    if temp_actions[0] != None:
                        actions.extend(temp_actions)
        
        if self.player or self.enemy:
            for key in ("q", "e", "space"):
                self.times[key] = min(self.times[key] + 1, self.times[f"max_{key}"])
            
    def plot(self, screen, main_pos:list[float]) -> None:
        # Entitie
        x, y, s = (self.pos[0]-main_pos[0])*zoom_map, (self.pos[1]-main_pos[1])*zoom_map, self.size*zoom_map
        box = pygame.Rect(x, y, s, s)
        pygame.draw.rect(screen, (0, 200, 255), box)
        fonte = pygame.font.SysFont(None, 12)
        text = fonte.render(f"{self.name}", True, (255, 255, 255))
        screen.blit(text, (x, y))

        if self.player:
            # Hp
            box = pygame.Rect(10, 10, int(self.hp/self.max_hp * 100), 20)
            pygame.draw.rect(screen, (255, 100, 100), box)
            fonte = pygame.font.SysFont(None, 30)
            text = fonte.render(f"{int(self.hp)}/{self.max_hp}", True, (255, 255, 255))
            screen.blit(text, (20, 10))

            # keys
            for index, key in enumerate(["q", "e", "space"]):
                box = pygame.Rect(self.max_hp + 20, 10 + index*7, int(self.times[key]/self.times[f"max_{key}"]*50), 6)
                pygame.draw.rect(screen, (200, 200, 150) if key == self.next_action else (150, 200, 100), box)
        else:
            box = pygame.Rect(x, y - 10, int(self.hp), 4)
            pygame.draw.rect(screen, (180, 80, 80), box)


#######################################################################################
class BaseAtk:
    def __init__(self, damage:int, speed:float, pos:list[float], pos_final:list[float], id:str, poison:int = None, size:float = 0.01, life_span:int = 10, 
                dead = None, dead_collision = None) -> None:
        self._id:str = id
        
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

    def action(self, colliders:list, actions:list, player) -> None:
        colliders = [*colliders, player]
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
        if self.life_span <= 0 or (self._reached_target()):
            self.alive = False
            if self.dead != None:
                temp_action = self.dead(self.pos, self.pos, _id = self._id)
                if type(temp_action) != list:
                    temp_action:list = [temp_action]
                actions.extend(temp_action)
            return

        for ent in colliders:
            if not getattr(ent, "colision", False):
                continue
            # Ignore the owner of projectile
            if hasattr(ent, "_id") and ent._id == self._id:
                continue

            if _aabb_overlap(self.pos[0], self.pos[1], self.size,
                            ent.pos[0], ent.pos[1], ent.size):
                # Aply damage
                if hasattr(ent, "hp"):
                    ent.hp = max(0, float(ent.hp) - self.damage)
                    if ent.hp <= 0 and hasattr(ent, "die"):
                        try: ent.die()
                        except Exception: pass

                self.alive = False
                if self.dead_collision is not None:
                    temp_action = self.dead_collision(self.pos, self.pos)
                    if type(temp_action) != list:
                        temp_action = [temp_action]
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

######################################################################################
def _aabb_overlap(ax:float, ay:float, asize:float, bx:float, by:float, bsize:float) -> bool:
    """Retorna True se [ax,ay,asize] colide com [bx,by,bsize] (quadrados AABB)."""
    return (ax < bx + bsize and ax + asize > bx and ay < by + bsize and ay + asize > by)

def euclidean(p1, p2) -> float:
    return ((p1[0] - p2[0])*(p1[0] - p2[0]) + (p1[1] - p2[1])*(p1[1] - p2[1]))**(0.5)

def enemy_movement_simple(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> "str":
    if random() > 1/(euclidean(obj.pos, player.pos)+1):
        if abs(obj.pos[0] - player.pos[0]) > abs(obj.pos[1] - player.pos[1]):
            if obj.pos[0] - player.pos[0] < -1:
                return "d"
            elif obj.pos[0] - player.pos[0] >= +1:
                return "a"
        else:
            if obj.pos[1] - player.pos[1] < -1:
                return "s"
            elif obj.pos[1] - player.pos[1] >= +1:
                return "w"

def enemy_movement_agro(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> "str":
    if random() > 1/(euclidean(obj.pos, player.pos)+1):
        if abs(obj.pos[0] - player.pos[0]) > abs(obj.pos[1] - player.pos[1]):
            if obj.pos[0] - player.pos[0] < -(.4 + obj.size):
                return "d"
            elif obj.pos[0] - player.pos[0] >= .4 + obj.size:
                return "a"
        else:
            if obj.pos[1] - player.pos[1] < -(.4 + obj.size):
                return "s"
            elif obj.pos[1] - player.pos[1] >= .4 + obj.size:
                return "w"

######################################################################################
def enemy_atk_simple(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> ("str", list[float]):
    if random() > 0.97:
        return ["q", "e", "space"][randint(0, 2)], [player.pos[0], player.pos[1]]
    else:
        return None, None

def enemy_atk_agro(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> ("str", list[float]):
    if (random() > 0.95) and (euclidean(obj.pos, player.pos) < 1.2 + obj.size):
        return ["q", "e", "space"][randint(0, 2)], [player.pos[0], player.pos[1]]
    else:
        return None, None

#######################################################################################
def projectile_simple(owner, target, _id, damage:int = 20, speed:float = 0.25, size = 0.03, life_span = 25, player = None):
    """More simple projectile"""
    target = [(target[0] - owner[0])/speed * life_span, (target[1] - owner[1])/speed * life_span]
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def fragmentation(owner, target, _id, damage:int = 25, speed:float = 0.07, size = 0.04, life_span = 20, player = None):
    return [BaseAtk(damage = damage, speed = speed, pos = [owner[0]+x/20, owner[1]+y/20], pos_final = [target[0] + x, target[1] + y],
                    size = size, life_span = life_span, id = _id) for x, y in ((-3, -3), (-3, 3), (3, -3), (3, 3), (3, 0), (0, 3), (-3, 0), (0, -3))]

def projectile_with_fragmentation(owner, target, _id, damage:int = 50, speed:float = 0.15, size = 0.06, life_span = 40, player = None):
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, dead = fragmentation, dead_collision = None, id = _id)

def projectile_arrow(owner, target, _id, damage:int = 20, speed:float = 0.4, size = 0.03, life_span = 25, player = None):
    target = [(target[0] - owner[0])/speed * life_span, (target[1] - owner[1])/speed * life_span]
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def projectile_around(owner, target, _id, damage:int = 30, speed:float = 0.04, size = 0.04, life_span = 40, player = None):
    return [BaseAtk(damage = damage, speed = speed, pos = [target[0] + x, target[1] + y], pos_final = [target[0], target[1]],
                    size = size, life_span = life_span, id = _id) for x, y in ((-1, -1), (-1, 1), (1, -1), (1, 1))]

def projectile_sword(owner, target, _id, damage:int = 40, speed:float = 0.04, size = 0.1, life_span = 15, player = None):
    """Sword"""
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def projectile_large_sword(owner, target, _id, damage:int = 20, speed:float = 0.04, size = 0.1, life_span = 25, player = None):
    """Sword"""
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def chance_fragmentation(owner, target, _id, damage:int = 15, speed:float = 0.06, size = 0.04, life_span = 15, player = None):
    times:int = randint(0, 2) if random() > 0.1 else 0
    if times > 0:
        temp_atk:list = []
        for i in range(times):
            temp_atk.append(BaseAtk(damage = damage, speed = speed, pos = [owner[0], owner[1]],
                                    pos_final = [target[0] + (random()-0.5)*6, target[1] + (random()-0.5)*6],
                                    size = size, life_span = life_span, id = _id, dead = chance_fragmentation))
        return temp_atk
    else:
        return [BaseAtk(damage = damage, speed = speed, pos = [owner[0]+x/20, owner[1]+y/20], pos_final = [target[0] + x, target[1] + y],
                            size = size, life_span = life_span, id = _id) for x, y in [[(random()-0.5)*6, (random()-0.5)*6]]]

def projectile_chance_fragmentation(owner, target, _id, damage:int = 30, speed:float = 0.15, size = 0.07, life_span = 30, player = None):
    return BaseAtk(damage = damage, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, dead = chance_fragmentation, dead_collision = None, id = _id)


#######################################################################################
def ability_transportation(player:BaseEntity, target:list[float], colliders:list = None):
    player.pos = [target[0], target[1]]

def ability_create_barrier(player:BaseEntity, target:list[float], colliders:list = None):
    colliders.append(BaseEntity(name = "Wall", hp = 50, speed = 0, aceleration = 0, size = 0.5, pos = [target[0], target[1]], colision = True))

def ability_create_barries(player:BaseEntity, target:list[float], colliders:list = None):
    colliders.extend([BaseEntity(name = "Wall", hp = 15, speed = 0, aceleration = 0, size = 0.25, pos = [player.pos[0] + x, player.pos[1] + y], colision = True) for x, y in ((-.7, -.7), (-.7, .7), (.7, -.7), (.7, .7))])

def ability_cure(player:BaseEntity, target:list[float], colliders:list = None):
    player.hp = min(int(player.hp + player.max_hp*.2), player.max_hp)

weapons:dict[dict] = {}

#######################################################################################
characters:dict[dict] = {"mage":{"name":"Mage",
                                 "hp":100, # base
                                 "speed":0.03, # pixel per frame
                                 "aceleration":0.005,
                                 "q":projectile_with_fragmentation,
                                 "e":projectile_simple,
                                 "space":ability_create_barrier,#ability_transportation,
                                 "q_time":120,
                                 "e_time":30,
                                 "space_time":450,
                                 "size":0.25,
                                 "enemy_movement":enemy_movement_simple,
                                 "enemy_atk":enemy_atk_simple},
                         "archer":{"name":"Archer",
                                   "hp":120, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.01,
                                   "q":projectile_around,
                                   "e":projectile_arrow,
                                   "space":ability_create_barries,
                                   "q_time":150,
                                   "e_time":30,
                                   "space_time":1200,
                                   "size":0.3,
                                   "enemy_movement":enemy_movement_simple,
                                   "enemy_atk":enemy_atk_simple},
                         "slime":{"name":"Slime",
                                   "hp":30, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.003,
                                   "q":projectile_large_sword,
                                   "e":projectile_large_sword,
                                   "space":None,
                                   "q_time":30,
                                   "e_time":30,
                                   "space_time":30,
                                   "size":0.3,
                                   "enemy_movement":enemy_movement_agro,
                                   "enemy_atk":enemy_atk_agro},
                            "wolf":{"name":"Wolf",
                                   "hp":70, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.007,
                                   "q":projectile_large_sword,
                                   "e":projectile_large_sword,
                                   "space":None,
                                   "q_time":45,
                                   "e_time":45,
                                   "space_time":1200,
                                   "size":0.4,
                                   "enemy_movement":enemy_movement_agro,
                                   "enemy_atk":enemy_atk_agro},
                            }