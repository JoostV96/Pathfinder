import numpy as np
import pygame
from tkinter import Tk
from tkinter import messagebox

DIM = 25  
WIDTH = 500
HEIGHT = 600
CELL_DIM = WIDTH // DIM

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Canvas:
    
    def __init__(self, dim):
        self.canvas = np.zeros((dim,dim)).astype(int)
        
    def insert(self, row, col, val):
        """Inserts a value on the canvas.""" 
        if row >= 0 and row < DIM and col >= 0 and col < DIM:
            self.canvas[row, col] = val
    
    def delete(self, row, col):
        """Deletes a value from the canvas."""
        self.canvas[row, col] = 0
    
    def reset(self, dim):
        """Resets the canvas."""
        self.canvas = np.zeros((dim, dim)).astype(int)
    
        
class Drawer:
    
    def __init__(self, screen):
        self.screen = screen
    
    def draw_canvas(self, canvas):
        """Draws the whole canvas"""
        self.screen.fill(WHITE)
        pygame.draw.line(self.screen, BLACK, (0,0), (0,WIDTH), 1)
        pygame.draw.line(self.screen, BLACK, (0,0), (WIDTH,0), 1)
        pygame.draw.line(self.screen, BLACK, (WIDTH,0), (WIDTH,WIDTH), 1)
        pygame.draw.line(self.screen, BLACK, (0,WIDTH), (WIDTH,WIDTH), 1)
        
        for row in range(DIM):
            for col in range(DIM):
                if canvas.canvas[row, col] == 1:  # Walls
                    pygame.draw.rect(self.screen, BLACK, (col*CELL_DIM, row*CELL_DIM, CELL_DIM, CELL_DIM),0)
                if canvas.canvas[row, col] == 2:  # Path
                    pygame.draw.rect(self.screen, RED, (col*CELL_DIM, row*CELL_DIM, CELL_DIM, CELL_DIM),0)
                if canvas.canvas[row, col] == 3:  # Open List
                    pygame.draw.rect(self.screen, GREEN, (col*CELL_DIM, row*CELL_DIM, CELL_DIM, CELL_DIM),0)
                if canvas.canvas[row, col] == 4:  # Closed List
                    pygame.draw.rect(self.screen, BLUE, (col*CELL_DIM, row*CELL_DIM, CELL_DIM, CELL_DIM),0)
                    
        self.draw_button(start_x=0, start_y=WIDTH+25, text="DONE", margin=0)
        self.draw_button(start_x=WIDTH-WIDTH//3, start_y=WIDTH+25, text="RESET", margin=0)

    def draw_button(self, start_x, start_y, text, margin):
        """Draws a "button" to the canvas."""
        pygame.draw.rect(self.screen, RED, (start_x, start_y, WIDTH//3, 50))
        pygame.draw.rect(self.screen, BLACK, (start_x, start_y, WIDTH//3, 50),3)
        myfont = pygame.font.SysFont(None, 72)
        textsurface = myfont.render(text, False, BLACK)
        pos = (start_x, start_y)
        self.screen.blit(textsurface, pos)
    
    @staticmethod
    def mouse_to_cell(pos_x, pos_y):
        return pos_x // CELL_DIM, pos_y // CELL_DIM


class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
    

def astar(canvas, drawer, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""
    
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)
    
    maze = canvas.canvas

    # Loop until you find the end
    while len(open_list) > 0:
        current_node = open_list[0]
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item

        open_list.remove(current_node)
        closed_list.append(current_node)
        canvas.insert(current_node.position[0], current_node.position[1], 4)

        # Found the goal
        if current_node == end_node:            
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares
            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            
            # Check bounds
            if node_position[0]>=len(maze) or node_position[0]<0 or node_position[1]>=len(maze[len(maze)-1]) or node_position[1]<0:
                continue
            # Check for walls
            if maze[node_position[0]][node_position[1]] == 1:
                continue

            # Create new node
            new_node = Node(current_node, node_position)
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    break
            else:
                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0]) ** 2) + \
                          ((child.position[1] - end_node.position[1]) ** 2)
                child.f = child.g + child.h
    
                # Child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g >= open_node.g:
                        break
                # Add the child to the open list
                else:
                    open_list.append(child)      
                    canvas.insert(child.position[0], child.position[1], 3)
                drawer.draw_canvas(canvas)
                pygame.display.update()
        
def main():
    """Main function of the program"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption('Canvas')
    
    canvas = Canvas(DIM)
    drawer = Drawer(screen)
    
    Tk().wm_withdraw() # To hide the main window
    messagebox.showinfo('Welcome','First, pick a start and end point and press "DONE"')
    start_chosen = False
    count = 0  # Need to get 2 points only
    
    # First loop to get the start and end point first
    while not start_chosen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start_chosen = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                (pos_x, pos_y) = pygame.mouse.get_pos()   
                col, row = drawer.mouse_to_cell(pos_x, pos_y) 
                if count < 2:
                    if row < DIM:
                        count = count + 1
                        canvas.insert(row, col, 2)
                if pos_x >= 400 and pos_x <= WIDTH and pos_y >= WIDTH:  # Reset button pressed
                    canvas.reset(DIM)
                    count = 0
                if pos_x >= 0 and pos_x <= WIDTH//3 and pos_y >= WIDTH if count == 2:  # Done button pressed
                    start_and_end_points = np.where(canvas.canvas == 2)
                    start_point = (start_and_end_points[0][0], start_and_end_points[1][0])
                    end_point = (start_and_end_points[0][1], start_and_end_points[1][1])
                    Tk().wm_withdraw()
                    messagebox.showinfo('Next','Now, draw some walls and press "DONE"')
                        start_chosen = True
        drawer.draw_canvas(canvas)
        pygame.display.update()
    
    done = False
    # After getting the start and end points, draw the walls and find the path
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if pygame.mouse.get_pressed()[0]:
                (pos_x, pos_y) = pygame.mouse.get_pos()   
                col, row = drawer.mouse_to_cell(pos_x, pos_y) 
                if row < DIM:
                    canvas.insert(row, col, 1)
                if pos_x >= 400 and pos_x <= WIDTH and pos_y >= WIDTH:  # Reset button pressed
                    canvas.reset(DIM)
                    canvas.insert(start_point[0], start_point[1], 2)
                    canvas.insert(end_point[0], end_point[1], 2)
                if pos_x >= 0 and pos_x <= WIDTH//3 and pos_y >= WIDTH:  # Done button pressed
                    res = astar(canvas, drawer, start_point, end_point)
                    if res:
                        for coord in res:
                            canvas.insert(coord[0], coord[1], 2)
                        canvas.canvas[canvas.canvas == 3] = 0
                        canvas.canvas[canvas.canvas == 4] = 0
                        drawer.draw_canvas(canvas)
                        pygame.display.update()
                        Tk().wm_withdraw() 
                        messagebox.showinfo('Result','The end point is {} blocks away'.format(len(res)))
                    else:
                        Tk().wm_withdraw() 
                        messagebox.showinfo('Result','No path found, make sure there is a gap between the walls')
    
        drawer.draw_canvas(canvas)
        pygame.display.update()
    pygame.quit()
    
if __name__ == "__main__":
    main()