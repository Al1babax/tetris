import random
import pygame
from typing import List, Tuple
import random
import time
from color import Colors
import os

"""
Game area: Leave two rows to top for generation of cubes, 20x10 area, 
"""


class GenerateShape:
    def __init__(self):
        self.position = [100, 100]
        self.dir_dict = {
            "r": (30, 0),
            "l": (-30, 0),
            "u": (0, -30),
            "d": (0, 30)
        }
        self.shape_str = [
            [["r"], ["d"], ["u", "r"], []],
            [["r"], ["r"], ["d"], []],
            [["r"], ["d"], ["r"], []],
            [["d"], ["r"], ["u"], []],
            [["r"], ["u"], ["r"], []],
            [["d"], ["u", "r"], ["r"], []],
            [["r"], ["r"], ["r"], []]
        ]
        self.rec_size = 30
        self.all_shapes = []
        self.make_all_shapes()

    def choose_random_shape(self):
        return random.choice(self.all_shapes)

    def make_all_shapes(self):
        for shape in self.shape_str:
            self.all_shapes.append(self.make_shape(shape))

    def make_rectangle(self, directions):
        start_x, start_y = self.position
        rec_points = [(start_x, start_y), (start_x + self.rec_size, start_y),
                      (start_x + self.rec_size, start_y + self.rec_size),
                      (start_x, start_y + self.rec_size), (start_x, start_y)]

        # Change starting position based on directions, (multiple to avoid duplicate draws
        for direction in directions:
            if not direction:
                continue

            self.position[0] += self.dir_dict[direction][0]
            self.position[1] += self.dir_dict[direction][1]
            rec_points.append((self.position[0], self.position[1]))

        return rec_points

    def back_to_start(self, str_dirs):
        # Do draws in opposite order to not draw weird lines
        points = []
        for direction in str_dirs:
            if not direction:
                continue

            direction_to_move = []
            match direction:
                case "u":
                    direction_to_move = self.dir_dict["d"]
                case "d":
                    direction_to_move = self.dir_dict["u"]
                case "l":
                    direction_to_move = self.dir_dict["r"]
                case "r":
                    direction_to_move = self.dir_dict["l"]

            self.position[0] += direction_to_move[0]
            self.position[1] += direction_to_move[1]

            points.append((self.position[0], self.position[1]))

        return points

    def make_shape(self, shape):
        new_shape = []

        # Draw main lines
        for rec_str in shape:
            new_shape.extend(self.make_rectangle(rec_str))

        # Draw back to start
        for rec_str in shape[::-1]:
            new_shape.extend(self.back_to_start(rec_str))

        print(self.position)

        # Reset start position
        self.position = [100, 100]

        return new_shape


class Render:
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

    def can_move(self, polygon) -> bool:
        if polygon.bottom == 700:
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

    def generate_random_shape(self):
        pass

    def execute(self):
        shape_gen = GenerateShape()
        while self.run:
            self.screen.fill((0, 0, 0))
            self.draw_game_area()
            pygame.draw.polygon(self.screen, (255, 255, 255), shape_gen.choose_random_shape(), width=4)

            self.handle_events()
            self.handle_fps()

            # Update the screen
            pygame.display.update()

            # Limit to 60 frames per second
            dt = self.clock.tick(2) / 1000
            self.timer -= dt

        self.cleanup()

    def cleanup(self):
        pygame.quit()


class Game:
    """
    Game state and logic

    Game will be a grid of 20x10 rows:20, cols:10

    New shapes will spawn in the first 2 rows in top

    New shape is max size 2x4

    Between every update the last spawned object will do collision calc
    to see if it can still drop down

    If row is full of numbers Tetris will happen and that line disappear
    Every shape above this tetris row will drop down and have to be calculated
    """

    def __init__(self):
        self.state = []
        self.init_state()

        # Shapes are max size 2x4
        self.all_shapes = [
            [
                [1, 1, 1, 0],
                [0, 1, 0, 0]
            ],
            [
                [1, 1, 1, 0],
                [0, 0, 1, 0]
            ],
            [
                [1, 1, 0, 0],
                [0, 1, 1, 0]
            ],
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0]
            ],
            [
                [0, 1, 1, 0],
                [1, 1, 0, 0]
            ],
            [
                [1, 1, 1, 0],
                [1, 0, 0, 0]
            ],
            [
                [1, 1, 1, 1],
                [0, 0, 0, 0]
            ]
        ]
        # ID counter for objects
        self.id_counter = 0
        self.game_end = False

        self.last_spawned_object_x = None
        self.last_spawned_object_y = None
        self.prev_color = None

        # Save color for each object id
        self.color_dict = {
            0: "blue",
        }

        self.colorer = Colors()
        self.spawn_new = True

    def init_state(self):
        for row in range(20):
            new_line = []
            for col in range(10):
                new_line.append(0)

            self.state.append(new_line)

    def gen_id(self):
        self.id_counter += 1
        return self.id_counter

    def random_color(self):
        # Choose new random color that is not the same as previous
        colors = ["white", "red", "green", "yellow", "orange"]
        new_color = random.choice(colors)
        while new_color == self.prev_color:
            new_color = random.choice(colors)

        self.prev_color = new_color
        return new_color

    def print_state(self):
        os.system("cls")
        for row in self.state:
            for cell in row:
                print(self.colorer.color_text(f" {cell} ", self.color_dict.get(cell)), end="")
            print("\n", end="")

        print("\n")

    def spawn_shape(self):
        random_shape = random.choice(self.all_shapes)
        new_id = self.gen_id()

        # Choose random col to spawn
        random_col = random.randint(0, 6)

        for row in range(len(random_shape)):
            for col in range(len(random_shape[0])):
                self.state[row][random_col + col] = 0 if random_shape[row][col] == 0 else new_id

        self.color_dict[new_id] = self.random_color()

    def find_rectangle(self, cur_x, cur_y, object_id):
        """
        Check the column and find the bottom rectangle belonging to object_id
        returns cur_x, cur_y, object_found
        :param cur_x: int
        :param cur_y: int
        :param object_id:int
        :return: (int, int, bool)
        """
        # Check current pos
        if self.state[cur_x][cur_y] == object_id:
            return cur_x, cur_y, True

        # First find the id on the col, max 4 steps up and down
        # Check up
        for i in range(4):
            if cur_x - i < 0:
                continue
            if self.state[cur_x - i][cur_y] == object_id:
                return cur_x - i, cur_y, True

        # Check down
        for i in range(4):
            if cur_x + i > 19:
                continue
            if self.state[cur_x + i][cur_y] == object_id:
                return cur_x + i, cur_y, True

        return cur_x, cur_y, False

    def find_shape(self, object_id):
        for row in range(20):
            for col in range(10):
                if self.state[row][col] == object_id:
                    return row, col

    def collision_detection(self, object_id):
        # First find shape start
        start_row, start_col = self.find_shape(object_id)

        # Figure out which squares below the shape have to be checked
        # From starting position start looping through columns and then through rows

        # STEPS:
        # 1. DO UNTIL ID FOUND:
        # 1.1 check current pos
        # 1.2 at current position if no object_id found go up max one step
        # 1.3 go down max one step
        # 1.4 if still no object_id found stop and return False
        # 2. go down until find either 0 or another object_id
        # 3. if another object_id was found return True
        # 4. Go to next column
        cur_row, cur_col = start_row, start_col
        for col in range(4):
            # Find bottom rectangle
            cur_row, cur_col, object_found = self.find_rectangle(cur_row, cur_col, object_id)

            # No more cols to check
            if not object_found:
                break

            # Go down until find 0 or other object
            while self.state[cur_row][cur_col] == object_id:
                # check if hit bottom
                if cur_row == 19:
                    return True

                cur_row += 1

            # Check if hit other object
            if self.state[cur_row][cur_col] != 0:
                return True

            cur_col += 1
            # Out of bounds
            if cur_col > 9:
                break

        return False

    def find_shape_reverse(self, object_id):
        for col in range(10):
            for row in range(19, -1, -1):
                if self.state[row][col] == object_id:
                    return row, col

    def lazy_game_end(self) -> bool:
        # Only going to check that if there is piece in the top 2 rows when trying to spawn new game ends
        for row in range(2):
            for col in range(10):
                if self.state[row][col] != 0:
                    return True

        return False

    def move(self, object_id):
        # loop through cols and rows[::-1] and move everything down
        # First find shape start
        start_row, start_col = self.find_shape_reverse(object_id)

        # Use same logic as in collision detection:
        # Find the column lowest rectangle, and from there start moving recs down and check above if another
        # one needs moving

        for col in range(4):
            # Out of bounds
            if start_col + col > 10:
                continue

            cur_row, cur_col = start_row, start_col + col
            # Find rectangle
            cur_row, cur_col, object_found = self.find_rectangle(cur_row, cur_col, object_id)

            if not object_found:
                break

            # Travel to bottom
            while self.state[cur_row][cur_col] == object_id:
                cur_row += 1

            # Move up once
            cur_row -= 1

            # Move every rectangle in the column down
            while True:
                # Move
                self.state[cur_row + 1][cur_col] = self.state[cur_row][cur_col]
                self.state[cur_row][cur_col] = 0

                # Check if more recs above, if so move pointer up
                if self.state[cur_row - 1][cur_col] != object_id:
                    break

                cur_row -= 1

    def update(self):
        # Spawn a new shape
        if self.spawn_new:
            if self.lazy_game_end():
                self.game_end = True
                return

            self.spawn_shape()
            self.spawn_new = False

        # Move primary target down
        for object_id in range(1, self.id_counter + 1):
            collision_bool = self.collision_detection(object_id)

            # If no collision move down
            if not collision_bool:
                self.move(object_id)

            # If collided object was last spawned, spawn new one
            elif object_id == self.id_counter:
                self.spawn_new = True


def main():
    game = Game()

    while not game.game_end:
        game.update()
        game.print_state()
        time.sleep(0.3)


if __name__ == '__main__':
    main()

    # renderer = Render()
    # renderer.execute()
