import pygame
import time
import random
import sys
import js

# Firebase integration (already working in your previous setup)
from js import firebase_app, firebase_firestore
from pyodide.ffi import to_js

# Initialize pygame
pygame.init()

# Define colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Display size
dis_width = 600
dis_height = 400

dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake Game by Afiq')

clock = pygame.time.Clock()
snake_block = 10

# 🔹 Base speed (you can adjust)
base_speed = 0.15  

font_style = pygame.font.SysFont(None, 25)
score_font = pygame.font.SysFont(None, 35)

# Display the player's score
def Your_score(score):
   value = score_font.render("Your Score: " + str(score), True, yellow)
   dis.blit(value, [0, 0])

# Draw the snake on screen
def our_snake(snake_block, snake_list):
   for x in snake_list:
       pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])

# Display a message (for game over)
def message(msg, color):
   mesg = font_style.render(msg, True, color)
   dis.blit(mesg, [dis_width / 6, dis_height / 3])

# Send score to Firebase
def send_score_to_firebase(name, score):
   db = firebase_firestore.getFirestore(firebase_app)
   doc_ref = firebase_firestore.doc(db, "scores", str(time.time()))
   firebase_firestore.setDoc(doc_ref, to_js({
       "game": "snake",
       "name": name,
       "score": score,
       "created_at": firebase_firestore.serverTimestamp()
   }))

# Main game loop
def gameLoop():
   game_over = False
   game_close = False

   x1 = dis_width / 2
   y1 = dis_height / 2

   x1_change = 0
   y1_change = 0

   snake_List = []
   Length_of_snake = 1
   score = 0

   foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
   foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

   player_name = js.prompt("Enter your name:", "Player")

   while not game_over:

       while game_close == True:
           dis.fill(blue)
           message("You Lost! Press Q-Quit or C-Play Again", red)
           Your_score(score)
           pygame.display.update()

           for event in pygame.event.get():
               if event.type == pygame.KEYDOWN:
                   if event.key == pygame.K_q:
                       game_over = True
                       game_close = False
                   if event.key == pygame.K_c:
                       gameLoop()

       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               game_over = True
           if event.type == pygame.KEYDOWN:
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

       if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
           game_close = True
           send_score_to_firebase(player_name, score)
       x1 += x1_change
       y1 += y1_change
       dis.fill(black)
       pygame.draw.rect(dis, blue, [foodx, foody, snake_block, snake_block])
       snake_Head = []
       snake_Head.append(x1)
       snake_Head.append(y1)
       snake_List.append(snake_Head)
       if len(snake_List) > Length_of_snake:
           del snake_List[0]

       for x in snake_List[:-1]:
           if x == snake_Head:
               game_close = True
               send_score_to_firebase(player_name, score)

       our_snake(snake_block, snake_List)
       Your_score(score)

       pygame.display.update()

       # When snake eats food
       if x1 == foodx and y1 == foody:
           foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
           foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
           Length_of_snake += 1
           score += 1

       # ⚡ Dynamic Speed Increase System
       # Every 5 points → increase speed multiplier
       speed_multiplier = 1 + (score // 5)  # +1 multiplier per 5 points
       current_speed = base_speed / speed_multiplier

       # Optional: cap maximum speed
       if current_speed < 0.02:  # prevent going too fast
           current_speed = 0.02

       time.sleep(current_speed)

   pygame.quit()
   quit()


# Run the game
gameLoop()
