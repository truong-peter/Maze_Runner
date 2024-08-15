import arcade
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Maze Runner"

CHARACTER_SCALING = 0.35
TILE_SCALING = 0.45
COIN_SCALING = 0.30
PLAYER_MOVEMENT_SPEED = 4.5
POS_SCALE = 35
POS_OFFSET = 100
NUM_OF_COINS = 3
MAZE_SIZE = 25



def mazeGeneration(width, height):
    '''Generate a maze 1=walls AND 0=paths'''
    # Fill Maze with all 1's
    maze = [[1 for y in range(width)]  for x in range(height)]  

    stack = []
    visited = []

    rndRow = random.randrange(0,height)
    rndCol = random.randrange(0,width)

    maze[rndRow][rndCol] = 0  
    stack.append((rndRow, rndCol)) 
    visited.append((rndRow, rndCol))
    
    # While the stack is not empty
    while stack:
        currCell = stack.pop()  
        neighbor = choose_neighbor(currCell, width, height, visited, maze)

        # If the current cell has any neighbours which have not been visited
        if neighbor is not None:
            stack.append(currCell) 
            maze[currCell[0]][currCell[1]] = 0  

            # Remove the wall at location of neighbor
            maze[(currCell[0] + neighbor[0]) // 2][(currCell[1] + neighbor[1]) // 2] = 0  
            stack.append(neighbor)  
            visited.append(neighbor) 

    # Add border walls
    # Horizontal Wall
    for x in range(width):
        maze[x][0] = 1
        maze[x][-1] = 1
    # Vertical Wall
    for y in range(height):
        maze[0][y] = 1
        maze[-1][y] = 1

    return maze

def choose_neighbor(cell, width, height, visited, maze):
    '''Return the valid direction in which the maze will continue in (NESW)'''
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]  # left, right, up, down
    random.shuffle(directions)

    for direction in directions:
        farNeighbor = (cell[0] + direction[0]*2, cell[1] + direction[1]*2)
        nearNeighbor = (cell[0] + direction[0], cell[1] + direction[1])
        if 1 <= farNeighbor[0] < width-1 and 1 <= farNeighbor[1] < height-1: #If possible x & y directions inside borders 
            if farNeighbor not in visited: # if far neighbor is new possible path return neighbor
                return farNeighbor
        
        if not farNeighbor:
            maze[nearNeighbor[0]][nearNeighbor[1]] = 0 # Break the wall edge case (prevents nonconnected paths)
    return None


class maze(arcade.Window):
 
    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.BURLYWOOD)

        self.scene = None
        self.player = None
        self.wall_collide = None

        # Store sprites in list to referrence later
        self.wall_list = None
        self.items_list = None
        self.camera = None
        self.score = 0

        # Background music initialization + looping
        # Commented out because unreliable on MacOS and dependenices are installed but still gives issues 
        #self.bg_music = arcade.Sound(":resources:music/funkyrobot.mp3", streaming=True)
        #self.bg_music.play(volume=0.10, loop = True)


    def setup(self):

        self.scene = arcade.Scene()
        self.dark_circle_sprite = arcade.Sprite("assets/dark_circle.png")

        # Initialize Sprites
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.items_list = arcade.SpriteList(use_spatial_hash=True)

        player_idle = ":resources:images/animated_characters/male_person/malePerson_idle.png"
        self.player = arcade.Sprite(player_idle, CHARACTER_SCALING)
        
        self.camera = arcade.Camera(self.width, self.height)

        maze = mazeGeneration(MAZE_SIZE,MAZE_SIZE)

        # Get all 0s empty spaces in the maze
        # Add walls in places where 1s exist
        emptySpace = []
        for x in range(len(maze)):
            for y in range(len(maze[x])): 
                if maze[x][y] == 1:
                    wall = arcade.Sprite(":resources:images/topdown_tanks/tileGrass2.png", TILE_SCALING)
                    wall.position = (((x * POS_SCALE) + POS_OFFSET), ((y * POS_SCALE) + POS_OFFSET))  
                    self.wall_list.append(wall)
                    self.scene.add_sprite("Walls", wall)  
                elif maze[x][y] == 0:
                    emptySpace.append((x,y))

        # Starting position of player in maze
        random.shuffle(emptySpace)
        coinList = emptySpace[0:NUM_OF_COINS+1]
        self.player.center_x = ((coinList[-1][0] * POS_SCALE) + POS_OFFSET)
        self.player.center_y = ((coinList[-1][1] * POS_SCALE) + POS_OFFSET)  
        coinList = coinList[0:NUM_OF_COINS]
        
        # Add coins to game collider
        for x,y in coinList:
            coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
            coin.position = (((x * POS_SCALE) + POS_OFFSET), ((y * POS_SCALE) + POS_OFFSET))  
            self.items_list.append(coin)
            self.scene.add_sprite("Coins", coin)
                    

        # Physics engine for walls (collide)
        self.wall_collide = arcade.PhysicsEngineSimple(self.player, self.scene.get_sprite_list("Walls"))
        
    def on_draw(self):
        '''Draw components onto canvas to make visible'''
        self.clear()
        self.wall_list.draw()
        self.items_list.draw()
        #self.dark_circle_sprite.draw()
        self.camera.use()
        self.player.draw()  
        self.center_camera_to_player()
       
        

    def on_update(self, delta_time):
        '''Any component that triggers or is triggered during runtime'''
        self.dark_circle_sprite.center_x = self.player.center_x
        self.dark_circle_sprite.center_y = self.player.center_y
        
        self.wall_collide.update()
        self.center_camera_to_player()
        coin_touch = arcade.check_for_collision_with_list(self.player,self.items_list)

        # Remove coin once player collects it
        for coin in coin_touch:
            coin.remove_from_sprite_lists()
            self.score += 1

        # Win condition
        if self.score == NUM_OF_COINS:
            self.center_camera_to_player()


    def center_camera_to_player(self):
        '''Get (x,y) of player sprite. Used for centering dark_circle and displaying text'''
        screen_center_x = self.player.center_x 
        screen_center_y = self.player.center_y

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

        arcade.draw_text(f"Coins Collected: {self.score}/{NUM_OF_COINS}", start_x=screen_center_x + 700, start_y=screen_center_y + 630, color=arcade.color.WHITE, font_size=20)
        if self.score == NUM_OF_COINS:
            arcade.draw_text(f"You Win!" , start_x=screen_center_x + 440, start_y=screen_center_y + 550, color=arcade.color.BLUE, font_size=20)

    def on_key_press(self, key, modifiers):

        # Animations for player based on movement
        player_left = arcade.load_texture(":resources:images/animated_characters/male_person/malePerson_walk2.png", flipped_horizontally= True)
        player_right = arcade.load_texture(":resources:images/animated_characters/male_person/malePerson_walk2.png")
        player_down = arcade.load_texture(":resources:images/animated_characters/male_person/malePerson_walk0.png")
        player_up = arcade.load_texture(":resources:images/animated_characters/male_person/malePerson_climb1.png")

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = PLAYER_MOVEMENT_SPEED
            self.player.texture = player_up

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = -PLAYER_MOVEMENT_SPEED
            self.player.texture = player_down

        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
            self.player.texture = player_left

        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
            self.player.texture = player_right
            

    def on_key_release(self, key, modifiers):

        player_idle = arcade.load_texture(":resources:images/animated_characters/male_person/malePerson_idle.png")

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = 0
            self.player.texture = player_idle

        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = 0
            self.player.texture = player_idle
            
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = 0
            self.player.texture = player_idle
            
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = 0
            self.player.texture = player_idle

def main():
    window = maze()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()