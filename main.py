import pygame, time, random
import js
from js import firebase_app, firebase_firestore, _snake_db

pygame.init()

# Colors
WHITE=(255,255,255); YELLOW=(255,255,102); BLACK=(0,0,0); RED=(213,50,80); GREEN=(0,255,0); BLUE=(50,153,213)

# Display
DIS_W, DIS_H = 360, 480   # taller so the playfield fits nicely
screen = pygame.display.set_mode((DIS_W, DIS_H))
pygame.display.set_caption("Snake — Web")

clock = pygame.time.Clock()
CELL = 10
BASE_SLEEP = 0.15  # base delay (seconds) — will be divided by multiplier
MIN_SLEEP  = 0.02  # cap (faster than this is too crazy)

font_small  = pygame.font.SysFont(None, 22)
font_medium = pygame.font.SysFont(None, 28)

def draw_snake(s):
   for (x,y) in s:
       pygame.draw.rect(screen, GREEN, (x, y, CELL, CELL))

def send_score(name, score):
   # Uses the helpers exposed by index.html
   db = _snake_db
   ref = firebase_firestore.doc(db, "scores", str(time.time()))
   firebase_firestore.setDoc(ref, {
       "game": "snake",
       "name": name,
       "score": int(score),
       "created_at": firebase_firestore.serverTimestamp()
   })

def set_speed_text(mult):
   js._snake_set_speed_text(f"Speed ×{mult:.1f}")

def show_speed_popup(mult, show=True):
   js._snake_show_speed_popup(f"×{mult:.1f}", show)

def new_food():
   return (
       round(random.randrange(0, DIS_W - CELL) / CELL) * CELL,
       round(random.randrange(0, DIS_H - CELL) / CELL) * CELL
   )

def game():
   # initial state
   x = DIS_W//2; y = DIS_H//2
   dx = 0; dy = 0
   snake = [(x,y)]
   length = 1
   score  = 0
   food = new_food()

   # name prompt
   try:
       player_name = js.prompt("Enter your name:", "Player") or "Player"
   except Exception:
       player_name = "Player"

   # speed system
   mult = 1
   last_mult = 1
   popup_until = 0.0
   set_speed_text(mult)

   running = True
   while running:
       for e in pygame.event.get():
           if e.type == pygame.QUIT:
               return
           if e.type == pygame.KEYDOWN:
               if e.key == pygame.K_LEFT:  dx, dy = -CELL, 0
               elif e.key == pygame.K_RIGHT: dx, dy = CELL, 0
               elif e.key == pygame.K_UP:   dx, dy = 0, -CELL
               elif e.key == pygame.K_DOWN: dx, dy = 0, CELL

       # move
       x += dx; y += dy

       # bounds -> game over
       if x < 0 or x >= DIS_W or y < 0 or y >= DIS_H:
           send_score(player_name, score); break

       # self-collide -> game over
       if (x,y) in snake[:-1]:
           send_score(player_name, score); break

       snake.append((x,y))
       if len(snake) > length: snake.pop(0)

       # eat
       if x == food[0] and y == food[1]:
           food = new_food()
           length += 1
           score += 1

       # speed scaling (every 5 points)
       mult = 1 + (score // 5)
       sleep_time = BASE_SLEEP / mult
       if sleep_time < MIN_SLEEP: sleep_time = MIN_SLEEP

       # popup when multiplier increases
       now = time.time()
       if mult != last_mult:
           last_mult = mult
           set_speed_text(mult)
           show_speed_popup(mult, True)
           popup_until = now + 2.0  # show for 2 seconds

       if popup_until and now > popup_until:
           show_speed_popup(mult, False)
           popup_until = 0.0

       # draw
       screen.fill(BLACK)
       # food
       pygame.draw.rect(screen, BLUE, (food[0], food[1], CELL, CELL))
       # snake
       draw_snake(snake)

       # (optional) draw score inside canvas too, if you want:
       score_surf = font_small.render(f"Score {score}", True, YELLOW)
       screen.blit(score_surf, (8, 6))

       pygame.display.flip()
       time.sleep(sleep_time)

   # simple game-over splash
   screen.fill(BLACK)
   t = font_medium.render("Game Over", True, RED)
   screen.blit(t, (DIS_W//2 - t.get_width()//2, DIS_H//2 - 12))
   pygame.display.flip()
   time.sleep(1.25)

if __name__ == "__main__":
   game()
