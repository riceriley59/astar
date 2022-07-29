#using pygame for GUI
import pygame
import math

#using a Queue as my data structure for this project
from queue import PriorityQueue

#basic pygame setup
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

#giving color variables values to make it easier
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
GREY = (128,128,128)
ORANGE = (255,165,0) 
TURQUOISE = (64,224,208)


#created a class spot which represents one node in the graph
class Spot:
	#construct each object and intialize it's position
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	#methods to get information about the object
	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == PURPLE

	def reset(self):
		self.color = WHITE

	#change colors based on state
	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	#draw method which draws a rectangle with all the attributes given
	def draw(self,win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	#create a neighbors dictionary and add a neighbor for each object in all 4 
	# directions next to it and then check to make sure that it's not a barrier 
	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
			self.neighbors.append(grid[self.row - 1][self.col])
		
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
			self.neighbors.append(grid[self.row][self.col + 1])
		
		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

#this function returns the distance from two points
def h(p1,p2):
	x1,y1 = p1
	x2,y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

#this looks at where the algorithm was before an then turns that cube into a path
def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

#this is the function which implements the astar algorithm
def algorithm(draw, grid, start, end):
	#initiate the queue then put the start spot along with the count in the queue
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	#need a came_from dictionary wich stores all the spaces that have been visited
	came_from = {}

	#initiate the gscores of all spots with infinity which is essentially the 
	# path cost of a node
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0

	#initialize the fscore of all spots with the infinity. This is the heuristic
	#score plus the g-score so the estimated distance plus the path cost of a node
	#and is used to value the effectiveness of each node in the ability to get to 
	#the end
	f_score = {spot: float("inf") for row in grid for spot in row}
	#Get the heuristic value or distance between the start and end position since
	#the g-score is zero the f_score in the beginning is just the heuristic score
	f_score[start] = h(start.get_pos(), end.get_pos())


	open_set_hash = {start}

	#make sure the queue isn't empty and if it is return False and if it isn't then 
	#keep on looping through each node until the end is met
	while not open_set.empty():
		#this basically looks for events and quits the application if the user
		#presses the red x button on the window to end it
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		#you want to get the next node and then remove it from the hash table
		current = open_set.get()[2]
		open_set_hash.remove(current)

		#if the next node is an end path then you just want to draw the path and 
		#end the program
		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		#loop through the neighbors dictionary for the current spot
		for neighbor in current.neighbors:
			#the neighbors temporary is the nodes score plus one because it would be one more
			#step if you go towards a neighbor
			temp_g_score = g_score[current] + 1

			#if temporary score is less than the g_score if not then keep on looping 
			#there will always be at least one neighbor who meets this condition
			if temp_g_score < g_score[neighbor]:
				#put the current node in the came_from dictionary
				came_from[neighbor] = current
				
				#set the neighbor's g_score value to temporary g_score since we made the 
				#step and added one
				g_score[neighbor] = temp_g_score

				#then set the f_score adding the temp g_score and the current heuristic value
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

				#if the neighbor isn't in the hashtable then add to the count and then put the neighbor in the
				# queue and add to the hashtable and make it an open spot 
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()
		#call draw function after this
		draw()

		#if the current spot is not equal to the start spot then make it closed
		if current != start:
			current.make_closed()
	return False

#function that automatically makes grid of spot objects given the parameter rows and width
def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)
	return grid

#function that draws grid using pygame lines
def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0,i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

#draw function that basically updates the screen every function call
def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()

#get position of mouse when clicking
def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col

#main control function needs a win object and a width parameter
def main(win, width):
	#specify amount of rows and then make a grid with that amount
	ROWS = 50
	grid = make_grid(ROWS, width)

	#initialize some variables
	start = None
	end = None
	run = True
	started = False

	#initialize main run loop
	while run:
		#call draw function to draw the grid
		draw(win, grid, ROWS, width)

		#checks to events in pygame for user inputs
		for event in pygame.event.get():
			#if user quits then quit
			if event.type == pygame.QUIT:
				run = False

			#if the astar was started then continue looping until it ends
			if started:
				continue

			#if the user left clicks then make that spot object the start node
			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()
				elif not end and spot != start:
					end = spot
					end.make_end()
				elif spot != end and spot != start:
					spot.make_barrier()

			#if the user right clicks then make that spot object the end node
			elif pygame.mouse.get_pressed()[2]:
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				if spot == end:
					end = None
				
			#if a key is pressed
			if event.type == pygame.KEYDOWN:
				#if the space bar is pressed and the algorithm hasn't started then 
				#update the neighbors dictionary for each spot object then start
				#the astar algorithm
				if event.key == pygame.K_SPACE and not started:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
			
			#if key is pressed
			if event.type == pygame.KEYDOWN:
				#if c key is pressed then clear the screen and make a new grid 
				#with no start and end objects
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)

	#quit the program if run loop is broken out of
	pygame.quit()

#call main function with WIN and WIDTH variables which were specified at top
main(WIN, WIDTH)