import random
import pygame
from typing import List, Tuple

"""
Game area: Leave two rows to top for generation of cubes, 20x10 area, 
"""


def make_shapes():
    points = []
    x = 100
    y = 100
    rec = 30

    points.append((x, y))

    x += rec * 3
    points.append((x, y))

    y += rec
    points.append((x, y))

    x -= rec
    points.append((x, y))

    y += rec
    points.append((x, y))

    x -= rec
    points.append((x, y))

    y -= rec
    points.append((x, y))

    x -= rec
    points.append((x, y))

    return points


class Game:
    def __init__(self):
        pygame.init()

        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 800
        # Setup screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Create a clock to manage the frame rate
        self.clock = pygame.time.Clock()
        # Create a font object for rendering the FPS
        self.font = pygame.font.SysFont(None, 36)
        # List for squares
        self.squares: List[pygame.Rect] = []
        self.rectangle_spawn_timer = 0.5
        self.timer = 0
        self.run = True

    def create_rectangle(self, x: float, y: float, w: float, h: float) -> None:
        square = pygame.Rect(x, y, w, h)
        self.squares.append(square)

    def draw_rectangles(self, color: Tuple[int, int, int]):
        for square in self.squares:
            pygame.draw.rect(self.screen, color, square)

    def easy_collision(self, target_square: pygame.Rect) -> bool:
        # Loop over other squares to check for collision
        for square in self.squares:
            if target_square == square:
                continue

            if target_square.bottomleft > square.bottomright or target_square.bottomright < square.bottomleft:
                continue

            if square.top == target_square.bottom:
                return True

        return False

    def can_move(self, square: pygame.Rect) -> bool:
        if square.bottom == 800:
            return False

        if self.easy_collision(square):
            return False

        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

    def handle_fps(self):
        # Calculate and display FPS
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))  # White color
        self.screen.blit(fps_text, (10, 10))  # Draw the FPS text in the top left corner

    def handle_spawn_timer(self):
        if self.timer <= 0:
            random_x = random.randint(50, 550)
            self.create_rectangle(random_x, 100.0, 30.0, 30.0)
            self.timer = self.rectangle_spawn_timer

    def draw_game_area(self):
        # Vertical lines
        pygame.draw.line(self.screen, (255, 255, 255), (250, 0), (250, 800), 5)
        pygame.draw.line(self.screen, (255, 255, 255), (550, 0), (550, 800), 5)
        # Horizontal lines
        pygame.draw.line(self.screen, (255, 255, 255), (250, 100), (550, 100), 5)
        pygame.draw.line(self.screen, (255, 255, 255), (250, 700), (550, 700), 5)

    def execute(self):
        while self.run:
            self.screen.fill((0, 0, 0))
            self.draw_game_area()
            pygame.draw.polygon(self.screen, (255, 255, 255), [(100, 100), (190, 100), (190, 130), (160, 130), (160, 160), (130, 160), (130, 130), (100, 130)])
            self.draw_rectangles((255, 0, 0))

            for square in self.squares:
                if self.can_move(square):
                    square.move_ip(0, 1)

            self.handle_events()
            self.handle_fps()

            # Update the screen
            pygame.display.update()

            # Limit to 60 frames per second
            dt = self.clock.tick(60) / 1000
            self.timer -= dt
            self.handle_spawn_timer()

        self.cleanup()

    def cleanup(self):
        pygame.quit()


def main():
    print(make_shapes())


if __name__ == '__main__':
    # main()
    game = Game()
    game.execute()
