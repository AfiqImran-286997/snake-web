import pygame
import time
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 480
CELL = 10
SNAKE_SPEED = 15

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE  = (50, 153, 213)
GRAY  = (169, 169, 169)
PURP  = (160, 32, 240)
GOLD  = (255, 215, 0)

font_main  = pygame.font.SysFont("bahnschrift", 26)
font_score = pygame.font.SysFont("comicsansms", 20)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake — Pygame (offline)")
clock = pygame.time.Clock()

def draw_text_center(msg, color, y):
   surf = font_main.render(msg, True, color)
   rect = surf.get_rect(center=(WIDTH//2, y))
   win.blit(surf, rect)

def hud(score, remain):
   s = font_score.render(f"Score: {score}", True, WHITE)
   t = font_score.render(f"Time: {remain}", True, WHITE)
   win.blit(s, (10, 10))
   win.blit(t, (WIDTH-120, 10))

def rand_cell():
   return [
       random.randrange(0, WIDTH // CELL) * CELL,
       random.randrange(0, HEIGHT // CELL) * CELL
   ]

def game_over_screen(score):
   while True:
       for e in pygame.event.get():
           if e.type == pygame.QUIT:
               return "quit"
           if e.type == pygame.KEYDOWN:
               if e.key == pygame.K_q:
                   return "quit"
               if e.key == pygame.K_c or e.key == pygame.K_r:
                   return "restart"
       win.fill(BLACK)
       draw_text_center(f"Game Over! Score: {score}", RED, HEIGHT//3)
       draw_text_center("Press C/R to Restart or Q to Quit", WHITE, HEIGHT//3 + 40)
       pygame.display.flip()
       clock.tick(15)

def play_one_round():
   x = (WIDTH // (2*CELL)) * CELL
   y = (HEIGHT // (2*CELL)) * CELL
   dx, dy = 0, 0
   cur_dir = (0, 0)
   next_dir = (0, 0)

   snake = [[x, y]]
   snake_len = 1
   score = 0

   food = rand_cell()

   poison = [rand_cell() for _ in range(4)]
   poison_cycle_start = time.time()
   POISON_VISIBLE_SECS = 3.0
   POISON_HIDDEN_SECS = 1.0

   golden = None
   golden_spawn_time = None
   GOLDEN_LIFE = 5.0

   obstacles = []

   round_start = None
   HARD_LIMIT = 60

   running = True
   while running:
       # input
       for e in pygame.event.get():
           if e.type == pygame.QUIT:
               return "quit"
           if e.type == pygame.KEYDOWN:
               if round_start is None and e.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                                                    pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
                   round_start = time.time()
               if e.key in (pygame.K_LEFT, pygame.K_a):
                   next_dir = (-CELL, 0)
               elif e.key in (pygame.K_RIGHT, pygame.K_d):
                   next_dir = (CELL, 0)
               elif e.key in (pygame.K_UP, pygame.K_w):
                   next_dir = (0, -CELL)
               elif e.key in (pygame.K_DOWN, pygame.K_s):
                   next_dir = (0, CELL)

       # prevent 180° reverse
       if (next_dir[0] != -cur_dir[0] or next_dir[1] != -cur_dir[1]) or cur_dir == (0, 0):
           dx, dy = next_dir
           cur_dir = next_dir

       # time / end by timeout
       elapsed = 0 if round_start is None else time.time() - round_start
       if elapsed >= HARD_LIMIT:
           out = game_over_screen(score)
           return out

       # poison visibility
       t = time.time() - poison_cycle_start
       cycle = POISON_VISIBLE_SECS + POISON_HIDDEN_SECS
       phase = t % cycle
       poison_visible = (phase <= POISON_VISIBLE_SECS)
       # respawn set when hidden->visible; approximate on phase near 0
       if not poison_visible and phase < 0.05:
           poison = [rand_cell() for _ in range(4)]

       # maybe golden
       if golden is None and random.randint(1,100) <= 3:
           golden = rand_cell()
           golden_spawn_time = time.time()
       if golden and (time.time() - golden_spawn_time) > GOLDEN_LIFE:
           golden = None

       # move
       x += dx; y += dy
       if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
           out = game_over_screen(score)
           return out
       head = [x, y]
       snake.append(head)
       while len(snake) > snake_len:
           snake.pop(0)

       # collisions
       if head in snake[:-1]:
           out = game_over_screen(score)
           return out

       for ox, oy in obstacles:
           if x == ox and y == oy:
               out = game_over_screen(score)
               return out

       # draw
       win.fill(BLUE)

       # food
       pygame.draw.rect(win, RED, (food[0], food[1], CELL, CELL))

       # poison
       if poison_visible:
           for px, py in poison:
               pygame.draw.rect(win, PURP, (px, py, CELL, CELL))

       # golden
       if golden:
           pygame.draw.rect(win, GOLD, (golden[0], golden[1], CELL, CELL))

       # obstacles
       for ox, oy in obstacles:
           pygame.draw.rect(win, GRAY, (ox, oy, CELL, CELL))

       # snake
       for sx, sy in snake:
           pygame.draw.rect(win, GREEN, (sx, sy, CELL, CELL))

       # hud
       remain = max(0, HARD_LIMIT - int(elapsed))
       hud(score, remain)

       pygame.display.flip()

       # eats
       if x == food[0] and y == food[1]:
           food = rand_cell()
           snake_len += 1
           score += 1
           # spawn obstacle safely (simple attempt: avoid snake + food)
           forbidden = set((sx, sy) for sx, sy in snake)
           forbidden.add((food[0], food[1]))
           while True:
               c = rand_cell()
               if (c[0], c[1]) not in forbidden:
                   obstacles.append(c)
                   break

       if poison_visible:
           for i in range(len(poison) - 1, -1, -1):
               if x == poison[i][0] and y == poison[i][1]:
                   poison.pop(i)
                   score = max(0, score - 2)

       if golden and x == golden[0] and y == golden[1]:
           score += 5
           snake_len += 5
           for _ in range(5):
               forbidden = set((sx, sy) for sx, sy in snake)
               forbidden.add((food[0], food[1]))
               while True:
                   c = rand_cell()
                   if (c[0], c[1]) not in forbidden:
                       obstacles.append(c)
                       break
           golden = None

       clock.tick(SNAKE_SPEED)

def main():
   while True:
       out = play_one_round()
       if out == "quit":
           break
   pygame.quit()
   sys.exit()

if __name__ == "__main__":
   main()
