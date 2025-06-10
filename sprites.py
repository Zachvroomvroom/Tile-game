import pygame as pg
from tilemap import collide_hit_rect

from settings import *
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if sprite.vel.x < 0:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if sprite.vel.y < 0:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((10,10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir.rotate(0)*BULLET_SPEED

        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel*self.game.dt
        self.rect.center = self.pos
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME*1000:
            self.kill()
        if pg.sprite.spritecollideany(self,self.game.walls):
            self.kill()


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("Player.png")
        self.image = pg.transform.rotate(self.image,90)
        self.image = pg.transform.scale(self.image, (48*TILESIZE//32, 32*TILESIZE//32))
        self.rect = self.image.get_rect()
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(YELLOW)
        self.player_img = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.last_shot = 0
        self.vx, self.vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.vel = vec(0,0)
        self.pos = vec(x,y)*TILESIZE
        self.rot = 0
        # self.Pcol = self.x//TILESIZE
        # self.Prow = self.y//TILESIZE
        # self.rot_speed = PLAYER_ROT_SPEED

        self.health = PLAYER_HEALTH

    def get_keys(self):
        self.rot_speed=0
        keys = pg.key.get_pressed()
        self.vel = vec(0,0)
        self.vx, self.vy = 0, 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = +PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED,0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED,0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now-self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1,0).rotate(-self.rot)
                pos= self.pos+BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game,pos,dir)
                self.vel = vec(-BULLET_RECOIL, 0).rotate(-self.rot)


    def update(self):
        self.get_keys()
        self.rot = (self.rot+self.rot_speed*self.game.dt)%360
        self.image = pg.transform.rotate(self.player_img,self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel*self.game.dt
        # self.x += self.vx * self.game.dt
        # self.y += self.vy * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self,self.game.walls,'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self,self.game.walls,'y')
        self.rect.center = self.hit_rect.center


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load("Enemy_Turret.png")
        self.image = pg.transform.rotate(self.image, 90)
        self.image = pg.transform.scale(self.image, (32 * TILESIZE // 32, 32 * TILESIZE // 32))
        self.rect = self.image.get_rect()
        self.mob_img = self.image.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x,y)*TILESIZE
        # self.vx, self.vy = 0, 0
        # self.rect.center = self.pos
        self.rot = 0
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.rect.center = self.pos
        # self.x = x * TILESIZE
        # self.y = y * TILESIZE

        self.health = MOB_HEALTH

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0,0,width,7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image,col,self.health_bar)

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1,0))
        self.image = pg.transform.rotate(self.mob_img,self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(MOB_SPEED,0).rotate(-self.rot)

        self.acc = vec(1,0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(MOB_SPEED)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + .5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y
        # self.x += self.vx * self.game.dt
        # self.y += self.vy * self.game.dt
        collide_with_walls(self,self.game.walls,'x')
        collide_with_walls(self,self.game.walls,'y')
        if self.health <= 0:
            self.kill()
        self.rect.center = self.hit_rect.center


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, version):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(GREEN)
        if version == 1:
            self.image = pg.image.load("Wall_Sprites/Wall_Forward.png")
        if version == 2:
            self.image = pg.image.load("Wall_Sprites/Wall_Up.png")
        self.image = pg.transform.scale(self.image,(TILESIZE,TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE