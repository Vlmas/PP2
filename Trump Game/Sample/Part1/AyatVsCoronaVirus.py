import pygame
import random

pygame.init()

size = (800,640)
window = pygame.display.set_mode(size)
pygame.display.set_caption("AyatVsCoronavirus")
fps = pygame.time.Clock()
hp_sur = pygame.Surface((100,20))
hp_shrift = pygame.font.Font(None, 40)
tukirik = pygame.image.load("ket.png")

bug = pygame.image.load("backg.png")
sound = pygame.mixer.Sound("Sound_20992.wav")

class Player(object):
    def __init__ (self):
        self.x = 800/2 - 32
        self.y = 640 - 40
        self.size = 32
        self.vel = 10
        self.hitbox = pygame.Rect(self.x,self.y,self.size,self.size)
        self.hp = 5

    def move(self,left=False,right=False):
        if left:
            self.hitbox = pygame.Rect(self.x-self.vel,self.y,self.size,self.size)
            self.x -= self.vel
        elif right:
            self.hitbox = pygame.Rect(self.x+self.vel,self.y,self.size,self.size)
            self.x += self.vel

    def check(self):
        if self.hp <= 0:
            run = False
            window.blit(bug,(0,0))
            pygame.mixer.Sound.play(sound)
            pygame.mixer.music.stop()

    def draw(self):
        pygame.draw.rect(window, (23,25,123),(self.x,self.y,self.size,self.size))

class Enemy(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.size = 32
        self.vel = 10
        self.hitbox = pygame.Rect(self.x,self.y,self.size,self.size)

    def move(self):
        if self.x < 0 or self.x > 800-32:
            self.vel*=(-1)
        self.hitbox = pygame.Rect(self.x+self.vel,self.y,self.size,self.size)
        self.x += self.vel

    def draw(self):
        pygame.draw.rect(window, (23,25,123),(self.x,self.y,self.size,self.size))

class Bullet(object):
    def __init__(self,hero):
        self.x = -100
        self.y = -100
        self.size = 10
        self.vel = 20
        self.shot = False
        self.hero = hero
        self.hitbox = pygame.Rect(self.x,self.y,self.size,self.size)
        self.hithero = False

    def shoot(self,x,y,size):
        if not(self.shot):
            self.x = round(size//2 + x)
            self.y = round(size//2 + y)
            self.shot = True

    def move(self):
        if self.shot:
            if self.hero:
                self.hitbox = pygame.Rect(self.x,self.y-self.vel,self.size,self.size)
                for f in enemy:
                    if self.hitbox.colliderect(f.hitbox):
                        enemy.remove(f)
                        self.x = -100
                        self.y = -100
                        self.shot = False
                        return
                if self.y <= 0:
                    self.x = -100
                    self.y = -100
                    self.shot = False
                    return
                self.y -=self.vel
            else:
                self.hitbox = pygame.Rect(self.x,self.y+self.vel,self.size,self.size)
                if self.hitbox.colliderect(hitbox):
                    self.hithero = True
                    self.x = -100
                    self.y = -100
                    self.shot = False
                    return
                if self.y >= 640:
                    self.x = -100
                    self.y = -100
                    self.shot = False
                    return
                self.y +=self.vel

    def check(self,hp):
        if self.hithero:
            self.hithero = False
            hp = int(hp)-1
            return hp
        else: return hp

    def draw(self):
        if self.hero:
            pygame.draw.circle(window, (255,255,255),(self.x,self.y), 5)
            window.blit(tukirik, (self.x,self.y))
        else:
            pygame.draw.circle(window, (255,0,0),(self.x,self.y), 5)

run = True
left = right = False
player1 = Player()
hitbox = player1.hitbox
bullethero = Bullet(True)
enemy = []
bulletenemy = []

for f in range(0,4):
    enemy.append(Enemy(random.randrange(1,80)*10,random.randrange(1,10)*10 ))
for f in range(0,4):
    bulletenemy.append(Bullet(False))

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                left = True
            elif event.key == pygame.K_d:
                right = True
            elif event.key == pygame.K_SPACE:
                bullethero.shoot(player1.x,player1.y,player1.size)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                left = False
            elif event.key == pygame.K_d:
                right = False
    hp_sur.fill((128,128,128))
    hp_sur.blit(hp_shrift.render("HP: "+ str(player1.hp), 1, (255,255,255)), (0,0))
    #BackGround
    window.fill((150,150,150))
    #Player
    player1.move(left,right)
    player1.draw()
    hitbox = player1.hitbox
    #BulletHero
    bullethero.move()
    bullethero.draw()
    #Enemy
    i = 0
    for f in enemy:
        f.move()
        f.draw()
        bulletenemy[i].shoot(f.x,f.y,f.size)
        player1.hp = (bulletenemy[i].check(int(player1.hp)))
        player1.check()
        bulletenemy[i].move()
        bulletenemy[i].draw()
        i+=1
    #End
    window.blit(hp_sur,(0,0))
    player1.check()
    pygame.display.update()
    fps.tick(30)
pygame.quit()