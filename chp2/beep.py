import pygame, sys
from pygame.locals import *

pygame.init()

soundObj = pygame.mixer.Sound('beeps.wav')
soundObj.play()
import time
time.sleep(1)
soundObj.stop()

# super simple...

# background music? What...
# super cool

pygame.mixer.music.load('background-music.mp3')
pygame.mixer.music.play(-1, 0.0) # -1 makes it loop forever
pygame.mixer.music.stop()
