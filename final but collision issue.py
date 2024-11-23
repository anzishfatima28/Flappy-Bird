import pygame as pg
import sys
import time
from random import randint
import os  # Importing os to check file existence

class Game:
    def __init__(self):
        # Setting up the window
        self.width = 650
        self.height = 763
        pg.init()
        self.win = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("Flappy Bird Clone")
        self.clock = pg.time.Clock()

        # Initialize variables
        self.scale_factor = 1.2
        self.move_speed = 200  # Background movement speed
        self.is_enter_pressed = False
        self.pipes = []
        self.pipe_generate_counter = 0
        self.game_over = False
        self.game_over_delay = 0.5  # Delay before showing "Game Over" screen
        self.game_over_time = 0  # Timer for game over

        self.setup_background_and_ground()
        self.bird = Bird(self.scale_factor)

        self.gameloop()

    def setup_background_and_ground(self):
        # Load images for background and ground
        bg_path = r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Network Shortcuts\flappy bird\backgroundd - Copy.png"
        ground_path = r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Network Shortcuts\flappy bird\grounddd - Copy.png"

        if os.path.exists(bg_path):
            self.bg_img = pg.transform.scale(pg.image.load(bg_path).convert(), (self.width, self.height))
        else:
            print("Background image not found at:", bg_path)
            sys.exit()

        ground_height = 150
        if os.path.exists(ground_path):
            self.ground_img = pg.transform.scale(pg.image.load(ground_path).convert(), (self.width, ground_height))
        else:
            print("Ground image not found at:", ground_path)
            sys.exit()

        # Set up ground position for seamless scrolling
        self.ground1_rect = self.ground_img.get_rect(topleft=(0, self.height - ground_height))
        self.ground2_rect = self.ground_img.get_rect(topleft=(self.width, self.height - ground_height))

    def gameloop(self):
        last_time = time.time()

        while True:
            # Calculate delta time
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            self.handle_events()

            if self.is_enter_pressed and not self.game_over:
                self.update_game(dt)
                self.check_collisions()

            self.draw_game()
            pg.display.update()
            self.clock.tick(60)

            # Handle game over state
            if self.game_over:
                self.game_over_time += dt
                if self.game_over_time >= self.game_over_delay:
                    self.display_game_over()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:  # Start the game
                    self.reset_game()
                if event.key == pg.K_SPACE and self.is_enter_pressed and not self.game_over:  # Bird flap
                    self.bird.flap()
                if self.game_over and event.key == pg.K_r:  # Restart game
                    self.reset_game()

    def reset_game(self):
        self.is_enter_pressed = True
        self.game_over = False
        self.game_over_time = 0  # Reset game over timer
        self.pipes.clear()
        self.bird.rect.center = (100, 300)
        self.bird.y_velocity = 0

    def update_game(self, dt):
        # Moving the ground
        self.ground1_rect.x -= int(self.move_speed * dt)
        self.ground2_rect.x -= int(self.move_speed * dt)

        # Reset ground positions for seamless scrolling
        if self.ground1_rect.right <= 0:
            self.ground1_rect.x = self.ground2_rect.right
        if self.ground2_rect.right <= 0:
            self.ground2_rect.x = self.ground1_rect.right

        # Generating pipes
        self.pipe_generate_counter += 1
        if self.pipe_generate_counter > 70:  # Generate a new pipe every 70 frames
            self.pipes.append(Pipe(self.scale_factor, self.move_speed))
            self.pipe_generate_counter = 0

        # Moving pipes
        for pipe in self.pipes[:]:
            pipe.update(dt)
            if pipe.rect_up.right < 0:
                self.pipes.remove(pipe)

        # Moving the bird
        self.bird.update(dt)

    def check_collisions(self):
        # Check for collisions between the bird and pipes
        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.rect_up) or self.bird.rect.colliderect(pipe.rect_down):
                self.game_over = True
                break

        # Check if bird hits the ground
        if self.bird.rect.bottom >= 663:  # Ground level
            self.game_over = True

    def draw_game(self):
        self.win.blit(self.bg_img, (0, 0))
        for pipe in self.pipes:
            pipe.draw_pipe(self.win)
        self.win.blit(self.ground_img, self.ground1_rect)
        self.win.blit(self.ground_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        if self.game_over:
            self.display_game_over()

    def display_game_over(self):
        font = pg.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.win.blit(text, text_rect)
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.win.blit(restart_text, restart_rect)


class Bird(pg.sprite.Sprite):
    def __init__(self, scale_factor):
        super().__init__()
        self.img_list = [
            pg.transform.scale(pg.image.load(r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Network Shortcuts\flappy bird\wing up - Copy.png").convert_alpha(), (50, 50)),
            pg.transform.scale(pg.image.load(r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Network Shortcuts\flappy bird\wing down - Copy.png").convert_alpha(), (50, 50))
        ]
        self.image_index = 0
        self.image = self.img_list[self.image_index]
        self.rect = self.image.get_rect(center=(100, 300))

        # Bird physics
        self.y_velocity = 0
        self.gravity = 500
        self.flap_strength = -250
        self.animation_counter = 0

    def update(self, dt):
        # Gravity effect
        self.y_velocity += self.gravity * dt
        self.rect.y += self.y_velocity * dt

        # Play bird animation
        self.animate()

        # Prevent bird from going off-screen
        if self.rect.top < 0:
            self.rect.top = 0
            self.y_velocity = 0
        if self.rect.bottom > 663:
            self.rect.bottom = 663
            self.y_velocity = 0

    def flap(self):
        self.y_velocity = self.flap_strength

    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.image_index = 1 - self.image_index  # Toggle between 0 and 1
            self.image = self.img_list[self.image_index]
            self.animation_counter = 0


class Pipe:
    def __init__(self, scale_factor, move_speed):
        self.img_up = pg.transform.scale_by(
            pg.image.load(r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Network Shortcuts\flappy bird\pipe upside down - Copy.png").convert_alpha(), scale_factor
        )
        self.img_down = pg.transform.scale_by(
            pg.image.load(r"C:\Users\hp\AppData\Roaming\Microsoft\Windows\Network Shortcuts\flappy bird\pipe down - Copy.png").convert_alpha(), scale_factor
        )
        self.rect_up = self.img_up.get_rect()
        self.rect_down = self.img_down.get_rect()

        self.pipe_distance = 200
        self.rect_up.y = randint(300, 600)
        self.rect_up.x = 700
        self.rect_down.y = self.rect_up.y - self.pipe_distance - self.rect_down.height
        self.rect_down.x = self.rect_up.x

        self.move_speed = move_speed

    def draw_pipe(self, win):
        win.blit(self.img_up, self.rect_up)
        win.blit(self.img_down, self.rect_down)

    def update(self, dt):
        self.rect_up.x -= int(self.move_speed * dt)
        self.rect_down.x -= int(self.move_speed * dt)


# Run the game
if __name__ == "__main__":
    Game()