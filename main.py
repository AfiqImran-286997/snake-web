import pygame
import time
import random
import sys
import js
from js import firebase_app, firebase_firestore
from pyodide.ffi import to_js

pygame.init()

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Display setup
DIS_WIDTH = 600
DIS_HEIGHT = 400
dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
pygame.display.set_caption('Snake Web Game')

clock = pygame.time.Clock()
snake_block = 10

# Base speed
BASE_SPEED = 0.15

font_small = pygame.font.SysFont(None, 25)
font_medium = pygame.font.SysFont(None, 30)
font_large = pygame.font.SysFont(None, 40)

def show_score(score):
   value = font_medium.render("Score: " + str(score), True, YELLOW)
   dis.blit(value, [10, 10])

def show_speed_text(multiplier):
   text = font_small.render(f"Speed ×{multiplier:.1f}", True, YELLOW)
   dis.blit(text, [DIS_WIDTH - 140, 10])

def draw_snake(snake_list):
   for x, y in snake_list:
       pygame.draw.rect(dis, GREEN, [x, y, snake_block, snake_block])

def show_message(msg, color):
   mesg = font_large.render(msg, True, color)
   dis.blit(mesg, [DIS_WIDTH / 6, DIS_HEIGHT / 3])

def send_score_to_firebase(name, score):
   db = firebase_firestore.getFirestore(firebase_app)
   doc_ref = firebase_firestore.doc(db, "scores", str(time.time()))
   firebase_firestore.setDoc(doc_ref, to_js({
       "game": "snake",
       "name": name,
       "score": score,
       "created_at": firebase_firestore.serverTimestamp()
   }))

def gameLoop():
   game_over = False
   game_close = False

   x1 = DIS_WIDTH / 2
   y1 = DIS_HEIGHT / 2
   x1_change = 0
   y1_change = 0

   snake_list = []
   length_of_snake = 1
   score = 0

   foodx = round(random.randrange(0, DIS_WIDTH - snake_block) / 10.0) * 10.0
   foody = round(random.randrange(0, DIS_HEIGHT - snake_block) / 10.0) * 10.0

   player_name = js.prompt("Enter your name:", "Player")

   # --- Speed system ---
   speed_multiplier = 1
   last_speed_multiplier = 1
   last_speedup_time = 0
   show_speedup = False

   while not game_over:

       while game_close:
           dis.fill(BLUE)
           show_message("You Lost! Press Q-Quit or C-Play Again", RED)
           show_score(score)
           pygame.display.update()

           for event in pygame.event.get():
               if event.type == pygame.KEYDOWN:
                   if event.key == pygame.K_q:
                       game_over = True
                       game_close = False
                   elif event.key == pygame.K_c:
                       gameLoop()

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               game_over = True
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_LEFT:
                   x1_change = -snake_block
                   y1_change = 0
               elif event.key == pygame.K_RIGHT:
                   x1_change = snake_block
                   y1_change = 0
               elif event.key == pygame.K_UP:
                   y1_change = -snake_block
                   x1_change = 0
               elif event.key == pygame.K_DOWN:
                   y1_change = snake_block
                   x1_change = 0

       if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0:
           game_close = True
           send_score_to_firebase(player_name, score)

       x1 += x1_change
       y1 += y1_change

       dis.fill(BLACK)
       pygame.draw.rect(dis, BLUE, [foodx, foody, snake_block, snake_block])

       snake_head = [x1, y1]
       snake_list.append(snake_head)
       if len(snake_list) > length_of_snake:
           del snake_list[0]

       for block in snake_list[:-1]:
           if block == snake_head:
               game_close = True
               send_score_to_firebase(player_name, score)

       draw_snake(snake_list)
       show_score(score)
       show_speed_text(speed_multiplier)

       # Show "Speed Up!" popup
       if show_speedup and time.time() - last_speedup_time <= 2:
           popup = font_large.render(f"Speed Up! ×{speed_multiplier:.1f}", True, RED)
           dis.blit(popup, [DIS_WIDTH / 3, DIS_HEIGHT / 2 - 20])
       elif show_speedup and time.time() - last_speedup_time > 2:
           show_speedup = False

       pygame.display.update()

       # Eat food
       if x1 == foodx and y1 == foody:
           foodx = round(random.randrange(0, DIS_WIDTH - snake_block) / 10.0) * 10.0
           foody = round(random.randrange(0, DIS_HEIGHT - snake_block) / 10.0) * 10.0
           length_of_snake += 1
           score += 1

       # --- Dynamic speed ---
       speed_multiplier = 1 + (score // 5)
       current_speed = BASE_SPEED / speed_multiplier
       if current_speed < 0.02:
           current_speed = 0.02

       # If speed changed → trigger popup
       if speed_multiplier != last_speed_multiplier:
           show_speedup = True
           last_speedup_time = time.time()
           last_speed_multiplier = speed_multiplier

       time.sleep(current_speed)

   pygame.quit()
   quit()

gameLoop()
