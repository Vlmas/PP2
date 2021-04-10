import pygame
import sys
import random
import time

pygame.init()
running=True

win_size=(720,540)
win=pygame.display.set_mode(win_size)
pygame.display.set_caption('New OOP Based Snake Game by Almas')
fps=pygame.time.Clock()

snakes=[]
food=[]

class Colors:
    black=(0,0,0)
    white=(255,255,255)
    green=(0,255,0)
    red=(255,0,0)
    blue=(0,0,255)
    dark_red=(160,0,0)
    dark_green=(0,120,0)
    dark_blue=(0,0,120)
    gray=(130,130,130)

class Snake:
    def __init__(self):
        self.__size=12
        self.__speed=12
        self.x=random.randrange(1,60)*self.__size
        self.y=random.randrange(1,45)*self.__size
        self._status='alive'
        self._direction='right'
        self._body=[[self.x,self.y],[self.x-self.__size,self.y]]
        self._hitbox=pygame.Rect(self.x,self.y,self.__size,self.__size)

    def set_direction(self,keys):
        if keys[pygame.K_w] and self._direction!='down':
            self._direction='up'
        elif keys[pygame.K_s] and self._direction!='up':
            self._direction='down'
        elif keys[pygame.K_d] and self._direction!='left':
            self._direction='right'
        elif keys[pygame.K_a] and self._direction!='right':
            self._direction='left'

    def move(self,seconds):
        if self._direction=='up':
            self.y-=self.__speed#*seconds
        elif self._direction=='down':
            self.y+=self.__speed#*seconds
        elif self._direction=='right':
            self.x+=self.__speed#*seconds
        elif self._direction=='left':
            self.x-=self.__speed#*seconds
        self._hitbox=pygame.Rect(self.x,self.y,self.__size,self.__size)

    def expand(self):
        self._body.insert(0,[self.x,self.y])
        self._body.pop()

    def get_size(self):
        return self.__size
    
    def get_speed(self):
        return self.__speed

    def draw(self):
        head=True
        for part in self._body:
            if head:
                pygame.draw.rect(win,Colors.dark_red,(part[0],part[1],self.__size,self.__size))
            else:
                pygame.draw.rect(win,Colors.red,(part[0],part[1],self.__size,self.__size))
            head=False

class Food:
    def __init__(self):
        self.__size=12
        self.x=random.randrange(1,59)*self.__size
        self.y=random.randrange(1,44)*self.__size
        self._hitbox=pygame.Rect(self.x,self.y,self.__size,self.__size)

    def respawn(self):
        global snakes
        for snake in snakes:
            if self._hitbox.colliderect(snake._hitbox):
                self.x=random.randrange(1,59)*self.__size
                self.y=random.randrange(1,44)*self.__size
                self._hitbox=pygame.Rect(self.x,self.y,self.__size,self.__size)

    def get_size(self):
        return self.__size

    def draw(self):
        pygame.draw.rect(win,Colors.dark_red,(self.x,self.y,self.__size,self.__size))

class Game:
    @staticmethod
    def game():
        global running,win,snakes,food

        snakes.append(Snake())
        food.append(Food())

        while running:
            milliseconds=fps.tick(25)
            seconds=milliseconds/1000

            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                    pygame.quit()
                    sys.exit(0)

            win.fill(Colors.dark_green)

            keys=pygame.key.get_pressed()

            for snake in snakes:
                snake.draw()
                snake.set_direction(keys)
                snake.move(seconds)
                snake.expand()
            
            for foo in food:
                foo.respawn()
                foo.draw()

            pygame.display.update()


if __name__=='__main__':
    Game.game()