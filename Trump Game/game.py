import pygame
import sys
import random
import time

pygame.init()

running=True

fps=pygame.time.Clock()
frame_rate=30
win_size=(800,600)
win=pygame.display.set_mode(win_size)
pygame.display.set_caption('TRUMP IS THE BOSS')

idle=pygame.image.load('Images/Idle/idle.png')
bg=pygame.image.load('Images/Background/background1.jpg')
enemy_img=pygame.image.load('Images/Enemies/playerShip1_orange.png')
bullet_img=pygame.image.load('Images/Bullet/herobullet.png')
move_left=[
    pygame.image.load('Images/Left/pygame_left_1.png'),
    pygame.image.load('Images/Left/pygame_left_2.png'),
    pygame.image.load('Images/Left/pygame_left_3.png'),
    pygame.image.load('Images/Left/pygame_left_4.png'),
    pygame.image.load('Images/Left/pygame_left_5.png'),
    pygame.image.load('Images/Left/pygame_left_6.png')
]
move_right=[
    pygame.image.load('Images/Right/pygame_right_1.png'),
    pygame.image.load('Images/Right/pygame_right_2.png'),
    pygame.image.load('Images/Right/pygame_right_3.png'),
    pygame.image.load('Images/Right/pygame_right_4.png'),
    pygame.image.load('Images/Right/pygame_right_5.png'),
    pygame.image.load('Images/Right/pygame_right_6.png')
]

deag_sound=pygame.mixer.Sound('Sounds/deagle.wav')
deag_sound.set_volume(0.1)

direction=''
jump_units=10
jumping=False

pygame.mixer.music.load('Sounds/offensive.mp3')
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)

bullets=[]
enemies=[]

class Colors:
    black=(0,0,0)
    white=(255,255,255)
    blue=(0,0,255)
    green=(0,255,0)
    red=(255,0,0)
    gray=(130,130,130)

class Hero:
    def __init__(self):
        self.sizex=60
        self.sizey=71
        self.x=(win_size[0]-self.sizex)/2
        self.y=win_size[1]-self.sizey-15
        self.hitbox=pygame.Rect(self.x,self.y,self.sizex,self.sizey)
        self.speed=10
        self.anim_counter=0
        self.image=idle
        self.moving_right=False
        self.moving_left=False
        self.status='alive'
        self.hp=5

    def move(self,direction):
        if direction=='left':
            self.x-=self.speed
        elif direction=='right':
            self.x+=self.speed
        self.hitbox=pygame.Rect(round(self.x),round(self.y),self.sizex,self.sizey)

    def animate(self):
        if self.moving_right:
            self.image=move_right[self.anim_counter//5]
            self.anim_counter+=1
        elif self.moving_left:
            self.image=move_left[self.anim_counter//5]
            self.anim_counter+=1
        elif not self.moving_left and not self.moving_right:
            self.image=idle
    
    def check_health(self):
        if self.hp<=0:
            self.status='dead'

    def draw(self):
        win.blit(self.image,(round(self.x),round(self.y)))

class Bullet:
    def __init__(self,carrier:str):
        self.sizex=11
        self.sizey=18
        self.x=-20
        self.y=-20
        self.image=pygame.image.load('Images/Bullet/herobullet.png')
        self.hitbox=pygame.Rect(self.x,self.y,self.sizex,self.sizey)
        self.speed=25
        self.carrier=carrier
        self.fire=False
        self.hit=False

    def shoot(self):
        if not self.fire:
            self.x=self.sizex+player.x+10
            self.y=self.sizey+player.y-40
            self.fire=True

    def move(self):
        if self.fire:
            if self.carrier=='hero':
                self.hitbox=pygame.Rect(self.x,self.y-self.speed,self.sizex,self.sizey)
                for enemy in enemies:
                    if self.hitbox.colliderect(enemy.hitbox):
                        self.hit=True
                        enemies.remove(enemy)
                        if len(enemies)==0:
                            GameScenaries.youWon()
                        self.x=-20
                        self.y=-20
                        self.fire=False
                        return
                        
                if self.y<0:
                    self.x=-20
                    self.y=-20
                    self.fire=False
                    return
                else:
                    self.y-=self.speed

    def draw(self):
        if self.carrier=='hero':
            win.blit(self.image,(round(self.x),round(self.y)))

class Enemy:
    def __init__(self):
        self.sizex=99
        self.sizey=75
        self.x=random.randrange(1,8)*self.sizex
        self.y=random.randrange(0,3)*self.sizey
        self.hitbox=pygame.Rect(self.x,self.y,self.sizex,self.sizey)
        self.speed=random.randrange(5,15)
        self.image=enemy_img
        self.remove=False

    def move(self):
        if self.x<0 or self.x>win_size[0]-self.sizex:
            self.hitbox=pygame.Rect(self.x-self.speed,self.y,self.sizex,self.sizey)
            self.speed=-self.speed
        self.hitbox=pygame.Rect(self.x+self.speed,self.y,self.sizex,self.sizey)
        self.x+=self.speed

    def draw(self):
        win.blit(self.image,(round(self.x),round(self.y)))

player=Hero()
herobullet=Bullet('hero')

cnt=random.randint(3,6)
for i in range(cnt):
    enemies.append(Enemy())

class GameScenaries:
    @staticmethod
    def gameOver():
        death_font=pygame.font.SysFont('georgia',80)
        font_render=death_font.render('YOU DIED',True,Colors.red)
        death_sound=pygame.mixer.Sound('Sounds/death_sound.wav')
        win.fill(Colors.black)
        win.blit(font_render,(win_size[0]/4,win_size[1]/2.5))
        death_sound.play()
        pygame.display.update()
        time.sleep(4)
        pygame.quit()
        sys.exit()

    @staticmethod
    def youWon():
        font=pygame.font.SysFont('georgia',80)
        font_render=font.render('YOU WON',True,Colors.green)
        win.fill(Colors.white)
        win.blit(font_render,(win_size[0]/4,win_size[1]/2.5))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()

while running:
    fps.tick(frame_rate)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
            pygame.quit()
            sys.exit(0)
        if event.type==pygame.KEYUP and event.key==pygame.K_f:
            deag_sound.play()

    keys=pygame.key.get_pressed()

    if player.status=='dead' or player.status=='self destruction':
        GameScenaries.gameOver() 
    if keys[pygame.K_ESCAPE]:
        player.status='self destruction'
    if keys[pygame.K_k]:
        GameScenaries.youWon()
    if keys[pygame.K_f]:
        herobullet.shoot()

    if keys[pygame.K_a] and player.x>5:
        direction='left'
        player.moving_left=True
        player.moving_right=False
    elif keys[pygame.K_d] and player.x<win_size[0]-player.sizex-5:
        direction='right'
        player.moving_left=False
        player.moving_right=True
    else:
        player.moving_left=False
        player.moving_right=False
        player.anim_counter=0
        direction=''

    if not jumping:
        if keys[pygame.K_SPACE]:
            jumping=True
    else:
        if jump_units>=-10:
            if jump_units<0:
                player.y+=(jump_units**2)/6
            else:
                player.y-=(jump_units**2)/6
            jump_units-=1
        else:
            jumping=False
            jump_units=10

    if player.anim_counter+1>=frame_rate:
        player.anim_counter=0

    win.blit(bg,(0,0))

    for enemy in enemies:
        # if herobullet.hit:
        #     enemies.remove(enemy)
        #     herobullet.hit=False
        if len(enemies)<=0:
            GameScenaries.youWon()
        enemy.draw()
        enemy.move()

    player.draw()
    player.move(direction)
    player.animate()
    herobullet.draw()
    herobullet.move()

    pygame.display.update()