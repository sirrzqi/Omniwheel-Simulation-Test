import pygame
import numpy as np

pygame.init()

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((1280, 720))

player_radius = 25
player_pos = [300, 250] 

rot = 0
rot_speed = 2
#define a surface 
image_orig = pygame.Surface((150,75))
image_orig.set_colorkey((255,0,0))
image_orig.fill((255,255,255))

image = image_orig.copy()
image.set_colorkey(BLACK)
rect = image.get_rect()
rect.center = (640, 360)

FPS = 45
clock = pygame.time.Clock()
run = True

while run:
    clock.tick(FPS)
    screen.fill((86, 125, 70))

    # making a copy of the old center of the rectangle
    old_center = rect.center
    rot = (rot + rot_speed) % 360
    # rotating the origonal image
    new_image = pygame.transform.rotate(image_orig, 45)
    # 
    rect = new_image.get_rect()
    # set the rotated rectangel to the old center
    rect.center = old_center
    # drawing the rotated rectangel to the screen 
    screen.blit(new_image, rect)

    pygame.draw.circle(screen, (255, 255, 255), player_pos, player_radius)
    
    key = pygame.key.get_pressed()
    if key[pygame.K_a]:  
       player_pos[0] -= 10
    if key[pygame.K_d]:  
        player_pos[0] += 10
    if key[pygame.K_w]:  
        player_pos[1] -= 10
    if key[pygame.K_s]:  
        player_pos[1] += 10

    if player_pos[0] - player_radius < 0:  
        player_pos[0] = player_radius
    if player_pos[0] + player_radius > 1280:  
        player_pos[0] = 1280 - player_radius
    if player_pos[1] - player_radius < 0:    
        player_pos[1] = player_radius
    if player_pos[1] + player_radius > 720:  
        player_pos[1] = 720 - player_radius

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    
    pygame.display.flip()

pygame.quit()