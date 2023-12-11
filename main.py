#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, ColorSensor)
from pybricks.parameters import Port, Direction, Color
from pybricks.tools import wait

BLACK = 0
BLUE = 1
GREEN = 2
YELLOW = 3
RED = 4
WHITE = 5
BROWN = 6

V_MIN = 7
V_MIN_BROWN = 25
S_MIN = 50

red_h = [300, 360]
blue_h = [170, red_h[0] - 1]
green_h = [80, blue_h[0] - 1]
yellow_h = [40, green_h[0] - 1]
red_h_2 = [0, yellow_h[0] - 1]

ev3 = EV3Brick()
speed = 100
angle_a = 160 # full 480
angle_d = 195 # full 780
motor_a = Motor(Port.A, Direction.COUNTERCLOCKWISE)
motor_d = Motor(Port.D, Direction.COUNTERCLOCKWISE)

color_sensor = ColorSensor(Port.S1)


def run_motor(motor, angle):
	motor.run_target(speed, angle)
	# motor.reset_angle(-1) Сместилось на 20 градусов по обоим двигателям
	# wait(10000)
	wait(2000)


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
	# ev3.screen.print(hsv)
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
		if hsv[2] < V_MIN_BROWN:
			return BROWN
		return YELLOW
	if hsv[0] >= red_h[0] and hsv[0] <= red_h[1]:
		return RED
	if hsv[0] >= red_h_2[0] and hsv[0] <= red_h_2[1]:
		if hsv[2] < V_MIN_BROWN:
			return BROWN
		return RED
	return -1


def drop(current_angle_a, current_angle_d):
	angle_drop_a = 40
	angle_drop_d = 80
	ev3.speaker.beep(300, 100)
	run_motor(motor_a, current_angle_a + angle_drop_a)
	run_motor(motor_d, current_angle_d + angle_drop_d)
	run_motor(motor_d, current_angle_d)
	run_motor(motor_a, current_angle_a)
	ev3.speaker.beep(300, 100)


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
# run_motor(motor_a, -475)
# run_motor(motor_a, 0)
run_motor(motor_d, 780)
wait(5000)
run_motor(motor_d, 0)
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


# snake()
# snake_improved()
# snake_other()
# forward_along_line()
