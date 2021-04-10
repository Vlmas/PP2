import random
import sys
import os
import time

class Character:
    def __init__(self,name,health,mana):
        self.name=name
        self.health=health
        self.mana=mana

    def change_health(self,health):
        if health in range(0,101):
            self.health=health
        else:
            self.health=100

    def change_mana(self,mana):
        if mana in range(0,101):
            self.mana=mana
        else:
            self.mana=100

class Skill:
    def __init__(self,name,damage,mana):
        self.name=name
        self.damage=damage
        self.mana=mana

class Hero(Character):
    def __init__(self,name,health,mana):
        Character.__init__(self,name,health,mana)
        self.skills=[]

    def add_skill(self,skill):
        self.skills.append(skill)

    def remove_skill(self,skill):
        if skill in self.skills:
            self.skills.remove(skill)
        else:
            print('Данный навык не имеется в списке навыков героя!')
    
class Evil(Character):
    def __init__(self,name,health,mana,skill):
        Character.__init__(self,name,health,mana)
        self.skill=skill

def main():
    hero_skills=[
        Skill('Удар рукой',10,5),
        Skill('Удар ногой',20,10),
        Skill('Удар дубинкой',30,15),
        Skill('Кинуть камень',30,15),
        Skill('Удар ножом',40,25),
        Skill('Поджечь',50,40),
        Skill('Выстрелить с пистолета',45,30),
        Skill('Выстрелить с автомата',60,50),
        Skill('Подорвать гранатой',65,55),
        Skill('Подорвать взрывчаткой C4',100,90),
    ]
    enemy_skills=[
        Skill('Удар рукой',10,5),
        Skill('Удар ногой',20,10),
        Skill('Удар дубинкой',30,15),
        Skill('Кинуть камень',30,15),
        Skill('Удар ножом',40,25),
        Skill('Поджечь',50,40),
        Skill('Выстрелить с пистолета',45,30),
        Skill('Выстрелить с автомата',60,50),
        Skill('Подорвать гранатой',65,55)
    ]
    enemy_names=['Hitler','Kim Jong Un','I am Evil','Joker']

    print('Инициализация...')
    hero=Hero('Ilyas',50,50)
    hero.add_skill(random.choice(hero_skills))
    hero.add_skill(random.choice(hero_skills))
    enemy=Evil(
        random.choice(enemy_names),
        random.randrange(15,50),
        random.randrange(0,80),
        random.choice(enemy_skills)
    )
    turn='h'
    enemy_base_health=int(enemy.health)
    rounds=1

    time.sleep(1)
    print('Игра успешно инициализирована!')
    time.sleep(2)
    os.system('cls')

    print('Имя героя: {}. Здоровье: {}. Мана: {}.'.format(hero.name,hero.health,hero.mana))
    print('Имя врага: {}. Здоровье: {}. Мана: {}.'.format(enemy.name,enemy.health,enemy.mana))

    time.sleep(5)
    os.system('cls')

    while True:
        if hero.health>0 and enemy.health>0:
            os.system('cls')
            print(f'Раунд {rounds}')
            print('Текущие состояние героя {} - Здоровье: {}. Мана: {}.'.format(hero.name,hero.health,hero.mana))
            print('Текущие состояние врага {} - Здоровье: {}. Мана: {}.'.format(enemy.name,enemy.health,enemy.mana))
            if turn=='h':
                print('Выберите каким навыком атаковать врага:')

                t=1
                for i in hero.skills:
                    print('{}) Имя навыка: {}.'.format(t,i.name),'Урон: {}.'.format(i.damage),'Мана: {}.'.format(i.mana))
                    t+=1
                
                idx=input()

                if idx=='q':
                    print('Выходим из игры!')
                    sys.exit(0)
                elif idx>='0' and idx<='9' and int(idx)<=len(hero.skills):
                    idx=int(idx)
                else:
                    print('Недопустимое число!')
                    sys.exit(0)
                
                os.system('cls')

                print('Атакуем врага навыком {}!'.format(hero.skills[idx-1].name))

                enemy.health-=hero.skills[idx-1].damage

                if len(hero.skills)>1:
                    hero.remove_skill(hero.skills[idx-1])

                time.sleep(1)

                turn='e'
            elif turn=='e':
                print('Внимание! Враг атакует навыком {}, с уроном {}!'.format(enemy.skill.name,enemy.skill.damage))
                time.sleep(3)
                hero.health-=enemy.skill.damage
                turn='h'
            rounds+=1
        else:
            if hero.health<=0:
                print('Герой был повержен!')
                print('Имя врага: {}'.format(enemy.name))
                print(f'Пережито раундов: {rounds}')
                sys.exit(0)
            elif enemy.health<=0:
                print('{} победил врага {}!'.format(hero.name,enemy.name))
                print('Присваиваем трофеи..')
                hero.add_skill(enemy.skill)
                hero.health+=int(enemy_base_health/2)
                if hero.health>100:
                    hero.health=100
                hero.change_mana(hero.mana+enemy.mana/2)
                time.sleep(1)
                print('Инициализируем нового врага..')
                enemy=Evil(
                    random.choice(enemy_names),
                    random.randrange(15,50),
                    random.randrange(0,80),
                    random.choice(enemy_skills)
                )
                enemy_base_health=enemy.health
                turn='h'
                time.sleep(1)
                not_yet=random.randrange(1,100)
                if not_yet%6==0:
                    print('О нет! Враг перед смертью успел кинуть камень в героя!')
                    hero.health-=30
                    time.sleep(3)
                os.system('cls')


if __name__=='__main__':
    main()