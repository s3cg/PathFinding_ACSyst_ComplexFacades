#The following code is based on this reference https://towardsdatascience.com/snake-played-by-a-deep-reinforcement-learning-agent-53f2c4331d36

import os 
import csv 
from csv import writer


from tkinter import font
import turtle
import random
import time 
import math 
import math 
import gym
from gym import spaces 
from gym.utils import seeding

from datetime import datetime

import pandas as pd







HEIGHT = 16 
WIDTH = 56
PIXEL_H = 30*HEIGHT
PIXEL_W = 30*WIDTH

SLEEP = 0.2 

GAME_TITLE = 'Neo'
BG_COLOR = 'black'

NEO_SHAPE = 'square'
NEO_COLOR = 'gray'

#----- New Update version test with 3 different versions change this on the coords_game too 
#--- Initial point
#---- FACADE 1 COORDS
#NEO_START_LOC_H = 537.16 
#NEO_START_LOC_V = 141.09

#-291.59,-8.91 --- FACADE 2
#-84.87,-102.66 --- FACADE 3
#-23.94,5.15 ---- FACADE 4 
#80.03,9.84
#-23.94,-5.15
#37,141.09

#NEO_START_LOC_H = 37
#NEO_START_LOC_V = 141.09

#--Example_01
NEO_START_LOC_H = 537.16 
NEO_START_LOC_V = 141.09





#--- Last point
#NEO_START_LOC_H = 0
#NEO_START_LOC_V = 0
#
#---final time: Current time:  16:17:43
#---final state before dying: [[1 1 0 0 0 0 0 0 0 1 0 0]]





GLASS_SHAPE = 'square'
GLASS_COLOR = 'green'

class Neo(gym.Env):

    def __init__(self, human=False, env_info={'state_space':None}):
        super(Neo, self).__init__()
    
        self.done = False
        self.seed()
        self.reward = 0
        self.action_space = 4
        self.state_space = 12

        self.total, self.maximum = 0, 0
        self.human = human
        self.env_info = env_info


        self.count = 0

        ##  GAME CREATION
        #   screen/background
        self.win = turtle.Screen()
        self.win.title(GAME_TITLE)
        self.win.bgcolor(BG_COLOR)
        self.win.tracer(0)
        self.win.setup(width=PIXEL_W+32, height=PIXEL_H+32)   

        #Neo
        self.neo = turtle.Turtle()
        self.neo.shape(NEO_SHAPE)
        self.neo.shapesize(stretch_wid=0.20, stretch_len=0.20)
        self.neo.speed(0)
        self.neo.penup()
        self.neo.color(NEO_COLOR)
        self.neo.goto(NEO_START_LOC_H, NEO_START_LOC_V)
        self.neo.direction = 'stop'

        #neo body, add first element (for location of neo's head)
        self.neo_body = []
        self.add_to_body()

        
        self.neo_glasses = []
        #self.add_to_glasses()

        self.r_neo_glasses = []
        self.add_to_right_glasses()

        #self.facade_tot_glasses = []
        #self.facade_glasses()


        self.f_neo_glasses = []

        self.bnds_neo_glasses = []
        self.add_bounds()
        
        

        
        
        self.curr_pos_x = self.neo.xcor() - 840
        self.curr_neg_x = self.neo.xcor() - (-840)
        
        self.curr_pos_y = self.neo.ycor() - 240
        self.curr_neg_y = self.neo.ycor() - (-240)


        #closest distance


        self.distances_all = []
        for r_n in self.r_neo_glasses:
            self.r_n_dist = math.sqrt((self.neo.xcor()-r_n.xcor())**2 + (self.neo.ycor()-r_n.ycor())**2)
            self.prev_r_n_dist = self.r_n_dist
            
            #dist_all = math.sqrt((self.neo.xcor()-r_n.xcor())**2 + (self.neo.ycor()-r_n.ycor())**2)
            self.distances_all.append(self.r_n_dist)

        self.closest_dist = min(self.distances_all)


        #---    Bounds
        self.distances_bounds = []
        for bounds in self.bnds_neo_glasses:
            self.bounds_dist = math.sqrt((self.neo.xcor()-bounds.xcor())**2 + (self.neo.ycor()-bounds.ycor())**2)
            self.prev_bounds_dist = self.bounds_dist

            self.distances_bounds.append(self.bounds_dist)
        
        self.clst_bounds = min(self.distances_bounds)



        
        #   score
        self.score = turtle.Turtle()
        self.score.speed(0)
        self.score.color('white')
        self.score.penup()
        self.score.hideturtle()
        self.score.goto(0, 175)
        self.score.write(f"Total: {self.total}  Highest: {self.maximum}", align='center', font=('Roboto', 12))

        #   control 
        self.win.listen()
        self.win.onkey(self.go_up, 'Up')
        self.win.onkey(self.go_right, 'Right')
        self.win.onkey(self.go_down, 'Down')
        self.win.onkey(self.go_left, 'Left')
    
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    
    def facade_coordinates(self):
        df = pd.read_csv('./data/coords_windows.csv')
        
        x_coords = []
        for x in df['x']:
            x_coords.append(x)
        
        y_coords = []
        for y in df['y']:
            y_coords.append(y)

        coords = list(zip(x_coords, y_coords))
        return coords


    def bounds_coordinates(self):
        df_bnds = pd.read_csv('./data/bounds.csv')
        
        x_bounds_coords = []
        for x_bnds in df_bnds['x']:
            x_bounds_coords.append(x_bnds)
        
        y_bounds_coords = []
        for y_bnds in df_bnds['y']:
            y_bounds_coords.append(y_bnds)

        coords_bnds = list(zip(x_bounds_coords, y_bounds_coords))
        return coords_bnds
    
    def move_neo(self):
        if self.neo.direction == 'stop':
            self.reward = 0
        if self.neo.direction == 'up':
            y = self.neo.ycor()
            self.neo.sety(y + 10.20)
        if self.neo.direction == 'right':
            x = self.neo.xcor()
            self.neo.setx(x + 10.20)
        if self.neo.direction == 'down':
            y = self.neo.ycor()
            self.neo.sety(y - 10.20)
        if self.neo.direction == 'left':
            x = self.neo.xcor()
            self.neo.setx(x - 10.20)
    
    def go_up(self):
        if self.neo.direction != "down":
            self.neo.direction = "up"
    
    def go_down(self):
        if self.neo.direction != "up":
            self.neo.direction = "down"
    
    def go_right(self):
        if self.neo.direction != "left":
            self.neo.direction = "right"
    
    def go_left(self):
        if self.neo.direction != "right":
            self.neo.direction = "left"

    


    
    def update_score(self):
        self.total += 1
        if self.total >= self.maximum:
            self.maximum = self.total
        self.score.clear()
        self.score.write(f"Total: {self.total} Highest: {self.maximum}", align='center', font=('Roboto', 12))

    def reset_score(self):
        self.score.clear()
        self.total = 0 
        self.score.write(f"Total: {self.total} Highest: {self.maximum}", align='center', font=('Roboto', 12))
    

    def add_to_body(self):
        body = turtle.Turtle()
        body.speed(0)
        body.shape('square')
        body.color('white')
        body.penup()
        self.neo_body.append(body)

    def add_to_right_glasses(self):
        for pts in self.facade_coordinates():

            self.x_glass_sc = pts[0]
            self.y_glass_sc = pts[1]
            r_x_glass = pts[0]
            r_y_glass = pts[1]
            r_glass_body = turtle.Turtle()
            r_glass_body.speed(0)
            r_glass_body.shape('square')
            r_glass_body.shapesize(stretch_len=0.20, stretch_wid=0.20)
            r_glass_body.color('green')
            r_glass_body.penup()
            r_glass_body.setposition(r_x_glass, r_y_glass)
            self.r_neo_glasses.append(r_glass_body)

    def add_bounds(self):
        for pts in self.bounds_coordinates():

            self.x_bnds_sc = pts[0]
            self.y_bnds_sc = pts[1]
            bnds_x_glass = pts[0]
            bnds_y_glass = pts[1]
            bnds_glass_body = turtle.Turtle()
            bnds_glass_body.speed(0)
            bnds_glass_body.shape('square')
            bnds_glass_body.shapesize(stretch_len=0.20, stretch_wid=0.20)
            bnds_glass_body.pencolor('gray')
            bnds_glass_body.penup()
            bnds_glass_body.setposition(bnds_x_glass, bnds_y_glass)
            self.bnds_neo_glasses.append(bnds_glass_body)

    def min_distance(self):
        self.distances_all = []
        for r_n in self.r_neo_glasses:
            self.r_n_dist = math.sqrt((self.neo.xcor()-r_n.xcor())**2 + (self.neo.ycor()-r_n.ycor())**2)
            self.prev_r_n_dist = self.r_n_dist
            
            #dist_all = math.sqrt((self.neo.xcor()-r_n.xcor())**2 + (self.neo.ycor()-r_n.ycor())**2)
            self.distances_all.append(self.r_n_dist)
        
        self.prev_close_dist = self.closest_dist
        self.closest_dist = min(self.distances_all)



    def check_bounds(self):
        self.distances_bnds = []
        for bnds in self.bnds_neo_glasses:
            self.bnds_dist = math.sqrt((self.neo.xcor()-bnds.xcor())**2 + (self.neo.ycor()-bnds.ycor())**2)
            self.prev_bnds_dist = self.bnds_dist

            self.distances_bnds.append(self.bnds_dist)
            
            if self.bnds_dist < 4:
                #print(self.bnds_dist)
                
                self.reset_score()
                for xxx in self.r_neo_glasses:
                    xxx.goto(1000, 1000)
                
                self.add_to_right_glasses()

                return True
            #    print('ALMOST TRUE')
    

    def check_bounds_dist(self):
        self.distances_bounds = []
        for bounds in self.bnds_neo_glasses:
            self.bounds_dist = math.sqrt((self.neo.xcor()-bounds.xcor())**2 + (self.neo.ycor()-bounds.ycor())**2)
            self.prev_bounds_dist = self.bounds_dist

            self.distances_bounds.append(self.bounds_dist)
        
        self.prev_clst_bounds = self.clst_bounds
        self.clst_bounds = min(self.distances_bounds)
            
            #self.distances_bnds.append(self.bnds_dist)

            
        
        #self.prev_close_dist = self.closest_dist
        #self.closest_dist = min(self.distances_all)

    def index_min_distance(self):
        self.x_c = []
        self.y_c = []
        self.dist_neo = []

        for coords in self.r_neo_glasses:
            self.x_coords = coords.xcor()
            self.y_coords = coords.ycor()
            self.i_dist = math.sqrt((self.neo.xcor()-coords.xcor())**2 + (self.neo.ycor()-coords.ycor())**2)
            self.x_c.append(self.x_coords)
            self.y_c.append(self.y_coords)
            self.dist_neo.append(self.i_dist)
        
        self.all_family = list(zip(self.x_c, self.y_c, self.dist_neo))
        self.min_dist_value = min(self.dist_neo)

        for i, j, k in self.all_family:
            if self.min_dist_value == k:
                self.x_min_dist = i
                self.y_min_dist = j
                """t_glass_body = turtle.Turtle()
                t_glass_body.speed(0)
                t_glass_body.shape('square')
                t_glass_body.shapesize(stretch_len=0.05, stretch_wid=0.05)
                t_glass_body.color('red')
                t_glass_body.penup()
                t_glass_body.setposition(self.x_min_dist, self.y_min_dist) """

    

    def position(self):
        self.prev_pos_x = self.curr_pos_x
        self.curr_pos_x = self.neo.xcor() - 840

        self.prev_neg_x = self.curr_neg_x
        self.curr_neg_x = self.neo.xcor() - (-840)

        self.prev_pos_y = self.curr_pos_y
        self.curr_pos_y = self.neo.ycor() - 240

        self.prev_neg_y = self.curr_neg_y
        self.curr_neg_y = self.neo.ycor() - (-240)

            
    def dist_r_glasses(self):
        for r_n in self.r_neo_glasses:
            r_n_dist = math.sqrt((self.neo.xcor()-r_n.xcor())**2 + (self.neo.ycor()-r_n.ycor())**2)
            
            if r_n_dist < 10:
                x_r = 1000
                y_r = 1000
                r_n.goto(x_r, y_r)
                #r_n.pencolor('red')
                #r_n.color('red')
                self.update_score()
                return True
        
    

    

    
    def wall_check(self):
        if self.neo.xcor() > 840 or self.neo.xcor() < -840 or self.neo.ycor() > 240 or self.neo.ycor() < -240:
            

            self.reset_score()

            for yyy in self.r_neo_glasses:
                    yyy.goto(1000, 1000)
                
            self.add_to_right_glasses()


            return True

        

    def reset(self):
        if self.human:
            time.sleep(1)
        
        for body in self.neo_body:
            body.goto(1000, 1000)
        
        self.neo_body = []
        self.neo.goto(NEO_START_LOC_H, NEO_START_LOC_V)
        self.neo.direction = 'stop'
        self.reward = 0
        self.total = 0
        self.done = False

        state = self.get_state()

        return state

    
    def run_game(self):
        reward_given = False
        self.win.update()
        self.move_neo()

        #print('x_coords:', self.neo.xcor(),'y_coords: ', self.neo.ycor())
        
       
            
        
        #self.move_neobody()


        if self.dist_r_glasses():
            

            #---REMEMBER 5 is working fine removing the boxes 
            self.reward = 10
            reward_given = True

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Current time: ", current_time)



        
        ###---Removed body_check()


        if self.wall_check():
            self.reward = -100
            reward_given = -100
            self.done = True
            if self.human:
                self.reset()

        

        if self.check_bounds():
            self.reward = -100
            reward_given = -100
            self.done = True
            if self.human:
                self.reset()
        




        #----NOW THIS SHIT POSITION SEEMS TO WORK
        self.position()
        self.index_min_distance()
        #print('Here Are the coordinates', self.x_min_dist, self.y_min_dist)
        
        

        ###--- TEST WITH ELSE ---
        if not reward_given:
            if self.curr_pos_x < self.prev_pos_x:
                #print('FUCK__POS_X_TRUE')
                self.reward = -1
            else:
                self.reward = 1
    
            if self.curr_neg_x > self.prev_neg_x:
                #print('FUCK_NEG_X_TRUE')
                self.reward = -1
            else:
                self.reward = 1
            
            if self.curr_pos_y < self.prev_pos_y:
            #    print('SHIT_POS_Y_TRUE')
                self.reward = -1
            else:
                self.reward = 1
            
            if self.curr_neg_y > self.prev_neg_y:
                #print('SHIT_NEG_Y_TRUE')
                self.reward = -1
            else:
                self.reward = 1
            


            self.min_distance()
            self.check_bounds()
            self.check_bounds_dist()


            #print(self.prev_clst_bounds, self.clst_bounds)

            

            if self.prev_clst_bounds < self.prev_clst_bounds:
                self.reward = -3
                #print('going far')
            else:
                self.reward = 1
                #print('going closer')


            if  self.prev_close_dist < self.min_dist_value:
                self.reward = -3
                #print('Closer')
            else:
                self.reward = 1
                #print('far')
            


            #print(self.curr_pos_x, self.prev_pos_x, self.curr_neg_x, self.prev_neg_x)
            #print('prev_close', self.prev_close_dist, 'curr_close', self.closest_dist)
            #print('g_far', self.min_dist_value, 's_c_dist', self.closest_dist)
            
            
        res_list = [self.neo.xcor(), self.neo.ycor(), self.min_dist_value]
        #print('res_list_ENV', res_list)

        filename = './outputs/coords_outputs.csv'

        with open(filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(res_list)
        f.close()
        
        
        
        if self.human:
            time.sleep(SLEEP)
            state = self.get_state()


    # AI agent
    def step(self, action):
        if action == 0:
            self.go_up()
        if action == 1:
            self.go_right()
        if action == 2:
            self.go_down()
        if action == 3:
            self.go_left()
        self.run_game()
        state = self.get_state()
        return state, self.reward, self.done, {}
    
    def get_state(self):
        #neo coordinates abs
        self.neo.x, self.neo.y = self.neo.xcor() , self.neo.ycor()
        #neo coordinates scaled 0-1
        self.neo.xsc, self.neo.ysc = abs(self.neo.x/1680+0.5), abs(self.neo.y/480+0.5)
        
        
        #glass coordinates scaled 0-1
        #self.r_neo_glasses


        ###---CHECK THIS SHIT----------
        ###--- locate the last min and max coordinates
        ###---ONE WAY could be get the min xcoor and min ycoord

        
        #self.glass.xsc, self.glass.ysc = self.glass.xcor()/1680, self.glass.ycor()/480
        self.index_min_distance()
        self.xsc, self.ysc = abs(self.x_min_dist/1680+0.5), abs(self.y_min_dist/480+0.5)
        
    
        #---Print if is necessary---
        #print('Scaled: ', self.xsc, self.ysc,  self.neo.xsc, self.neo.ysc)


        #HEIGHT = 16 
        #WIDTH = 56

        #HEIGHT/2 
        #WIDTH/2
        # wall check
        if self.neo.y >= 480/2:
            wall_up, wall_down = 1, 0
        elif self.neo.y <= -480/2:
            wall_up, wall_down = 0, 1
        else:
            wall_up, wall_down = 0, 0
        if self.neo.x > 1680/2:
            wall_right, wall_left = 1, 0
        elif self.neo.x <= -1680/2:
            wall_right, wall_left = 0, 1
        else:
            wall_right, wall_left = 0, 0
        
        # body close
        body_up = []
        body_right = []
        body_down = []
        body_left = []
        if len(self.neo_body) > 3:
            for body in self.neo_body[3:]:
                if body.distance(self.neo) == 20:
                    if body.ycor() < self.neo.ycor():
                        body_down.append(1)
                    elif body.ycor() > self.neo.ycor():
                        body_up.append(1)
                    if body.xcor() < self.neo.xcor():
                        body_left.append(1)
                    elif body.xcor() > self.neo.xcor():
                        body_right.append(1)
        
        if len(body_up) > 0: body_up = 1
        else: body_up = 0
        if len(body_right) > 0: body_right = 1
        else: body_right = 0
        if len(body_down) > 0: body_down = 1
        else: body_down = 0
        if len(body_left) > 0: body_left = 1
        else: body_left = 0

        #state: glass_up, glass_right, glass_down, glass_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, direction_up, direction_right, direction_down, direction_left
        if self.env_info['state_space'] == 'coordinates':
            state = [self.xsc, self.ysc, self.neo.xsc, self.neo.ysc, \
                int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down), int(wall_left or body_left), \
                int(self.neo.direction == 'up'), int(self.neo.direction == 'right'), int(self.neo.direction == 'down'), int(self.neo.direction == 'left')]
        
        elif self.env_info['state_space'] == 'no direction':
            state = [int(self.neo.y < self.y_min_dist), int(self.neo.x < self.x_min_dist), int(self.neo.y > self.y_min_dist), int(self.neo.x > self.x_min_dist), \
                int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down), int(wall_left or body_left), \
                0, 0, 0, 0]
        
        elif self.env_info['state_space'] == 'no body knowledge':
            state = [int(self.neo.y < self.y_min_dist), int(self.neo.x < self.x_min_dist), int(self.neo.y > self.y_min_dist), int(self.neo.x > self.x_min_dist), \
                wall_up, wall_right, wall_down, wall_left, \
                int(self.neo.direction == 'up'), int(self.neo.direction == 'right'), int(self.neo.direction == 'down'), int(self.neo.direction == 'left')]

        else:
            state = [int(self.neo.y < self.y_min_dist), int(self.neo.x < self.x_min_dist), int(self.neo.y > self.y_min_dist), int(self.neo.x > self.x_min_dist), \
                int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down), int(wall_left or body_left), \
                int(self.neo.direction == 'up'), int(self.neo.direction == 'right'), int(self.neo.direction == 'down'), int(self.neo.direction == 'left')]

        return state


def bye(self):
    self.win.bye()

if __name__ == '__main__':
    human = True
    env = Neo(human=human)

    if human:
        while True:
            env.run_game()
