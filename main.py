from functools import total_ordering

import pygame
from typing import List, Tuple
import random
import time
from color import Colors
import os

"""
Game area: Leave two rows to top for generation of cubes, 20x10 area,
600x300, 30x30 per rectangle 
"""


class Render:
    def __init__(self, engine):
        pygame.init()

        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 800
        # Setup screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        # Create a clock to manage the frame rate
        self.clock = pygame.time.Clock()
        # Create a font object for rendering the FPS
        self.font = pygame.font.SysFont(None, 36)

        # Game engine
        self.engine: Engine = engine
        self.timer = 0
        self.move_timer = 0
        # List for squares
        self.run = True

    def handle_events(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] and self.move_timer <= 0:
            self.engine.manual_move("left")
            self.move_timer = 0.08
        elif key[pygame.K_RIGHT] and self.move_timer <= 0:
            self.engine.manual_move("right")
            self.move_timer = 0.08

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

    def handle_fps(self):
        # Calculate and display FPS
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))  # White color
        self.screen.blit(fps_text, (10, 10))  # Draw the FPS text in the top left corner

    def draw_game_area(self):
        # Vertical lines
        pygame.draw.line(self.screen, (255, 255, 255), (250, 0), (250, 800), 5)
        pygame.draw.line(self.screen, (255, 255, 255), (550, 0), (550, 800), 5)
        # Horizontal lines
        pygame.draw.line(self.screen, (255, 255, 255), (250, 100), (550, 100), 5)
        pygame.draw.line(self.screen, (255, 255, 255), (250, 700), (550, 700), 5)

    def draw_shapes(self):
        cur_x = 250.0
        cur_y = 100.0

        for row in self.engine.state:
            for cell in row:
                if cell != 0:
                    rectangle = pygame.Rect((cur_x, cur_y, 30, 30))
                    color = self.engine.color_dict.get(cell)
                    pygame.draw.rect(self.screen, color, rectangle, border_radius=6)

                cur_x += 30

            cur_x -= 300
            cur_y += 30

    def execute(self):
        while self.run:
            self.screen.fill((0, 0, 0))
            self.draw_game_area()
            self.draw_shapes()

            self.handle_events()
            self.handle_fps()

            # Update the screen
            pygame.display.update()
            # Update the engine
            if self.timer <= 0:
                self.engine.update()
                self.timer = 0.3

            # Limit to 60 frames per second
            dt = self.clock.tick(60) / 1000
            self.timer -= dt
            self.move_timer -= dt

        self.cleanup()

    def cleanup(self):
        pygame.quit()


class Engine:
    """
    Game state:

    Game will be a grid of 20x10 rows:20, cols:10
    New shapes will spawn in the first 2 rows in top
    New shape is max size 2x4

    Update loop (in order):

    1. If tetris mode: Keep only updating the falling pieces and return
    2. Primary shape exists: Keep dropping the primary piece, also if tetris mode can happen
    3. No primary shape: generate one

    Score and level system:

    Every 10 tetris cleared a new level will begin
    Score is calculated based on this formula points_for_tetris_lines * (level + 1)
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

        # Save the coordinates for top left corner of the shape
        self.last_spawned_object_id = None
        self.last_spawned_object_row = None
        self.last_spawned_object_col = None
        self.prev_color = None

        self.prev_tetris_row = 0
        self.total_tetris_rows = 0

        self.level = 0
        self.score = 0

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
        # os.system("cls")
        for row in self.state:
            for cell in row:
                print(self.colorer.color_text(f" {cell} ", self.color_dict.get(cell)), end="")
            print("\n", end="")

        print("\n")

    def assign_last_spawn_object_vars(self, random_shape, rand_col) -> None:
        for col in range(4):
            for row in range(1, -1, -1):
                if random_shape[row][col] != 0:
                    self.last_spawned_object_row = row
                    self.last_spawned_object_col = col + rand_col
                    return

    def spawn_shape(self):
        random_shape = random.choice(self.all_shapes)
        # random_shape: List[List[int]] = self.all_shapes[4]

        new_id = self.gen_id()

        # Choose random col to spawn
        random_col = random.randint(0, 6)

        # Save the position of spawned object for fast access later on (BOTTOM_LEFT_CORNER)
        self.assign_last_spawn_object_vars(random_shape, random_col)
        self.last_spawned_object_id = new_id

        for row in range(len(random_shape)):
            for col in range(len(random_shape[0])):
                # Spawn rectangle to the shape
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

    def reset_falling_object_vars(self, object_id: int) -> None:
        # If the main falling object hit bottom make fast access coordinates None
        if object_id == self.last_spawned_object_id:
            self.last_spawned_object_id = None
            self.last_spawned_object_row = None
            self.last_spawned_object_col = None

    def collision_detection_vertical(self, object_id):
        # First find shape start
        if object_id == self.last_spawned_object_id:
            start_row = self.last_spawned_object_row
            start_col = self.last_spawned_object_col
        else:
            start_row, start_col = self.find_shape_reverse(object_id)

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
                    self.reset_falling_object_vars(object_id)
                    return True

                cur_row += 1

            # Check if hit other object
            if self.state[cur_row][cur_col] != 0:
                self.reset_falling_object_vars(object_id)
                return True

            cur_col += 1
            # Out of bounds
            if cur_col > 9:
                break

        return False

    def collision_detection_horizontal(self, start_row, start_col, side):
        """
        Check for horizontal collision detection, start_row and start_col the most left or right bottom
        rectangle of shape
        Read collision_detection_vertical for more info
        :param start_row:
        :param start_col:
        :param side: str, which side to check for collision
        :return: bool, True if collision happened
        """
        # Check every surface from left or right side depending on direction
        # Check each row separately
        cur_row, cur_col = start_row, start_col
        cur_row -= 3
        for row in range(4):
            if cur_row < 0:
                cur_row += 1
                continue

            id_found = False

            # Go left max 4 in that row until object id found, if not found stop because shape ended and return
            for col in range(4):
                if cur_col < 0 or cur_col > 9:
                    continue

                if self.state[cur_row][cur_col] == self.last_spawned_object_id:
                    id_found = True
                    break

                if side == "right":
                    cur_col -= 1
                elif side == "left":
                    cur_col += 1

            if not id_found:
                cur_row += 1
                cur_col = start_col
                continue

            # Check if collision happens
            if side == "right":
                if cur_col + 1 == 10 or self.state[cur_row][cur_col + 1] != 0:
                    return True
            elif side == "left":
                if cur_col - 1 == -1 or self.state[cur_row][cur_col - 1] != 0:
                    return True

            cur_row += 1
            cur_col = start_col

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

    def bottom_left_rectangle(self, cur_row, cur_col, object_id) -> (int, int):
        # Start looking for object id 4 cols from the left to right
        best_position = [cur_row, cur_col]

        def dfs(row, col, object_id):
            if row < 0 or row > 19 or col < 0 or col > 9:
                return

            # If object_id not found return
            if self.state[row][col] != object_id:
                return

            # If found more left object
            if col < best_position[1]:
                best_position[0], best_position[1] = row, col
            # If found more bottom left object
            elif col == best_position[1] and row > best_position[0]:
                best_position[0], best_position[1] = row, col

            # Travel left, top, bottom
            moves = [(0, -1), (-1, 0), (1, 0)]
            for move in moves:
                dfs(row + move[0], col + move[1], object_id)

        dfs(cur_row, cur_col, object_id)

        return best_position[0], best_position[1]

    def bottom_column_position(self, cur_row, cur_col, object_id):
        # Get to the bottom in this col
        for _ in range(4):
            # First there is object below
            if cur_row + 1 <= 19 and self.state[cur_row + 1][cur_col] == object_id:
                cur_row += 1
            # We are at lowest
            elif self.state[cur_row][cur_col] == object_id:
                break
            # Have to go up to find the bottom
            elif cur_row - 1 >= 0:
                cur_row -= 1

        return cur_row, cur_col

    def move(self, object_id):
        # loop through cols and rows[::-1] and move everything down
        # First find shape start
        if object_id == self.last_spawned_object_id:
            start_row = self.last_spawned_object_row
            start_col = self.last_spawned_object_col
        else:
            start_row, start_col = self.find_shape_reverse(object_id)

        # 1. Find the bottom left rectangle if not primary object
        if object_id != self.last_spawned_object_id:
            start_row, start_col = self.bottom_left_rectangle(start_row, start_col, object_id)

        # 2. Col by col move every id in that col down
        cur_row, cur_col = start_row, start_col
        for col in range(4):
            # Out of bounds
            if cur_col < 0 or cur_col > 9:
                cur_col += 1
                continue

            # Get to the bottom in this col
            cur_row, cur_col = self.bottom_column_position(cur_row, cur_col, object_id)
            for row in range(4):
                if cur_row < 0 or cur_row > 19:
                    cur_row -= 1
                    continue

                # Do not move 0
                if self.state[cur_row][cur_col] == 0:
                    cur_row -= 1
                    continue

                self.state[cur_row + 1][cur_col] = self.state[cur_row][cur_col]
                self.state[cur_row][cur_col] = 0
                cur_row -= 1

            cur_row += 4
            cur_col += 1

        # Update the position for falling object
        if object_id == self.last_spawned_object_id:
            self.last_spawned_object_row += 1

    def manual_move(self, direction: str) -> None:
        """
        Move falling shape to given direction by one block
        :param direction: Left or right
        :return:
        """
        if self.last_spawned_object_id is None:
            return

        # Based on left or right get to most left or right column of the shape
        start_row = self.last_spawned_object_row
        start_col = self.last_spawned_object_col

        if direction == "right":
            most_right = [start_row, start_col]

            def dfs(row, col, object_id, visited_nodes: List):
                # Check out of bounds
                if not (0 <= row <= 19) or not (0 <= col <= 9):
                    return
                # Check if path still valid
                if self.state[row][col] != object_id:
                    return
                if (row, col) in visited_nodes:
                    return

                if col > most_right[1]:
                    most_right[0], most_right[1] = row, col

                # Travel right, top, bottom
                moves = [(0, 1), (-1, 0), (1, 0)]
                for move in moves:
                    visited_nodes.append((row, col))
                    dfs(row + move[0], col + move[1], object_id, visited_nodes)
                    visited_nodes.pop()

            dfs(start_row, start_col, self.last_spawned_object_id, [])
            start_row, start_col = most_right[0], most_right[1]

        # Make certain object is not horizontally hitting something
        if self.collision_detection_horizontal(start_row, start_col, direction):
            print("object hitting wall")
            return

        # Move every id column per column to right or left
        cur_row, cur_col = start_row, start_col
        for col in range(4):
            if cur_col < 0 or cur_col > 9:
                cur_col = cur_col - 1 if direction == "right" else cur_col + 1
                continue

            cur_row, cur_col = self.bottom_column_position(cur_row, cur_col, self.last_spawned_object_id)
            for row in range(4):
                if cur_row < 0 or cur_row > 19:
                    cur_row -= 1
                    continue
                # Do not move 0
                if self.state[cur_row][cur_col] != self.last_spawned_object_id:
                    cur_row -= 1
                    continue

                if direction == "right":
                    self.state[cur_row][cur_col + 1] = self.state[cur_row][cur_col]
                elif direction == "left":
                    self.state[cur_row][cur_col - 1] = self.state[cur_row][cur_col]

                self.state[cur_row][cur_col] = 0
                cur_row -= 1

            cur_row += 4
            cur_col = cur_col - 1 if direction == "right" else cur_col + 1

        self.last_spawned_object_col = self.last_spawned_object_col + 1 if direction == "right" \
            else self.last_spawned_object_col - 1

    def manual_rotate(self, direction: str) -> None:
        """
        Rotates the falling shape clockwise or counter-clockwise
        :param direction: clock
        :return:
        """
        pass

    def tetris(self) -> None:
        tetris_count = 0

        # scan whole thing
        for row in range(20):
            if 0 in self.state[row]:
                continue

            self.prev_tetris_row += 1
            for col in range(10):
                self.state[row][col] = 0

        if tetris_count != 0:
            self.total_tetris_rows += tetris_count
            match tetris_count:
                case 1:
                    self.score = 40 * (self.level + 1)
                case 2:
                    self.score = 80 * (self.level + 1)
                case 3:
                    self.score = 300 * (self.level + 1)
                case 4:
                    self.score = 1200 * (self.level + 1)

            # Update level


    def update(self):
        """
        Steps to happen
        1. Loop until tetris over update all object to fall
        2. Move primary object if exists
        3. Spawn new primary object if not exists
        :return:
        """
        # Use prev_tetris count to know how many updates to skip for falling tetris parts
        if self.prev_tetris_row > 0:
            for object_id in range(1, self.id_counter + 1):
                collision_bool = self.collision_detection_vertical(object_id)

                # If no collision move down
                if not collision_bool:
                    self.move(object_id)

            self.prev_tetris_row -= 1
            # Check for cascading tetris
            if self.prev_tetris_row == 0:
                self.tetris()

            return

        # Move primary down
        if self.last_spawned_object_id:
            collision_bool = self.collision_detection_vertical(self.last_spawned_object_id)

            # If no collision move down
            if not collision_bool:
                self.move(self.last_spawned_object_id)
            # If collided object was last spawned, spawn new one
            else:
                # Check for tetris
                self.tetris()
                self.spawn_new = True

        # Spawn a new shape
        if self.spawn_new:
            if self.lazy_game_end():
                self.game_end = True
                return

            self.spawn_shape()
            self.spawn_new = False

def main():
    game = Engine()

    while not game.game_end:
        game.update()
        game.print_state()
        time.sleep(0.5)
        # break


if __name__ == '__main__':
    # main()

    engine = Engine()
    renderer = Render(engine)
    renderer.execute()
