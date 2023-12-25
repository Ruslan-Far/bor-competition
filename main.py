#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor)
from pybricks.parameters import Port, Direction, Color
from pybricks.tools import wait

# параметры для работы с цветами
BLACK = 0
BLUE = 1
GREEN = 2
YELLOW = 3
RED = 4
WHITE = 5
BROWN = 6

V_MIN = 15
V_MIN_BROWN = 35
S_MIN = 50

red_h = [300, 360]
blue_h = [170, red_h[0] - 1]
green_h = [90, blue_h[0] - 1]
yellow_h = [40, green_h[0] - 1]
red_h_2 = [0, yellow_h[0] - 1]
# ----------------------------------------------------------

# инициализация девайсов
ev3 = EV3Brick()
MOTOR_A = Motor(Port.A, Direction.COUNTERCLOCKWISE)
MOTOR_D = Motor(Port.D, Direction.COUNTERCLOCKWISE)
color_sensor = ColorSensor(Port.S1)
# ----------------------------------------------------------

ROWS = 5
COLS = 4

# инициализация скоростей
SPEED_A = 600
SPEED_D = 300
# ----------------------------------------------------------

# инициализация текущего состояния
current_row = 0
current_col = 0
current_x = 0 # mm
current_y = 0 # mm
current_link_1_d = 0
current_link_2_d = 0
# ----------------------------------------------------------

is_dropped = False
map_red_field = []

class Point:
	link_0_alpha = 0 # degrees
	link_0_a = 0 # mm
	link_1_theta = 0 # degrees
	link_1_alpha = -90 # degrees
	link_1_a = 110 # mm
	link_2_theta = 0 # degrees

	def __init__(self, x, y, link_1_d, link_2_d):
		self.x = x
		self.y = y
		self.link_1_d = link_1_d
		self.link_2_d = link_2_d


def init_map():
	row = current_row
	y = current_y
	link_1_d = current_link_1_d
	while row < ROWS:
		map_red_field.append([])
		col = current_col
		x = current_x
		link_2_d = current_link_2_d
		while col < COLS:
			map_red_field[row].append(Point(x, y, link_1_d, link_2_d))
			x += 51
			if col == 0:
				link_2_d += 175
			else:
				link_2_d += 150
			col += 1
		y += 65
		link_1_d += 195
		row += 1


def update_current_state(row, col):
	global current_row
	global current_col
	global current_x
	global current_y
	global current_link_1_d
	global current_link_2_d
	current_row = row
	current_col = col
	current_x = map_red_field[row][col].x
	current_y = map_red_field[row][col].y
	current_link_1_d = map_red_field[row][col].link_1_d
	current_link_2_d = map_red_field[row][col].link_2_d


def move_to(row, col):
	if current_row != row:
		if not is_dropped:
			move_link_2_d_to(row, 0)
		move_link_1_d_to(row, col)
	move_link_2_d_to(row, col)
	update_current_state(row, col)


def move_link_1_d_to(row, col):
	run_motor(MOTOR_D, SPEED_D, map_red_field[row][col].link_1_d)


def move_link_2_d_to(row, col):
	run_motor(MOTOR_A, SPEED_A, map_red_field[row][col].link_2_d)


def run_motor(motor, speed, angle):
	motor.run_target(speed, angle)
	wait(100)


def conv_rgb2hsv(rgb):
	r = rgb[0] / 100
	g = rgb[1] / 100
	b = rgb[2] / 100
	cmax = max(r, g, b)
	cmin = min(r, g, b)
	delta = cmax - cmin
	# ------------------------ H
	if delta == 0:
		h = 0
	elif cmax == r:
		h = 60 * ((g - b) / delta % 6)
	elif cmax == g:
		h = 60 * ((b - r) / delta + 2)
	else:
		h = 60 * ((r - g) / delta + 4)
	# ------------------------ S
	if cmax == 0:
		s = 0
	else:
		s = delta / cmax
	# ------------------------ V
	v = cmax
	return [int(round(h)), int(round(100 * s)), int(round(100 * v))]


def detect_color():
	rgb = color_sensor.rgb()
	hsv = conv_rgb2hsv(rgb)
	print(hsv)
	if hsv[2] < V_MIN:
		return BLACK
	if hsv[1] < S_MIN:
		return WHITE
	if hsv[0] >= blue_h[0] and hsv[0] <= blue_h[1]:
		return BLUE
	if hsv[0] >= green_h[0] and hsv[0] <= green_h[1]:
		return GREEN
	if hsv[0] >= yellow_h[0] and hsv[0] <= yellow_h[1]:
		return YELLOW
	if hsv[0] >= red_h[0] and hsv[0] <= red_h[1]:
		if hsv[2] < V_MIN_BROWN:
			return BROWN
		return RED
	if hsv[0] >= red_h_2[0] and hsv[0] <= red_h_2[1]:
		if hsv[2] < V_MIN_BROWN:
			return BROWN
		return RED
	return -1


def drop():
	global current_row
	global current_col
	global is_dropped
	drop_link_1_d = 100
	if current_col == 0:
		drop_link_2_d = 70
	else:
		drop_link_2_d = 40
	run_motor(MOTOR_A, SPEED_A, current_link_2_d + drop_link_2_d)
	run_motor(MOTOR_D, SPEED_D, current_link_1_d + drop_link_1_d)
	current_row += 100
	is_dropped = True


def process_line_0(target_color):
	col = 1
	while col <= COLS:
		if detect_color() == target_color:
			drop()
			break
		elif col != COLS:
			move_to(0, col)
		col += 1


def run():
	global is_dropped
	init_map()
	target_color = 0

	ev3.speaker.beep(500, 200)
	process_line_0(target_color)
	row = 1
	current_color = target_color
	while row < ROWS:
		move_to(row, current_color % COLS)
		current_color = detect_color()
		if current_color == target_color:
			drop()
		else:
			is_dropped = False
		row += 1
	is_dropped = False
	move_to(0, 0)
	ev3.speaker.beep(500, 200)


# запуск программы
run()
# ----------------------------------------------------------


# i = 0
# repeats = 7
# ev3.speaker.beep(1000, 700)
# while i < repeats:

	
# 	# wait(1000)
# 	# ev3.screen.clear()
# 	# ev3.screen.print(detect_color())
# 	print(detect_color())



# 	if i + 1 != repeats:
# 		ev3.speaker.beep(600, 300)
# 		wait(10000)

# 	i += 1

# i = 0
# while i < 3:
# 	ev3.speaker.beep(300, 100)
# 	wait(500)
# 	i += 1


# just moving

# ev3.speaker.beep(300, 100)
# run_motor(MOTOR_A, SPEED_A, -175)
# run_motor(MOTOR_A, -15)
# run_motor(motor_d, 780)
# wait(5000)
# run_motor(MOTOR_D, 100)
# wait(5000)
# run_motor(MOTOR_D, 195)
# wait(5000)
# run_motor(MOTOR_D, 0)
# ev3.speaker.beep(300, 100)


def snake():
	angle_d = 190
	i = 0
	ev3.speaker.beep(300, 100)
	while i < 2:
		run_motor(motor_a, angle_a)
		run_motor(motor_d, angle_d)
		motor_d.reset_angle(0)
		run_motor(motor_a, 0)
		run_motor(motor_d, angle_d)
		motor_d.reset_angle(0)
		i += 1
	run_motor(motor_a, angle_a)
	ev3.speaker.beep(300, 100)


def snake_improved():
	a_a = 0
	a_d = 0
	i = 0
	reps_i = 5
	reps_j = 3
	koef_a = -1
	ev3.speaker.beep(300, 100)
	while i < reps_i:
		j = 0
		koef_a = -koef_a
		print(detect_color())
		while j < reps_j:
			a_a += koef_a * angle_a
			run_motor(motor_a, a_a)
			print(detect_color())
			j += 1
		if i + 1 != reps_i:
			# wait(20000)
			a_d += angle_d
			run_motor(motor_d, a_d)
		i += 1
		print("--------------------------------------------", i)
	run_motor(motor_a, 0)
	run_motor(motor_d, 0)
	ev3.speaker.beep(300, 100)


def snake_other():
	a_a = 0
	a_d = 0
	i = 0
	reps_i = 5
	reps_j = 3
	ev3.speaker.beep(300, 100)
	while i < reps_i:
		j = 0
		print(detect_color())
		while j < reps_j:
			if j == 0:
				a_a += 175
			else:
				a_a += 150
			run_motor(motor_a, a_a)
			print(detect_color())
			j += 1
		a_a = 0
		run_motor(motor_a, a_a)
		if i + 1 != reps_i:
			wait(20000)
			a_d += angle_d
			run_motor(motor_d, a_d)
		i += 1
		print("--------------------------------------------", i)
	wait(20000)
	run_motor(motor_d, 0)
	ev3.speaker.beep(300, 100)


def forward_along_line():
	j = 0
	reps_j = 3
	a_a = 0
	print(detect_color())
	while j < reps_j:
		if j == 0:
			a_a += 175
		else:
			a_a += 150
		run_motor(motor_a, a_a)
		print(detect_color())
		j += 1
	drop(a_a, 0)
	run_motor(motor_a, 0)


def print_states_link_1_d():
	init_map()
	i = 0
	while i < ROWS:
		j = 0
		while j < COLS:
			print(map_red_field[i][j].link_1_d, end = " ")
			j += 1
		print("")
		i += 1
	print("-----------------------------------------------------------")


def print_states_link_2_d():
	init_map()
	i = 0
	while i < ROWS:
		j = 0
		while j < COLS:
			print(map_red_field[i][j].link_2_d, end = " ")
			j += 1
		print("")
		i += 1
	print("-----------------------------------------------------------")


def forward_along_last_column():
	global is_dropped
	init_map()
	move_to(0, 3)
	print(detect_color())
	drop()
	move_to(1, 3)
	print(detect_color())
	drop()
	move_to(2, 3)
	print(detect_color())
	drop()
	move_to(3, 3)
	print(detect_color())
	drop()
	move_to(4, 3)
	print(detect_color())
	drop()
	is_dropped = False
	move_to(0, 0)


def forward_along_first_row():
	init_map()
	print(detect_color())
	move_to(0, 1)
	print(detect_color())
	move_to(0, 2)
	print(detect_color())
	move_to(0, 3)
	print(detect_color())
	move_to(0, 2)
	print(detect_color())
	move_to(0, 1)
	print(detect_color())
	move_to(0, 0)
	print(detect_color())


def forward_along_2_row():
	# init_map()
	print(detect_color())
	move_to(1, 1)
	print(detect_color())
	move_to(1, 2)
	print(detect_color())
	move_to(1, 3)
	print(detect_color())
	move_to(1, 2)
	print(detect_color())
	move_to(1, 1)
	print(detect_color())
	move_to(1, 0)
	print(detect_color())


def forward_along_3_row():
	# init_map()
	print(detect_color())
	move_to(2, 1)
	print(detect_color())
	move_to(2, 2)
	print(detect_color())
	move_to(2, 3)
	print(detect_color())
	move_to(2, 2)
	print(detect_color())
	move_to(2, 1)
	print(detect_color())
	move_to(2, 0)
	print(detect_color())


def forward_along_4_row():
	# init_map()
	print(detect_color())
	move_to(3, 1)
	print(detect_color())
	move_to(3, 2)
	print(detect_color())
	move_to(3, 3)
	print(detect_color())
	move_to(3, 2)
	print(detect_color())
	move_to(3, 1)
	print(detect_color())
	move_to(3, 0)
	print(detect_color())


def forward_along_5_row():
	# init_map()
	print(detect_color())
	move_to(4, 1)
	print(detect_color())
	move_to(4, 2)
	print(detect_color())
	move_to(4, 3)
	print(detect_color())
	move_to(4, 2)
	print(detect_color())
	move_to(4, 1)
	print(detect_color())
	move_to(4, 0)
	print(detect_color())


def forward_along_first_column():
	global is_dropped
	init_map()
	print(detect_color())
	drop()
	move_to(1, 0)
	print(detect_color())
	drop()
	move_to(2, 0)
	print(detect_color())
	drop()
	move_to(3, 0)
	print(detect_color())
	drop()
	move_to(4, 0)
	print(detect_color())
	drop()
	is_dropped = False
	move_to(0, 0)


# forward_along_last_column()
# forward_along_first_row()
# forward_along_first_column()


# snake()
# snake_improved()
# snake_other()
# forward_along_line()
# print_states_link_1_d()
# print_states_link_2_d()
# map_red_field.append([])
# print(len(map_red_field))
# print(map_red_field[0])

# init_map()
# is_dropped = True
# print(detect_color())
# move_to(0, 3)
# print(detect_color())
# move_to(4, 3)
# is_dropped = False
# move_to(0, 3)

# print(detect_color())
# move_to(0, 0)
# print(detect_color())
# wait(10000)

# print(detect_color())
# move_to(0, 3)
# print(detect_color())
# wait(10000)
# drop()
# move_to(0, 0)
# print(detect_color())

# forward_along_first_row()
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# move_to(1, 0)
# forward_along_2_row()
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# move_to(2, 0)
# forward_along_3_row()
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# move_to(3, 0)
# forward_along_4_row()
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# move_to(4, 0)
# forward_along_5_row()
# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
# move_to(0, 0)