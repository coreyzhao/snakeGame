# Import from arcade
import arcade
import random
import queue
import sys

# Grid size (variables)
MARGIN = 5
GRID_WIDTH = 20
GRID_HEIGHT = 20
ROWS = 20
COLUMNS = 20

# Screen size (variables)
SCREEN_WIDTH = GRID_WIDTH * COLUMNS + MARGIN * COLUMNS
SCREEN_HEIGHT = GRID_HEIGHT * ROWS + MARGIN * ROWS

# Player color
PLAYER_COLOR = (arcade.color.BLUE)

# Tile color
TILE_COLOR = (161, 214, 226)

# Background color
BACKGROUND_COLOR = (25, 149, 173)


# Grid game
class Grid_Game(arcade.Window):

    def __init__(self, width, height, title):

        super().__init__(width, height, title)

        # Background color
        arcade.set_background_color(BACKGROUND_COLOR)

        # Speed
        self.board = Grid(ROWS, COLUMNS)
        self.move_timer = 0
        self.fixed_timer = 0.2
        self.last_direction = (0, 0)
        self.buffer = queue.Queue()


    # Start
    def on_draw(self):
        arcade.start_render()
        self.board.draw_grid()

    # Moving keys
    def on_key_press(self, symbol, modifiers ):

        # Exit game
        if (symbol == arcade.key.ESCAPE):
            sys.exit()

        # Keys
        new_direction = self.last_direction

        if(symbol == arcade.key.D):
            new_direction = (1, 0)

        elif(symbol == arcade.key.A):
            new_direction = (-1, 0)

        elif(symbol == arcade.key.S):
            new_direction = (0, -1)

        elif(symbol == arcade.key.W):
            new_direction = (0, 1)


        self.buffer.put(new_direction)

    def auto_move(self):

        self.board.move(*self.last_direction)

    def on_update(self, delta_time):

        self.move_timer += delta_time
        self.fixed_timer = 0.2 - self.board.score * 0.01


        if (self.move_timer > self.fixed_timer):
            self.move_timer = 0
            self.auto_move()

        if (self.board.game_over == True):
            self.board = Grid(COLUMNS, ROWS)
            self.last_direction = (0, 0)



        new_direction = 0,0

        try:
            new_direction = self.buffer.get_nowait()
            have_input = True

        except queue.Empty:
            have_input = False
            pass

        # Non suicide
        if have_input and new_direction != tuple(x *-1 for x in self.last_direction):
            self.last_direction = new_direction

# Draw grid
class Grid:
    def __init__(self, grid_width, grid_height):


        # Starting position
        x1 = ROWS // 2
        y1 = COLUMNS // 2

        self.grid_width = grid_width
        self.grid_height = grid_height

        # Make grid
        self.grid = []

        self.score = 0

        # Columns
        for i in range(COLUMNS):

            column = []

            # Rows
            for tiles in range(ROWS):

                column.append(None)

            self.grid.append(column)

        # Creating our player using tile object
        self.player = Tile(x1, y1, PLAYER_COLOR)

        # Place player in the grid
        self.grid[x1][y1] = self.player

        # Spawn token
        self.spawn_token()

        self.game_over = False

    def draw_tile(self, x, y, color):
        arcade.draw_rectangle_filled(GRID_WIDTH // 2 + MARGIN // 2 + MARGIN * x + GRID_WIDTH * x,
                                                 GRID_HEIGHT // 2 + MARGIN // 2 + MARGIN * y + GRID_HEIGHT * y,
                                                 GRID_HEIGHT, GRID_WIDTH, color)



    def draw_grid(self):

        # Draw tiles
        for x, columns in enumerate(self.grid):
            for y, tile in enumerate(columns):
                if (tile == None):
                    self.draw_tile(x, y, TILE_COLOR)

                else:
                    self.draw_tile(x, y, tile.color)



    def move(self, x, y):

        # Hitting wall = go other side
        new_x = self.player.x + x
        new_y = self.player.y + y


        if (new_x >= COLUMNS):
            self.game_over = True
            new_x = 0
            print(self.score)

        if (new_x <= - 1):
            self.game_over = True
            new_x = COLUMNS - 1
            print(self.score)

        if (new_y >= ROWS):
            self.game_over = True
            new_y = 0
            print(self.score)

        if (new_y <= - 1):
            self.game_over = True
            new_y = ROWS - 1
            print (self.score)

        next_tile = self.grid[new_x][new_y]

        #What to do if next_tile is empty
        if (next_tile == None):
            snake = [self.player]

            # Build snake
            while snake[-1].next_coords_x is not None:

                # Going deeper
                next_snake = self.grid[snake[-1].next_coords_x][snake[-1].next_coords_y]
                snake.append(next_snake)

            self.grid[snake[-1].x][snake[-1].y] = None

            # Set player
            if len(snake) > 1:
                snake[-2].next_coords_x = None
                snake[-2].next_coords_y = None

                next_coords_x = self.player.x
                next_coords_y = self.player.y

            # If snake is one element
            else:
                next_coords_x = None
                next_coords_y = None

            self.player = Tile(new_x, new_y, PLAYER_COLOR, False, next_coords_x, next_coords_y)
            self.place_player(self.player)

        #What to do if next tile is a token
        elif (next_tile.is_token == True):
            self.extend_player(new_x, new_y)
            self.spawn_token()

        #What to do if hit anything else
        else:
            self.game_over = True
            if (self.score > 1):
                print(self.score)


    # Extend snake
    def extend_player(self, x, y):

        new_player_head = Tile(x, y, PLAYER_COLOR, False, self.player.x, self.player.y)

        self.player = new_player_head

        self.place_player(self.player)

        #self.player = Tile(self.player.x, self.place_tile(self.player)

    def place_player(self, tile):

        self.grid[self.player.x][self.player.y] = tile

    def spawn_token(self):

        token_place_found = False

        while not token_place_found:
            x = random.randint(0,COLUMNS - 1)
            y = random.randint(0, ROWS - 1)

            if (self.grid[x][y] == None):
                token_place_found = True


        self.grid[x][y] = Tile(x, y, arcade.color.GOLD, True)

        self.score += 1


class Tile:

    # Next_coords points to next element
    def __init__(self, x, y, color, is_token=False, next_coords_x=None, next_coords_y=None):
        self.x = x
        self.y = y
        self.color = color
        self.is_token = is_token
        self.next_coords_x = next_coords_x
        self.next_coords_y = next_coords_y

        next_elem = None


# Screen size
def main():

    window = Grid_Game(SCREEN_WIDTH, SCREEN_HEIGHT, "Game")

    arcade.run()

if __name__ ==  "__main__":
    main()