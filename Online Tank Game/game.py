import pygame
import sys
import time
import pika
import random
import json
import uuid
import numpy
from threading import Thread

pygame.init()

menu=True
win_size=(800,600)
win=pygame.display.set_mode(win_size)
pygame.display.set_caption('Tank Game by Almas')
fps=pygame.time.Clock()
stopwatch=200
bot=False

bullet_img=pygame.image.load('Images/Bullet/tankbullet.png')
wall_img=pygame.image.load('Images/Wall/wall112.png')
bonus_img=pygame.image.load('Images/Bonus/tankbonus.png')
tank1_imgs=[
    pygame.image.load('Images/Tank1/tank1_downward.png'),
    pygame.image.load('Images/Tank1/tank1_upward.png'),
    pygame.image.load('Images/Tank1/tank1_leftward.png'),
    pygame.image.load('Images/Tank1/tank1_rightward.png')
]
tank2_imgs=[
    pygame.image.load('Images/Tank2/tank2_downward.png'),
    pygame.image.load('Images/Tank2/tank2_upward.png'),
    pygame.image.load('Images/Tank2/tank2_leftward.png'),
    pygame.image.load('Images/Tank2/tank2_rightward.png')
]
tank1_imgs_m=[
    pygame.image.load('Images/Tank1m/tank1_downward.png'),
    pygame.image.load('Images/Tank1m/tank1_upward.png'),
    pygame.image.load('Images/Tank1m/tank1_leftward.png'),
    pygame.image.load('Images/Tank1m/tank1_rightward.png')
]
tank2_imgs_m=[
    pygame.image.load('Images/Tank2m/tank2_downward.png'),
    pygame.image.load('Images/Tank2m/tank2_upward.png'),
    pygame.image.load('Images/Tank2m/tank2_leftward.png'),
    pygame.image.load('Images/Tank2m/tank2_rightward.png')
]

tanks=[]
bullets=[]
walls=[]
bonuses=[]
winners=[]
kicked=[]
losers=[]

class Colors:
    black=(0,0,0)
    white=(255,255,255)
    green=(0,255,0)
    red=(255,0,0)
    blue=(0,0,255)
    dark_red=(120,0,0)
    dark_green=(0,120,0)
    dark_blue=(0,0,120)
    gray=(130,130,130)

class RpcClient:
    def __init__(self):
        self.connection=pika.BlockingConnection(
            pika.ConnectionParameters(
                host='34.254.177.17',
                port=5672,
                virtual_host='dar-tanks',
                credentials=pika.PlainCredentials(
                    username='dar-tanks',
                    password='5orPLExUYnyVYZg48caMpX'
                )
            )
        )
        self.channel=self.connection.channel()
        queue=self.channel.queue_declare(queue='',exclusive=True,auto_delete=True)
        self.callback_queue=queue.method.queue
        self.channel.queue_bind(queue=self.callback_queue,exchange='X:routing.topic')
        self.channel.basic_consume(queue=self.callback_queue,on_message_callback=self.onResponse,auto_ack=True)
        self.response=None
        self.token=None
        self.corr_id=None
        self.tank_id=None
    
    def onResponse(self,ch,method,props,body):
        if self.corr_id==props.correlation_id:
            self.response=json.loads(body)
            print(self.response)

    def call(self,rk,msg={}):
        self.response=None
        self.corr_id=str(uuid.uuid4())
        self.channel.basic_publish(exchange='X:routing.topic',routing_key=rk,body=json.dumps(msg),
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            )
        )

        while self.response is None:
            self.connection.process_data_events()

    def registerRequest(self,room_id):
        msg={
            'roomId':room_id
        }
        print('[*] Registration request')
        self.call('tank.request.register',msg=msg)
        try:
            self.tank_id=self.response['tankId']
            self.token=self.response['token']
        except:
            raise Exception('[!] Registration error')

    def turnRequest(self,direction):
        msg={
            'token':self.token,
            'direction':direction
        }
        print('[*] Turn request')
        self.call('tank.request.turn',msg=msg)

    def fireRequest(self):
        msg={
            'token':self.token
        }
        print('[*] Fire request')
        self.call('tank.request.fire',msg=msg)

class RpcConsumer(Thread):
    def __init__(self,room):
        Thread.__init__(self)
        self.connection=pika.BlockingConnection(
            pika.ConnectionParameters(
                host='34.254.177.17',
                port=5672,
                virtual_host='dar-tanks',
                credentials=pika.PlainCredentials(
                    username='dar-tanks',
                    password='5orPLExUYnyVYZg48caMpX'
                )
            )
        )
        self.room_id=room
        self.response=None
        self.channel=self.connection.channel()
        queue=self.channel.queue_declare(queue='',exclusive=True,auto_delete=True)
        self.events_queue=queue.method.queue
        self.channel.queue_bind(queue=self.events_queue,exchange='X:routing.topic',routing_key=f'event.state.{self.room_id}')
        self.channel.basic_consume(
            queue=self.events_queue,
            on_message_callback=self.onResponse,
            auto_ack=True
        )

    def onResponse(self,ch,method,props,body):
        self.response=json.loads(body)

    def run(self):
        self.channel.start_consuming()

class Button:
    @staticmethod
    def writeText(x,y,text,win,color):
        font=pygame.font.SysFont('georgia',20)
        rend=font.render(text,True,color)
        win.blit(rend,(x,y))

    def __init__(self,x,y,text):
        self.text=text
        self.x=x
        self.y=y
        self.sizex=200
        self.sizey=50
        self.rect=pygame.Rect(self.x,self.y,self.sizex,self.sizey)

    def draw(self,mouse_pos,win):
        if self.rect.collidepoint(mouse_pos[0],mouse_pos[1]):
            self.writeText(self.x,self.y,self.text,win,Colors.white)
            pygame.draw.line(win,Colors.white,(self.x,self.y+self.sizey-20),
                (self.x+self.sizex-30,self.y+self.sizey-20),2)
        else:
            self.writeText(self.x,self.y,self.text,win,Colors.black)

    def eventCheck(self,mouse_pos,mouse_click):
        global menu,bot
        if self.rect.collidepoint(mouse_pos[0],mouse_pos[1]) and mouse_click[0] and self.text=='Quit the game':
            time.sleep(0.1)
            menu=False
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit(0)
        elif self.rect.collidepoint(mouse_pos[0],mouse_pos[1]) and mouse_click[0] and self.text=='Singleplayer':
            menu=False
            pygame.mixer.music.stop()
            Game.singlePlayer()
        elif self.rect.collidepoint(mouse_pos[0],mouse_pos[1]) and mouse_click[0] and self.text=='Multiplayer':
            menu=False
            pygame.mixer.music.stop()
            Game.multiPlayer()
        elif self.rect.collidepoint(mouse_pos[0],mouse_pos[1]) and mouse_click[0] and self.text=='Multiplayer with AI':
            menu=False
            bot=True
            pygame.mixer.music.stop()
            Game.multiPlayer()

class Tank:
    def __init__(self,carrier,x,y):
        self.hp=3
        self.speed=140
        self.sizex=64
        self.sizey=64
        self.x=x
        self.y=y
        self.carrier=carrier
        self.last_move=''
        self.direction=''
        self.ticks=0
        self.buff=False
        self.counter=300
        if self.carrier=='Almas':
            self.image=tank1_imgs[3]
        else:
            self.image=tank2_imgs[2]
        if self.carrier=='Almas':
            self.last_move='right'
        else:
            self.last_move='left'
        self.hitbox=pygame.Rect(self.x,self.y,self.sizex,self.sizey)
        self.moving=False
        self.tank_death_sound=pygame.mixer.Sound('Sounds/explosion.ogg')
        self.hit_sound=pygame.mixer.Sound('Sounds/hitsound.ogg')

    def checkKeys(self,keys):
        if self.carrier=='Almas':
            if keys[pygame.K_a]:
                self.direction='left'
                self.last_move='left'
                self.moving=True
            elif keys[pygame.K_d]:
                self.direction='right'
                self.last_move='right'
                self.moving=True
            elif keys[pygame.K_w]:
                self.direction='up'
                self.last_move='up'
                self.moving=True
            elif keys[pygame.K_s]:
                self.direction='down'
                self.last_move='down'
                self.moving=True
            if keys[pygame.K_e]:
                self.direction=''
                self.moving=False
            if keys[pygame.K_SPACE] and (pygame.time.get_ticks()-self.ticks)/1000>=1 and not self.buff:
                self.ticks=pygame.time.get_ticks()
                bullets.append(Bullet(self.x,self.y,self.sizex,self.last_move,self.carrier))
        else:
            if keys[pygame.K_LEFT]:
                self.direction='left'
                self.last_move='left'
                self.moving=True
            elif keys[pygame.K_RIGHT]:
                self.direction='right'
                self.last_move='right'
                self.moving=True
            elif keys[pygame.K_UP]:
                self.direction='up'
                self.last_move='up'
                self.moving=True
            elif keys[pygame.K_DOWN]:
                self.direction='down'
                self.last_move='down'
                self.moving=True
            if keys[pygame.K_m]:
                self.direction=''
                self.moving=False
            if keys[pygame.K_RETURN] and (pygame.time.get_ticks()-self.ticks)/1000>=1 and not self.buff:
                self.ticks=pygame.time.get_ticks()
                bullets.append(Bullet(self.x,self.y,self.sizex,self.last_move,self.carrier))
                
    def move(self,seconds):
        if self.carrier=='Almas':
            if self.direction=='up':
                self.y-=self.speed*seconds
                self.image=tank1_imgs[1]
            elif self.direction=='down':
                self.y+=self.speed*seconds
                self.image=tank1_imgs[0]
            elif self.direction=='right':
                self.x+=self.speed*seconds
                self.image=tank1_imgs[3]
            elif self.direction=='left':
                self.x-=self.speed*seconds
                self.image=tank1_imgs[2]
        else:
            if self.direction=='up':
                self.y-=self.speed*seconds
                self.image=tank2_imgs[1]
            elif self.direction=='down':
                self.y+=self.speed*seconds
                self.image=tank2_imgs[0]
            elif self.direction=='right':
                self.x+=self.speed*seconds
                self.image=tank2_imgs[3]
            elif self.direction=='left':
                self.x-=self.speed*seconds
                self.image=tank2_imgs[2]
        self.hitbox=pygame.Rect(round(self.x),round(self.y),self.sizex,self.sizey)
    
    def checkBorders(self):
        if self.x>win_size[0]:
            self.x=-self.sizex 
        if self.x<-self.sizex:
            self.x=win_size[0]
        if self.y>win_size[1]:
            self.y=-self.sizey 
        if self.y<-self.sizey:
            self.y=win_size[1]

    def kill(self):
        self.image=pygame.image.load('Images/Explosion/explosion.png')
        self.tank_death_sound.play()
        win.blit(self.image,(round(self.x),round(self.y)))
        pygame.display.update()
        time.sleep(0.0005)

    def checkCollisions(self):
        for bullet in bullets:
            if self.hitbox.colliderect(bullet.hitbox) and self.carrier!=bullet.carrier:
                self.hp-=1
                bullets.remove(bullet)
                self.hit_sound.play()

        for wall in walls:
            if self.hitbox.colliderect(wall.hitbox):
                self.hp-=1
                walls.remove(wall)
                self.hit_sound.play()

        for tank in tanks:
            if self.hitbox.colliderect(tank.hitbox) and self.carrier!=tank.carrier:
                self.hp-=1

    def checkBuff(self,keys):
        if self.buff:
            self.speed=280
            self.counter-=1
            if self.carrier=='Almas':
                if keys[pygame.K_SPACE] and (pygame.time.get_ticks()-self.ticks)/1000>=1:
                    self.ticks=pygame.time.get_ticks()
                    bullets.append(Bullet(self.x,self.y,self.sizex,self.last_move,self.carrier,500))
            else:
                if keys[pygame.K_RETURN] and (pygame.time.get_ticks()-self.ticks)/1000>=1:
                    self.ticks=pygame.time.get_ticks()
                    bullets.append(Bullet(self.x,self.y,self.sizex,self.last_move,self.carrier,500))
            if self.counter<=0:
                self.buff=False
                self.counter=300
                self.speed=140

    def draw(self):
        win.blit(self.image,(round(self.x),round(self.y)))

class Bullet:
    def __init__(self,tank_x,tank_y,tank_size,direction,carrier,speed=250):
        self.carrier=carrier
        self.size=9
        self.x=-20
        self.y=-20
        self.image=pygame.image.load('Images/Bullet/tankbullet.png')
        self.speed=speed
        self.direction=direction
        self.remove=False
        self.bullet_sound=pygame.mixer.Sound('Sounds/fire.ogg')
        self.bullet_sound.set_volume(0.5)
        if self.direction=='right':
            self.x=tank_x+tank_size+5
            self.y=tank_y+tank_size/2.4
        elif self.direction=='left':
            self.x=tank_x-5
            self.y=tank_y+tank_size/2.4
        elif self.direction=='up':
            self.x=tank_x+tank_size/2.4
            self.y=tank_y-5
        elif self.direction=='down':
            self.x=tank_x+tank_size/2.4
            self.y=tank_y+tank_size+5
        self.hitbox=pygame.Rect(round(self.x),round(self.y),self.size,self.size)

    def move(self,seconds):
        if self.x>win_size[0] or self.x<0 or self.y>win_size[1] or self.y<0:
            self.remove=True
        if self.direction=='right':
            self.x+=self.speed*seconds
        elif self.direction=='left':
            self.x-=self.speed*seconds
        elif self.direction=='up':
            self.y-=self.speed*seconds
        elif self.direction=='down':
            self.y+=self.speed*seconds
        self.hitbox=pygame.Rect(round(self.x),round(self.y),self.size,self.size)

    def checkCollisions(self):
        for wall in walls:
            if self.hitbox.colliderect(wall.hitbox):
                wall.hit_sound.play()
                walls.remove(wall)
                self.remove=True

    def draw(self):
        win.blit(self.image,(round(self.x),round(self.y)))

class Wall:
    def __init__(self):
        self.x=random.randrange(2,15)*40
        self.y=random.randrange(2,12)*40
        self.size=40
        self.image=wall_img
        self.hitbox=pygame.Rect(self.x,self.y,self.size,self.size)
        self.remove=False
        self.hit_sound=pygame.mixer.Sound('Sounds/hitsound.ogg')
        self.hit_sound.set_volume(3)

    def draw(self):
        win.blit(self.image,(self.x,self.y))

class Bonus:
    def __init__(self):
        self.size=32
        self.x=random.randrange(300,600)
        self.y=random.randrange(200,500)
        self.hitbox=pygame.Rect(self.x,self.y,self.size,self.size)
        self.image=bonus_img
        self.eaten=False
        self.sound=pygame.mixer.Sound('Sounds/bonus.ogg')
        self.times=[60,180,300,600,900]
        self.timer=random.choice(self.times)

    def checkCollisions(self):
        if self.timer>0:
            self.timer-=1
        if self.timer<=0:
            for tank in tanks:
                if tank.hitbox.colliderect(self.hitbox):
                    self.eaten=True
                    tank.buff=True
                    self.sound.play()
        
            for wall in walls:
                if wall.hitbox.colliderect(self.hitbox):
                    walls.remove(wall)

    def draw(self):
        if self.timer<=0:
            win.blit(self.image,(self.x,self.y))

class GameMenu:
    @staticmethod
    def showHP(tank_hp,tank_carrier):
        font=pygame.font.SysFont('times new roman',30)
        rend=font.render(f'HP of {tank_carrier}: {tank_hp}',True,Colors.black)
        if tank_carrier=='Almas':
            win.blit(rend,(0,0))
        else:
            win.blit(rend,(win_size[0]-185,0))

    @staticmethod
    def showWinner(tank_carrier):
        font=pygame.font.SysFont('times new roman',30)
        rend=font.render(f'{tank_carrier} wins!',True,Colors.black)
        win.blit(rend,(round(win_size[0]/2.5),0))

    @staticmethod
    def kick(data,sid,win_size):
        font1=pygame.font.SysFont('georgia',45)
        font2=pygame.font.SysFont('times new roman',25)
        rend1=font1.render('YOU WERE KICKED',True,Colors.white)
        win.fill(Colors.black)
        win.blit(rend1,(round(win_size[0]/3.5),round(win_size[1]/2.5)))
        for var in data:
            if var['tankId']==sid:
                rend2=font2.render('Score: {}'.format(var['score']),True,Colors.white)
                win.blit(rend2,(round(win_size[0]/2.2),round(win_size[1]/1.5)))
        pygame.display.update()
        time.sleep(3)

    @staticmethod
    def victory(data,sid,win_size):
        font1=pygame.font.SysFont('georgia',45)
        font2=pygame.font.SysFont('times new roman',25)
        rend1=font1.render('YOU HAVE WON!',True,Colors.green)
        win.fill(Colors.black)
        win.blit(rend1,(round(win_size[0]/3.2),round(win_size[1]/2.5)))
        for var in data:
            if var['tankId']==sid:
                rend2=font2.render('Score: {}'.format(var['score']),True,Colors.green)
                win.blit(rend2,(round(win_size[0]/2.2),round(win_size[1]/1.5)))
        pygame.display.update()
        time.sleep(3)

    @staticmethod
    def defeat(data,sid,win_size):
        font1=pygame.font.SysFont('georgia',45)
        font2=pygame.font.SysFont('times new roman',25)
        rend1=font1.render('YOU HAVE LOST!',True,Colors.red)
        win.fill(Colors.black)
        win.blit(rend1,(round(win_size[0]/3.2),round(win_size[1]/2.5)))
        for var in data:
            if var['tankId']==sid:
                rend2=font2.render('Score: {}'.format(var['score']),True,Colors.red)
                win.blit(rend2,(round(win_size[0]/2.2),round(win_size[1]/1.5)))
        pygame.display.update()
        time.sleep(3)

    @staticmethod
    def mainMenu(win):
        global menu
        bg=pygame.image.load('Images/Background/tank_bg2.jpg')
        pygame.mixer.music.load('Sounds/offensive.mp3')
        by_Almas=pygame.font.SysFont('blackadderitc',25)
        rendit=by_Almas.render('Made by Almas',True,Colors.black)
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        
        button1=Button(600,250,'Singleplayer')
        button2=Button(600,300,'Multiplayer')
        button3=Button(600,350,'Multiplayer with AI')
        button4=Button(600,400,'Quit the game')

        while menu:
            fps.tick(60)

            mouse_pos=pygame.mouse.get_pos()
            mouse_click=pygame.mouse.get_pressed()
            events=pygame.event.get()
            for event in events:
                if event.type==pygame.QUIT:
                    menu=False
                    pygame.quit()
                    sys.exit(0)

            win.blit(bg,(0,0))
            win.blit(rendit,(5,win_size[1]-30))
            button1.draw(mouse_pos,win)
            button2.draw(mouse_pos,win)
            button3.draw(mouse_pos,win)
            button4.draw(mouse_pos,win)
            button1.eventCheck(mouse_pos,mouse_click)
            button2.eventCheck(mouse_pos,mouse_click)
            button3.eventCheck(mouse_pos,mouse_click)
            button4.eventCheck(mouse_pos,mouse_click)
            pygame.display.update()

def sortScore(json):
    return json['score']

class Game:
    @staticmethod
    def singlePlayer():
        global win,tank1_imgs,tank2_imgs,bullet_img,tanks,bullets,walls,stopwatch
        tank1=Tank('Almas',20,500)
        tank2=Tank('player',700,20)
        tanks.append(tank1)
        tanks.append(tank2)
        running=True

        pygame.mixer.music.load('Sounds/pursuit.mp3')
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        
        for _ in range(random.randrange(18,28)):
            walls.append(Wall())

        for _ in range(random.randrange(1,4)):
            bonuses.append(Bonus())

        while running:
            milliseconds=fps.tick(60)
            seconds=milliseconds/1000

            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                    pygame.quit
                    sys.exit(0)

            keys=pygame.key.get_pressed()
            win.fill(Colors.dark_green)

            for tank in tanks:
                tank.draw()
                tank.checkKeys(keys)
                tank.checkBorders()
                tank.checkCollisions()
                tank.checkBuff(keys)
                tank.move(seconds)
                GameMenu.showHP(tank.hp,tank.carrier)
                if tank.hp==0:
                    tank.kill()
                    tanks.remove(tank)
                if len(tanks)<=1:
                    GameMenu.showWinner(tank.carrier)
                    stopwatch-=1
                    if stopwatch<=0:
                        running=False
                        pygame.quit
                        sys.exit(0)

            for bullet in bullets:
                bullet.draw()
                bullet.move(seconds)
                bullet.checkCollisions()
                if bullet.remove:
                    bullets.remove(bullet)

            for bonus in bonuses:
                bonus.draw()
                bonus.checkCollisions()
                if bonus.eaten:
                    bonuses.remove(bonus)

            for wall in walls:
                wall.draw()

            pygame.display.update()

    @staticmethod
    def multiPlayer():
        global win,win_size,tanks,losers,kicked,winners,tank1_imgs_m,tank2_imgs_m,bot
        running=True
        win_size=(1030,600)
        win=pygame.display.set_mode(win_size)
        interface=pygame.image.load('Images/Interface/interface1.png')
        fire_latency=150
        turn_latency=30
        pygame.mixer.music.load('Sounds/pursuit.mp3')
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
        time_font=pygame.font.SysFont('times new roman',20)
        id_font=pygame.font.SysFont('times new roman',12)
        data_font=pygame.font.SysFont('times new roman',18)
    
        room='room-1'
        client=RpcClient()
        client.registerRequest(room)
        consumer=RpcConsumer(room)
        consumer.daemon=True
        consumer.start()

        while running:
            fps.tick(100)

            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                    pygame.quit()
                    sys.exit(0)
                if event.type==pygame.KEYDOWN:
                    if not bot:
                        if event.key==pygame.K_SPACE:
                            client.fireRequest()
                        if event.key==pygame.K_w:
                            client.turnRequest('UP')
                        elif event.key==pygame.K_s:
                            client.turnRequest('DOWN')
                        elif event.key==pygame.K_d:
                            client.turnRequest('RIGHT')
                        elif event.key==pygame.K_a:
                            client.turnRequest('LEFT')

            win.fill(Colors.dark_green)
            win.blit(interface,(830,0))

            for var in consumer.response['gameField']['tanks']:
                if var not in tanks:
                    tanks.append(var)
                if var['id'] not in consumer.response['gameField']['tanks']:
                    tanks.remove(var)

            if bot:
                fire_latency-=1
                for tank in consumer.response['gameField']['tanks']:
                    if tank['id']==client.tank_id:
                        x=tank['x']
                        y=tank['y']
                for bullet in consumer.response['gameField']['bullets']:
                    if bullet['owner']!=client.tank_id:
                        if numpy.sqrt((x-bullet['x'])**2+(y-bullet['y'])**2)<=150 and bullet['x']<x:
                            client.turnRequest('RIGHT')
                        elif numpy.sqrt((x-bullet['x'])**2+(y-bullet['y'])**2)<=150 and bullet['x']>x:
                            client.turnRequest('LEFT')
                        elif numpy.sqrt((x-bullet['x'])**2+(y-bullet['y'])**2)<=150 and bullet['y']>y:
                            client.turnRequest('UP')
                        elif numpy.sqrt((x-bullet['x'])**2+(y-bullet['y'])**2)<=150 and bullet['y']<y:
                            client.turnRequest('DOWN')
                        else:
                            pass
                for tank in consumer.response['gameField']['tanks']:
                    if tank['id']!=client.tank_id:
                        turn_latency-=1
                        if turn_latency<=0:
                            turn_latency=30
                            if tank['x']>=x and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)>=20 and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=380:
                                client.turnRequest('RIGHT')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            if tank['x']<=x and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)>=20 and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=380:
                                client.turnRequest('LEFT')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            if tank['y']<=y and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)>=20 and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=380:
                                client.turnRequest('UP')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            if tank['y']>=y and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)>=20 and numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=380:
                                client.turnRequest('DOWN')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            else:
                                pass
                            if numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=130 and tank['x']<x:
                                client.turnRequest('RIGHT')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            if numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<130 and tank['x']>x:
                                client.turnRequest('LEFT')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            if numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=130 and tank['y']>y:
                                client.turnRequest('UP')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            if numpy.sqrt((x-tank['x'])**2+(y-tank['y'])**2)<=130 and tank['y']<y:
                                client.turnRequest('DOWN')
                                if fire_latency<=0:
                                    fire_latency=150
                                    client.fireRequest()
                            else:
                                pass

            for tank in consumer.response['gameField']['tanks']:
                try:
                    x=tank['x']
                    y=tank['y']
                    if tank['id']==client.tank_id:
                        if tank['direction']=='DOWN':
                            win.blit(tank1_imgs_m[0],(x,y))
                        elif tank['direction']=='UP':
                            win.blit(tank1_imgs_m[1],(x,y))
                        elif tank['direction']=='LEFT':
                            win.blit(tank1_imgs_m[2],(x,y))
                        elif tank['direction']=='RIGHT':
                            win.blit(tank1_imgs_m[3],(x,y))
                        else:
                            win.blit(tank1_imgs_m[3])
                        id_render=id_font.render(tank['id'],True,Colors.white)
                        win.blit(id_render,(x,y-15))
                    else:
                        if tank['direction']=='DOWN':
                            win.blit(tank2_imgs_m[0],(x,y))
                        elif tank['direction']=='UP':
                            win.blit(tank2_imgs_m[1],(x,y))
                        elif tank['direction']=='LEFT':
                            win.blit(tank2_imgs_m[2],(x,y))
                        elif tank['direction']=='RIGHT':
                            win.blit(tank2_imgs_m[3],(x,y))
                        else:
                            win.blit(tank2_imgs_m[3])
                        id_render=id_font.render(tank['id'],True,Colors.black)
                        win.blit(id_render,(x,y-15))
                except:
                    pass

            for bullet in consumer.response['gameField']['bullets']:
                try:
                    x=bullet['x']
                    y=bullet['y']
                    if bullet['owner']==client.tank_id:
                        pygame.draw.rect(win,Colors.gray,(x,y,6,6))
                    else:
                        pygame.draw.rect(win,Colors.white,(x,y,6,6))
                except:
                    pass

            tank_data=consumer.response['gameField']['tanks']
            tank_data.sort(key=sortScore,reverse=True)
            indices=0
            for var in tank_data:
                rend1=data_font.render('{0}:: hp: {1}, score: {2}'.format(var['id'],var['health'],var['score']),True,Colors.white)
                rend2=data_font.render('{0}:: hp: {1}, score: {2}'.format(var['id'],var['health'],var['score']),True,Colors.green)
                try:
                    if var['id']==client.tank_id:
                        win.blit(rend2,(win_size[0]-195,20*indices))
                    else:
                        win.blit(rend1,(win_size[0]-195,20*indices))
                    indices+=1
                except:
                    pass

            try:
                time_render=time_font.render('Remaining time: {}'.format(consumer.response['remainingTime']),True,Colors.white)
                win.blit(time_render,(845,570))
            except:
                pass

            for var in consumer.response['kicked']:
                if var['tankId'] not in kicked:
                    kicked.append(var['tankId'])
            if client.tank_id in kicked:
                GameMenu.kick(consumer.response['kicked'],client.tank_id,win_size=win_size)
                running=False
                pygame.quit()
                sys.exit(0)

            for var in consumer.response['winners']:
                if var['tankId'] not in winners:
                    winners.append(var['tankId'])
            if client.tank_id in winners:
                GameMenu.victory(consumer.response['winners'],client.tank_id,win_size=win_size)
                running=False
                pygame.quit()
                sys.exit(0)

            for var in consumer.response['losers']:
                if var['tankId'] not in losers:
                    losers.append(var['tankId'])
            if client.tank_id in losers:
                GameMenu.defeat(consumer.response['losers'],client.tank_id,win_size=win_size)
                running=False
                pygame.quit()
                sys.exit(0)

            pygame.display.update()
    

if __name__=='__main__':
    GameMenu.mainMenu(win)