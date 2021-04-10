import pygame

pygame.init()

class Game:
    def __init__(self):
        self.size = (800,640)
        self.window = pygame.display.set_mode(self.size)
        self.fps = pygame.time.Clock()
    def bg(self):
        self.window.fill((150,150,150))
    def update(self):
        pygame.display.update()
class Tank(object):
    def __init__(self,sur):
        self.x = 200
        self.y = 200
        self.sur = sur
        self.size = 32
        self.speed = 4
        self.hitbox = pygame.Rect(self.x,self.y,self.size,self.size)
        self.img = pygame.image.load("tank1.png")
        self.moving = self.img
        self.animc = 0
    def anim(self):
        self.img = pygame.image.load(f"tank{self.animc//15}.png")
    def move(self, direction):
        if direction == "Up":
            self.hitbox = pygame.Rect(self.x,self.y-self.speed,self.size,self.size)
            for f in walls:
                if self.hitbox.colliderect(f.hitbox): 
                    return
            self.moving = pygame.transform.rotate(self.img, 0)
            self.y -= self.speed
        elif direction == "Down":
            self.hitbox = pygame.Rect(self.x,self.y+self.speed,self.size,self.size)
            for f in walls:
                if self.hitbox.colliderect(f.hitbox): 
                    return
            self.moving = pygame.transform.rotate(self.img, 180)
            self.y += self.speed
        elif direction == "Left":
            self.hitbox = pygame.Rect(self.x-self.speed,self.y,self.size,self.size)
            for f in walls:
                if self.hitbox.colliderect(f.hitbox): 
                    return
            self.moving = pygame.transform.rotate(self.img, 90)
            self.x -= self.speed
        elif direction == "Right":
            self.hitbox = pygame.Rect(self.x+self.speed,self.y,self.size,self.size)
            for f in walls:
                if self.hitbox.colliderect(f.hitbox): 
                    return
            self.moving = pygame.transform.rotate(self.img, -90)
            self.x += self.speed
        self.animc+=1
        if self.animc>=30: self.animc = 0
    def draw(self):
        self.sur.blit(self.moving,(self.x,self.y))
class Wall(object):
    def init(self,x,y,sur):
        self.x = x
        self.y = y
        self.size = 16
        self.hitbox = pygame.Rect(self.x,self.y,self.size,self.size)
        self.sur = sur
        self.img = pygame.image.load("wall.png")
    def draw(self):
        self.sur.blit(self.img,(self.x,self.y))
class Bullet(object):
    def init(self,sur):
        self.x = -100
        self.y = -100
        self.size = 8
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.sur = sur
        self.hitbox = pygame.Rect(self.x,self.y,self.size,self.size)
        self.shot = False
        self.speed = 8
    def shoot(self,direction,x,y):
        self.x = x
        self.y = y
        self.shot = True
        if direction == "Up":
            self.x +=12
            self.up = True
        elif direction == "Down":
            self.x+=12
            self.y+=32 
            self.down = True
        elif direction == "Left":
            self.y +=12 
            self.left = True
        elif direction == "Right":
            self.y+=12
            self.x+=32 
            self.right = True
    def move(self):
        if self.up:
            self.hitbox = pygame.Rect(self.x,self.y-self.speed,self.size,self.size)
            for f in walls:
                if self.hitbox.colliderect(f.hitbox):
                    self.up=self.down=self.left=self.right=False
                    self.x = self.y = -100
                    self.shot = False
                    walls.remove(f)
                    return
            self.y-=self.speed
            if self.y <=0:
                self.up=self.down=self.left=self.right=False
                self.x = self.y = -100
                self.shot = False
                return
        elif self.down:
            self.hitbox = pygame.Rect(self.x,self.y+self.speed,self.size,self.size)

        for f in walls:
                if self.hitbox.colliderect(f.hitbox):
                    self.up=self.down=self.left=self.right=False
                    self.x = self.y = -100
                    self.shot = False
                    walls.remove(f)
                    return
                self.y+=self.speed
                if self.y >=640:
                    self.up=self.down=self.left=self.right=False
                    self.x = self.y = -100
                    self.shot = False
                    return
                elif self.left:
                    self.hitbox = pygame.Rect(self.x-self.speed,self.y,self.size,self.size)
                    for f in walls:
                        if self.hitbox.colliderect(f.hitbox):
                            self.up=self.down=self.left=self.right=False
                            self.x = self.y = -100
                            self.shot = False
                            walls.remove(f)
                            return
                    self.x-=self.speed
                    if self.x <=0:
                        self.up=self.down=self.left=self.right=False
                        self.x = self.y = -100
                        self.shot = False
                        return
                elif self.right:
                    self.hitbox = pygame.Rect(self.x+self.speed,self.y,self.size,self.size)
                    for f in walls:
                        if self.hitbox.colliderect(f.hitbox):
                            self.up=self.down=self.left=self.right=False
                            self.x = self.y = -100
                            self.shot = False
                            walls.remove(f)
                            return
                    self.x+=self.speed
                    if self.x >=800:
                        self.up=self.down=self.left=self.right=False
                        self.x = self.y = -100
                        self.shot = False
                        return
def draw(self):
    pygame.draw.circle(self.sur, (120,67,213), (self.x,self.y),int(self.size/2))
game = Game()
###
walls = []
f = open("walls.txt")
c = f.readlines()
i = 0
for lines in c:
    j=0
    for stolbik in lines:
        if stolbik == "-":
            walls.append(Wall(j,i,game.window))
        j+=16
    i+=16
f.close()
###
bullet = Bullet(game.window)
tank = Tank(game.window)
direction = ""
db = "Up"
while 1:
    for f in pygame.event.get():
        if f.type == pygame.QUIT:
            quit()
        if f.type == pygame.KEYDOWN:
            if f.key == pygame.K_q and not(bullet.shot):
                bullet.shoot(db,tank.x,tank.y)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        direction = "Up"
        db = "Up"
    elif keys[pygame.K_s]:
        direction = "Down"
        db = "Down"
    elif keys[pygame.K_a]:
        direction = "Left"
        db = "Left"
    elif keys[pygame.K_d]:
        direction = "Right"
        db = "Right"
    else: direction = ""
    game.bg()
    tank.move(direction)
    tank.anim()
    # if keys[pygame.K_q] and not(bullet.shot):
    #     bullet.shoot(db,tank.x,tank.y)
    tank.draw()
    bullet.move()
    bullet.draw()
    for f in walls:
        f.draw()
    game.update()
    print(bullet.x , bullet.y)
    game.fps.tick(30)
pygame.quit()