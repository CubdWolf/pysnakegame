#import
import pygame
import random

#config
cellSize = 25
cellCount = 30
mode = 1 #1 die, 2 other side

#bg stuff
bgcellcolor = (100,155,100)
bgcellcolor2 = (120,155,120)
bgCell = pygame.Surface((cellSize,cellSize))
bgCell.fill(bgcellcolor)

#fruit
fruitcellcolor = "red"
fruitCell = pygame.Surface((cellSize,cellSize))
fruitCell.fill(fruitcellcolor)
fruitExist = False

#snake
snakecolor = (128,128,0)
headcolor = (200,200,0)
snakeCell = pygame.Surface((cellSize,cellSize))
snakeposx= cellSize*(cellCount//2)
snakeposy= cellSize*(cellCount//2)
snakedir = 0 #0up, 1right, 2down, 3left
snakelistx = []
snakelisty = []
snakelen = 2

#init pygame
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((cellSize *cellCount, cellSize *cellCount))
running = True
pygame.display.set_caption("Silly Audie!!!")

#music
music =1
if music == 1:
    pygame.mixer.init()
    pygame.mixer.music.load("sillyaudio.ogg")
    pygame.mixer.music.play(-1)

#timer stuff
moveEvent = pygame.USEREVENT+1
pygame.time.set_timer(moveEvent, 50)

#die
dieCell = pygame.Surface((cellSize,cellSize))
dieCell.fill("red")
def die(snakeposx, snakeposy):
    screen.blit(dieCell, (snakeposx, snakeposy))
    print("die")
    return 1

#surface1 and pos
surface1 = pygame.Surface((100,50))
x = (1280-50)/2
y = (720-25)/2

#input stuff
pending = 0

#fps stuff
zero = 0
nozero = 0
fpstable = []

#main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and pending == 0:
            if event.key == pygame.K_UP: 
                if snakedir != 2:
                    snakedir = 0
                    pending = 1
            elif event.key == pygame.K_RIGHT: 
                if snakedir != 3:
                    snakedir = 1
                    pending = 1
            elif event.key == pygame.K_DOWN: 
                if snakedir != 0:
                    snakedir = 2
                    pending = 1
            elif event.key == pygame.K_LEFT: 
                if snakedir != 1:
                    snakedir = 3
                    pending = 1
            elif event.key ==pygame.K_SPACE:
                snakelen +=1
        elif event.type == moveEvent:
                    #background
            screen.fill(bgcellcolor2)
            bgloopy = 0
            while bgloopy <= cellCount:
                bgloopx = 0
                while bgloopx <= cellCount/2:
                    if bgloopy %2 == 0:
                        screen.blit(bgCell, ((cellSize*2*bgloopx), cellSize*bgloopy))
                        bgloopx +=1
                    else:
                        screen.blit(bgCell, ((cellSize+cellSize*2*bgloopx), cellSize*bgloopy))
                        bgloopx +=1
                bgloopy += 1

            #fruit     
            #print(fruitExist)
            if fruitExist == False:
                flp = 1
                while flp == 1:
                    fx = cellSize*(random.randint(0,(cellCount-1)))
                    fy = cellSize*(random.randint(0,(cellCount-1)))
                    for i in range(1,snakelen+1):
                        try:
                            if fx != snakelistx[-i] and fy != snakelisty[-i]:
                                flp = 0
                        except:
                            flp = 0
            screen.blit(fruitCell, (fx,fy))
            fruitExist=True

            if snakeposx == fx and snakeposy == fy:
                fruitExist =False
                snakelen +=1

            print("moved")
            snakelistx.append(snakeposx)
            snakelisty.append(snakeposy)
            snakeCell.fill(snakecolor)
            for i in range(2,snakelen+2):
                try:
                    screen.blit(snakeCell, (snakelistx[-i], snakelisty[-i]))
                except:
                    print("heh")
            snakeCell.fill(headcolor)
            screen.blit(snakeCell, (snakeposx,snakeposy))
            if snakedir == 0:
                print("movedup")
                snakeposy -= cellSize
            elif snakedir == 1:
                print("movedup")
                snakeposx += cellSize
            elif snakedir == 2:
                print("movedup")
                snakeposy += cellSize
            elif snakedir == 3:
                print("movedup")
                snakeposx -= cellSize
            for i in range(1,snakelen+1):
                try:
                    if snakeposx == snakelistx[-i] and snakeposy == snakelisty[-i]:
                        if mode ==1:
                            moveEvent = die(snakeposx,snakeposy)
                        elif mode ==2:
                            print("die")
                except:
                    print("heh")
            if snakeposx > (cellCount-1)*cellSize or snakeposx < 0 or snakeposy < 0 or snakeposy > (cellCount-1)*cellSize:
                if mode ==1:
                    moveEvent = die(snakeposx,snakeposy)
                elif mode ==2:
                    if snakeposx > (cellCount-1)*cellSize:
                        snakeposx = 0
                    elif snakeposy > (cellCount-1)*cellSize:
                        snakeposy = 0
                    elif snakeposx < 0:
                        snakeposx = cellCount*cellSize
                    elif snakeposy < 0:
                        snakeposy = cellCount*cellSize
            pending = 0



#fps
    x += random.randint(-10,10)
    y += random.randint(-10,10)
    fpstable.append(clock.get_fps())
    try:
        fpstable.remove(0)
        zero += 1
    except:
        nozero += 1
    if len(fpstable) > 0:
        pygame.display.set_caption(f"min: {str(min(fpstable))} current: {str(clock.get_fps())} max: {str(max(fpstable))} z: {zero} nz: {nozero}")
    pygame.display.update()
    clock.tick(120)

pygame.quit()