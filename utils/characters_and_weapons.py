# Others:
import pygame
import math
from random import random, randint

zoom_map:list[int] = [100]
W, H = 1600, 900

#######################################################################################
class BaseEntity:
    def __init__(self, name:str, hp:float, speed:float, aceleration:float, size:float, weapon,
                 q = None, e = None, space = None, q_time:int = 120, e_time:int = 30, space_time:int = 1200,
                 frame:str = None, pos:list[float] = [5, 5], colision:bool = False, 
                 player:bool = False, enemy:bool = False, enemy_movement = None, enemy_atk = None,
                 level:int = 0, exp:int = 0, coin:int = 0,
                 die = None) -> None:
        self._id:str = f"{randint(0, 999_999_999):09}"
        self._space_inventory:tuple[int] = (6, 4)
        self.inventory:list = [None for i in range(self._space_inventory[0] * self._space_inventory[1])]
        self._in_invetory:bool = False
        self._time_in_inventory:int = 0
        self._positions_box:list[tuple] = [(int(W/20 + W/(self._space_inventory[0]) * i), int(H/3 + H/(self._space_inventory[1] + 2) * j)) for i in range(self._space_inventory[0]) for j in range(self._space_inventory[1])]

        # Atributes
        self.name:str = name
        self.max_hp:float = int(hp*1.1**level)
        self.hp:float = self.max_hp
        self.speed:float = speed
        self.aceleration:float = aceleration
        self.size:float = size
        self.player:bool = player
        self.enemy:bool = enemy
        self.colision:bool = colision
        self.alive:bool = True
        self.level:int = level
        self.exp:int = exp
        self.coin:int = coin
        self.next_level = int(100*1.5**self.level)
        
        if (die != None) and type(die) != list:
            die = [die]
        self.die = die

        # Position
        self.pos:list[float] = pos
        self.pos_aceleration:list[float] = [0, 0]
        self.enemy_movement = enemy_movement
        self.enemy_atk = enemy_atk

        # Actions
        self.weapon = weapon
        self.iten = None
        self.put_weapon()
        self.next_action:str = None
        self._lmb_prev:bool = False  # left botton mouse
        self.last_click_world:list = None

        # Frames
        self.frame:str = frame
        self.last_position_mouse:tuple = (0, 0)

    def put_weapon(self, weapon = None) -> None:
        if weapon != None:
            self.weapon = weapon
        self.times:dict = {key:self.weapon.times[key] if key not in ["q", "e", "space"] else 0 for key in ["q", "e", "space", "max_q", "max_e", "max_space"]}
        self.functions:dict = {key:self.weapon.functions[key] for key in ["q", "e", "space"]}
        self.keyargs:dict = {key:self.weapon.keyargs[key] for key in ["q", "e", "space"]}

    def put_in_inventory(self, obj) -> None:
        if None in self.inventory:
            self.inventory.remove(None)
            self.inventory.append(obj)

    def action(self, colliders:list, main_pos:list[float], actions:list, player) -> None:
        # Level
        if self.exp > self.next_level:
            self.coin += 50
            self.next_level = int(100*1.5**self.level)
            self.level += 1
            self.level = min(self.level, 50)
            self.max_hp:int = int(self.max_hp*1.1)
            self.hp:int = int(self.max_hp)

        # movement
        if self.hp <= 0:
            self.alive:bool = False
            return None

        self.pos_aceleration[0] *= 0.9
        self.pos_aceleration[1] *= 0.9

        if (self.player) or (self.enemy):
            self._time_in_inventory = (self._time_in_inventory + 1)%30_000

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
                if keys[pygame.K_i] and self._time_in_inventory > 20:
                    self._in_invetory = (self._in_invetory + 1) % 2
                    self._time_in_inventory:int = 0
                elif keys[pygame.K_m]:
                    zoom_map[0] = 10
                elif keys[pygame.K_n]:
                    zoom_map[0] = 30
                elif keys[pygame.K_b]:
                    zoom_map[0] = 100
                    

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

        if not self._in_invetory:
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
            if self._in_invetory:
                buttons = pygame.mouse.get_pressed(3)        # (L, M, R)
                lmb = bool(buttons[0])
                sx, sy = pygame.mouse.get_pos()

                if self.last_position_mouse != (sx, sy) or sum(buttons) > 0:
                    self.last_position_mouse:tuple = (sx, sy)

                    n:int = 0
                    select_n:int = None
                    while n < len(self.inventory):
                        #print(f"{n}: {euclidean(self._positions_box[n], [sx, sy]):0.02f}")
                        if euclidean(self._positions_box[n], [sx, sy]) < 100:
                            select_n:int = n
                            break
                        n += 1
                    #print(f"{select_n} selected")
                    #print(buttons)
                    if (bool(buttons[0]) == True) and (select_n != None):
                        if self.inventory[n] != None:
                            self.put_weapon(weapon = self.inventory[n])

            else:
                if (self.next_action != None) and (self.times[self.next_action] == self.times[f"max_{self.next_action}"]):
                    buttons = pygame.mouse.get_pressed(3)        # (L, M, R)
                    lmb = bool(buttons[0])
                    if lmb and (not self._lmb_prev):
                        sx, sy = pygame.mouse.get_pos()
                    
                        wx = main_pos[0] + sx/zoom_map[0]
                        wy = main_pos[1] + sy/zoom_map[0]
                        self.last_click_world = (wx, wy)
                        self.times[self.next_action] = 0
                        if self.functions[self.next_action] != None:
                            if self.next_action == "space": # Ability
                                temp_actions = self.functions[self.next_action](player = self, target = (wx, wy), colliders = colliders)
                            else: # Atack
                                temp_actions = self.functions[self.next_action](owner = self.pos, target = (wx, wy), _id = self._id, player = self, level = self.weapon.level)
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
                        temp_actions = self.functions[self.next_action](owner = self.pos, target = (wx, wy), _id = self._id, player = self, level = self.weapon.level)
                    if type(temp_actions) != list:
                        temp_actions:list = [temp_actions]
                    if temp_actions[0] != None:
                        actions.extend(temp_actions)
        
        if self.player or self.enemy:
            for key in ("q", "e", "space"):
                self.times[key] = min(self.times[key] + 1, self.times[f"max_{key}"])
            
    def plot(self, screen, main_pos:list[float]) -> None:
        # Entitie
        x, y, s = (self.pos[0]-main_pos[0])*zoom_map[0], (self.pos[1]-main_pos[1])*zoom_map[0], self.size*zoom_map[0]
        box = pygame.Rect(x, y, s, s)
        pygame.draw.rect(screen, (0, 200, 255), box)
        fonte = pygame.font.SysFont(None, 12)
        text = fonte.render(f"{self.name}", True, (255, 255, 255))
        screen.blit(text, (x, y))

        if self.player:
            # Hp
            box = pygame.Rect(10, 10, int(self.hp/self.max_hp * 100), 20)
            pygame.draw.rect(screen, (255, 100, 100), box)
            fonte = pygame.font.SysFont(None, 26)
            text = fonte.render(f"{int(self.hp)}/{self.max_hp}", True, (255, 255, 255))
            screen.blit(text, (10, 10))

            # keys
            for index, key in enumerate(["q", "e", "space"]):
                box = pygame.Rect(120, 10 + index*7, int(self.times[key]/self.times[f"max_{key}"]*50), 6)
                pygame.draw.rect(screen, (200, 200, 150) if key == self.next_action else (150, 200, 100), box)

            # Coin, exp and level
            fonte = pygame.font.SysFont(None, 20)
            coin = fonte.render(f"Coin: {self.coin}", True, (240, 215, 90))
            exp = fonte.render(f"Exp: {self.exp}/{self.next_level}", True, (180, 180, 255))
            screen.blit(coin, (W - 210, 60))
            screen.blit(exp, (W - 210, 10))

            box = pygame.Rect(W - 220, 30, 210, 20)
            pygame.draw.rect(screen, (110, 110, 200), box)
            box = pygame.Rect(W - 210, 30, int(self.exp/self.next_level*200), 20)
            pygame.draw.rect(screen, (140, 140, 240), box)
            level = fonte.render(f"Level: {self.level}", True, (255, 255, 255))
            screen.blit(level, (W - 160, 32))

            if self._in_invetory:
                fonte = pygame.font.SysFont(None, 32)
                small_fonte = pygame.font.SysFont(None, 20)
                for index, pos in enumerate(self._positions_box):

                    box = pygame.Rect(*pos, 70, 70)
                    if self.inventory[index] != None:
                        pygame.draw.rect(screen, (110, 110, 110), box)
                        text = small_fonte.render(f"{self.inventory[index].name}", True, (220, 220, 220))
                        screen.blit(text, pos)
                    else:
                        pygame.draw.rect(screen, (160, 160, 160), box)   


                    weapon = fonte.render(f"Weapon: {self.weapon.name}", True, (160, 160, 230))
                    screen.blit(weapon, (W/12*2, H/12))

                    weapon = fonte.render(f"Iten: {self.iten}", True, (160, 160, 230))
                    screen.blit(weapon, (W/12*2, H/12*2))


        else:
            box = pygame.Rect(x, y - 10, int(self.hp), 4)
            pygame.draw.rect(screen, (180, 80, 80), box)
            level = fonte.render(f"LV: {self.level}", True, (220, 190, 190))
            screen.blit(level, (x, y - 20))


#######################################################################################
class BaseAtk:
    def __init__(self, damage:int, speed:float, pos:list[float], pos_final:list[float], id:str, poison:int = None, size:float = 0.01, life_span:int = 10, 
                dead = None, dead_collision = None,
                coin:int = 0, exp:int = 0, weapon = None,
                level:int = 0) -> None:
        self._id:str = id
        self.level:int = level
        
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
        self.weapon = weapon

        # If coin
        self.coin:int = coin
        self.exp:int = exp

        # Normalized velocity
        dx = self.pos_final[0] - self.pos[0]
        dy = self.pos_final[1] - self.pos[1]
        n = math.hypot(dx, dy) or 1.0
        ux, uy = dx / n, dy / n
        self.vx = ux * self.speed
        self.vy = uy * self.speed

    def _reached_target(self) -> bool:
        if self.speed == 0:
            return False
        tx = self.pos_final[0] - self.pos[0]
        ty = self.pos_final[1] - self.pos[1]
        if (tx * tx + ty * ty) <= (self.speed * self.speed): # If the distance is small, consider that you have arrived
            return True
        return (tx * self.vx + ty * self.vy) <= 0.0 # If the movement in the opposite direction to the target, passed the point

    def action(self, colliders:list, actions:list, player) -> None:
        colliders = [*colliders, player]
        if not self.alive:
            if self.dead != None:
                temp_action = self.dead(self.pos, self.pos, _id = self._id, player = self, level = self.level)
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
                temp_action = self.dead(self.pos, self.pos, _id = self._id, player = self, level = self.level)
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

                # Coin and exp
                if hasattr(ent, "coin"):
                    ent.coin += self.coin
                if hasattr(ent, "exp"):
                    ent.exp += self.exp
                if hasattr(ent, "weapon") and self.weapon != None:
                    ent.put_in_inventory(self.weapon)

                # Aply damage
                if hasattr(ent, "hp"):
                    ent.hp = max(0, float(ent.hp) - self.damage)
                    if ent.hp <= 0 and hasattr(ent, "die"):
                        if ent.die != None:
                            for func in ent.die:
                                func(ent, colliders, actions, player)

                self.alive = False
                if self.dead_collision is not None:
                    temp_action = self.dead_collision(self.pos, self.pos, _id = self._id, player = self, level = self.level)
                    if type(temp_action) != list:
                        temp_action = [temp_action]
                    actions.extend(temp_action)
                break

    def plot(self, screen, main_pos:list[float]) -> None:
        if not self.alive:
            return

        x = int((self.pos[0] - main_pos[0]) * zoom_map[0])
        y = int((self.pos[1] - main_pos[1]) * zoom_map[0])
        s = int(self.size * zoom_map[0])
        pygame.draw.rect(screen, (255, 230, 120), pygame.Rect(x, y, s, s))

class BaseWeapon:
    def __init__(self, q, e, space, q_time, e_time, space_time, chance_of_drop:int = 0,
                 keyargs_q = None, keyargs_e = None, keyargs_space = None, name = "NO NAME", level:int = 1) -> None:
        self.name:str = name
        self.level:int = level
        self.chance_of_drop:float = chance_of_drop
        self.times:dict = {"q":q_time, "e":e_time, "space":space_time,
                           "max_q":q_time, "max_e":e_time, "max_space":space_time}
        self.functions:dict = {"q":q, "e":e, "space":space}
        self.keyargs:dict = {"q":keyargs_q, "e":keyargs_e, "space":keyargs_space}

class BaseIten:
    def __init__(self, name:str, pause:int, function) -> None:
        self.name:str = name
        self.pause:int = pause
        self.function = function
        self._tick_now:int = 0

        self.action()

    def action(self, player:BaseEntity):
        self._tick_now = (1+self._tick_now)%32_000
        if (self._tick_now % self.pause) == 0:
            self.function(player)

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

def enemy_movement_away(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> "str":
    if random() > 1/(euclidean(obj.pos, player.pos)+1) * 3:
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
        return ["q", "e", "space"][randint(0, 2)], [player.pos[0] + (random()-0.5)/5, player.pos[1] + (random()-0.5)/5]
    else:
        return None, None

def enemy_atk_precision(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> ("str", list[float]):
    if random() > 0.97:
        return ["q", "e", "space"][randint(0, 2)], [player.pos[0] + player.pos_aceleration[0]*2 + random(), player.pos[1] + player.pos_aceleration[1]*2 + random()]
    else:
        return None, None

def enemy_atk_agro(obj:[BaseEntity], colliders:list, main_pos:list[float], actions:list, player:BaseEntity) -> ("str", list[float]):
    if (random() > 0.95) and (euclidean(obj.pos, player.pos) < 1.2 + obj.size):
        return ["q", "e", "space"][randint(0, 2)], [player.pos[0], player.pos[1]]
    else:
        return None, None

#######################################################################################
def projectile_simple(owner, target, _id, damage:int = 20, speed:float = 0.25, size = 0.03, life_span = 25, player = None, level = 0):
    """More simple projectile"""
    target = [(target[0] - owner[0])/speed * life_span, (target[1] - owner[1])/speed * life_span]
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def fragmentation(owner, target, _id, damage:int = 25, speed:float = 0.07, size = 0.04, life_span = 20, player = None, level = 0):
    return [BaseAtk(damage = damage * 1.1**level, speed = speed, pos = [owner[0]+x/20, owner[1]+y/20], pos_final = [target[0] + x, target[1] + y],
                    size = size, life_span = life_span, id = _id) for x, y in ((-3, -3), (-3, 3), (3, -3), (3, 3), (3, 0), (0, 3), (-3, 0), (0, -3))]

def random_fragmentation(owner, target, _id, damage:int = 10, speed:float = 0.07, size = 0.04, life_span = 25, player = None, level = 0):
    return [BaseAtk(damage = damage * 1.1**level, speed = speed, pos = [owner[0]+x/20, owner[1]+y/20], pos_final = [target[0] + x, target[1] + y],
                    size = size, life_span = life_span, id = _id) for x, y in [[(random()-.5)*10, (random()-.5)*10] for _ in range(randint(3, 12))]]

def projectile_with_fragmentation(owner, target, _id, damage:int = 50, speed:float = 0.15, size = 0.06, life_span = 40, player = None, level = 0):
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, dead = fragmentation, dead_collision = None, id = _id, level = player.weapon.level)

def projectile_with__random_fragmentation(owner, target, _id, damage:int = 50, speed:float = 0.15, size = 0.06, life_span = 40, player = None, level = 0):
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, dead = random_fragmentation, dead_collision = None, id = _id, level = player.weapon.level)

def projectile_arrow(owner, target, _id, damage:int = 20, speed:float = 0.4, size = 0.03, life_span = 25, player = None, level = 0):
    target = [(target[0] - owner[0])/speed * life_span, (target[1] - owner[1])/speed * life_span]
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def projectile_around(owner, target, _id, damage:int = 30, speed:float = 0.04, size = 0.04, life_span = 40, player = None, level = 0):
    return [BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = [target[0] + x, target[1] + y], pos_final = [target[0], target[1]],
                    size = size, life_span = life_span, id = _id) for x, y in ((-1, -1), (-1, 1), (1, -1), (1, 1))]

def projectile_sword(owner, target, _id, damage:int = 40, speed:float = 0.04, size = 0.1, life_span = 15, player = None, level = 0):
    """Sword"""
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def projectile_large_sword(owner, target, _id, damage:int = 25, speed:float = 0.04, size = 0.1, life_span = 25, player = None, level = 0):
    """Sword"""
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
                   size = size, life_span = life_span, id = _id)

def chance_fragmentation(owner, target, _id, damage:int = 20, speed:float = 0.06, size = 0.04, life_span = 15, player = None, level = 0):
    times:int = randint(0, 2) if random() > 0.1 else 0
    if times > 0:
        temp_atk:list = []
        for i in range(times):
            temp_atk.append(BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = [owner[0], owner[1]],
                                    pos_final = [target[0] + (random()-0.5)*6, target[1] + (random()-0.5)*6],
                                    size = size, life_span = life_span, id = _id, dead = chance_fragmentation))
        return temp_atk
    else:
        return [BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = [owner[0]+x/20, owner[1]+y/20], pos_final = [target[0] + x, target[1] + y],
                            size = size, life_span = life_span, id = _id) for x, y in [[(random()-0.5)*6, (random()-0.5)*6]]]

def projectile_chance_fragmentation(owner, target, _id, damage:int = 25, speed:float = 0.15, size = 0.07, life_span = 30, player = None, level = 0):
    return BaseAtk(damage = damage * 1.1 ** level, speed = speed, pos = owner, pos_final = target,
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

#######################################################################################
def drop_coin_and_exp(owner, colliders, actions, player) -> None:
    drop_position:list = [owner.pos[0]+random()*owner.size*2-owner.size, owner.pos[1]*owner.size*2-owner.size]
    actions.append(BaseAtk(damage = 0, speed = 0, 
                            pos = [owner.pos[0]+(random()*owner.size*2-owner.size)*2, owner.pos[1]+(random()*owner.size*2-owner.size)*2],
                            pos_final = [owner.pos[0]+(random()*owner.size*2-owner.size)*2, owner.pos[1]+random()*(owner.size*2-owner.size)*2],
                            size = 0.1, life_span = 600, id = owner._id,
                            coin = owner.coin, exp = owner.exp))

def drop_weapon(owner, colliders, actions, player) -> None:
    if owner.weapon.chance_of_drop >= random():
        drop_position:list = [owner.pos[0]+random()*owner.size*2-owner.size, owner.pos[1]*owner.size*2-owner.size]
        actions.append(BaseAtk(damage = 0, speed = 0, 
                                pos = [owner.pos[0]+(random()*owner.size*2-owner.size)*2, owner.pos[1]+(random()*owner.size*2-owner.size)*2],
                                pos_final = [owner.pos[0]+(random()*owner.size*2-owner.size)*2, owner.pos[1]+random()*(owner.size*2-owner.size)*2],
                                size = 0.15, life_span = 1200, id = owner._id,
                                weapon = owner.weapon))

#######################################################################################
def iten_cure(player):
    player.hp = int(player.hp + player.max_hp)

#######################################################################################
weapons:dict[dict] = {"fire_staff":{"name":"Fire Staff",
                                    "chance_of_drop":.1,
                                    "level":0,
                                    "q_time":120,
                                    "e_time":30,
                                    "space_time":450,
                                    "q":projectile_with_fragmentation,
                                    "e":projectile_simple,
                                    "space":ability_transportation,
                                    "iten":},
                      "simple_bow":{"name":"Simple Bow",
                                    "chance_of_drop":1,
                                    "level":0,
                                    "q_time":120,
                                    "e_time":25,
                                    "space_time":450,
                                    "q":None,
                                    "e":projectile_arrow,
                                    "space":None},
                      "claw":{"name":"Claw",
                                    "chance_of_drop":0,
                                    "level":0,
                                    "q_time":35,
                                    "e_time":25,
                                    "space_time":450,
                                    "q":projectile_sword,
                                    "e":projectile_large_sword,
                                    "space":None},
                       "random_staff":{"name":"Random Staff",
                                    "chance_of_drop":.05,
                                    "level":30,
                                    "q_time":60,
                                    "e_time":60,
                                    "space_time":450,
                                    "q":projectile_chance_fragmentation,
                                    "e":projectile_with__random_fragmentation,
                                    "space":None},
                     }

itens:dict["dict"] = {"ring_of_cure":{"name":"Ring of Cure",
                                      "pause":30,
                                      "function":iten_cure}}

#######################################################################################
characters:dict[dict] = {"mage":{"name":"Mage",
                                 "hp":100, # base
                                 "speed":0.03, # pixel per frame
                                 "aceleration":0.005,
                                 "weapon":BaseWeapon(**weapons["fire_staff"].copy()),
                                 "iten":BaseIten(*itens["ring_of_cure"]),
                                 "size":0.25,
                                 "enemy_movement":enemy_movement_away,
                                 "enemy_atk":enemy_atk_simple,
                                 "die":[drop_coin_and_exp, drop_weapon]},
                         "archer":{"name":"Archer",
                                   "hp":120, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.01,
                                   "weapon":BaseWeapon(**weapons["simple_bow"].copy()),
                                   "size":0.3,
                                   "enemy_movement":enemy_movement_away,
                                   "enemy_atk":enemy_atk_precision,
                                   "die":[drop_coin_and_exp, drop_weapon]},
                         "slime":{"name":"Slime",
                                   "hp":30, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.003,
                                   "weapon":BaseWeapon(**weapons["claw"].copy()),
                                   "size":0.3,
                                   "enemy_movement":enemy_movement_agro,
                                   "enemy_atk":enemy_atk_agro,
                                   "die":[drop_coin_and_exp, drop_weapon]},
                            "wolf":{"name":"Wolf",
                                   "hp":70, # base
                                   "speed":0.04, # pixel per frame
                                   "aceleration":0.007,
                                   "weapon":BaseWeapon(**weapons["claw"].copy()),
                                   "size":0.4,
                                   "enemy_movement":enemy_movement_agro,
                                   "enemy_atk":enemy_atk_agro,
                                   "die":[drop_coin_and_exp, drop_weapon]},
                         "the_randonnes":{"name":"The randonnes",
                                 "level":30,
                                 "hp":200, # base
                                 "speed":0.03, # pixel per frame
                                 "aceleration":0.005,
                                 "weapon":BaseWeapon(**weapons["random_staff"].copy()),
                                 "size":0.5,
                                 "enemy_movement":enemy_movement_away,
                                 "enemy_atk":enemy_atk_simple,
                                 "die":[drop_coin_and_exp, drop_weapon]},
                            }