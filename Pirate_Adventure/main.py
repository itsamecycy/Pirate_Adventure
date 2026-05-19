import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Pirate Adventure')
clock = pygame.time.Clock()


# Font for the game
font = pygame.font.Font('assets/fonts/Pixeltype.ttf', 50)
color1 = (143, 205, 217)

title_surf = font.render('Pirate Adventure!', False, color1)
title_rect = title_surf.get_rect(center = (640, 100))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    
    screen.blit(title_surf, title_rect)


    pygame.display.update() 
    clock.tick(60)
