import pandas as pd
import pygame
import sys
import time
import os
import random
import math

SCREEN_W, SCREEN_H = 800, 800
SCALE = 1


def traffic_light_init():
    file_name = 'traffic_light.txt'
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path, 'r') as f:
        traffic_light_r = f.read().splitlines()
    lights = line_data_init(traffic_light_r)
    return lights


def bus_init(scr, lights, bus_num_total):
    file_path = os.path.join(os.getcwd(), 'Lines')
    bus_data_list = []
    for line_number in range(len(bus_num_total)):
        bus_name = bus_num_total.iloc[line_number, 0]
        file_name = bus_name + '.txt'
        line_file_path = os.path.join(file_path, file_name)
        with open(line_file_path, 'r') as f:
            line_file = f.read().splitlines()
        line = line_data_init(line_file)
        line = add_traffic_light(line, lights)
        bus_data = Bus(bus_name, line, 0, scr)
        bus_data_list.append(bus_data)
    return bus_data_list


def line_data_init(line_file):
    res_list = []
    for line in line_file:
        line_list = []
        word = ''
        for c in line:
            if c == '(' or c == ')' or c == ' ':
                continue
            if c == ',':
                line_list.append(int(word))
                word = ''
                continue
            word += c
        if word == 'True':
            line_list.append(True)
        elif word == 'False':
            line_list.append(False)
        res_list.append(line_list)
    return res_list


def add_traffic_light(stops, t_lights):
    for stop_num in range(len(stops) - 1):
        stop_1 = stops[stop_num]
        stop_2 = stops[stop_num + 1]
        for light in t_lights:
            slope_1 = stop_1[1] - light[1] / stop_1[0] - light[0]
            slope_2 = light[1] - stop_2[1] / light[0] - stop_2[0]
            x_diff = (stop_1[0] - light[0]) * (stop_2[0] - light[0])
            y_diff = (stop_1[1] - light[1]) * (stop_2[1] - light[1])
            if (abs(slope_1 - slope_2) <= 1) and (x_diff < 0) and (y_diff < 0):
                stops.insert(stop_num + 1, light)
    return stops


class Bus(object):
    def __init__(self, *args):
        self.line_num = args[0]
        self.stops = args[1]
        self.x = args[1][0][0]
        self.y = args[1][0][1]
        self.spd = 0
        self.slope = 0
        self.stop_num = 0
        self.max_spd = 0.388  # 50km/h
        self.max_acc = 0.02  # 不知道
        self.mode = 1  # 0:stop, 1:accelerating, 2: constant motion, 3: decelerating 4: end
        self.direction = 0
        self.stop_time = args[2]
        self.distance = 0
        if self.stop_time != 0:
            self.mode = 0
        self.scr = args[3]

    def move(self, cur_time, weather):
        if self.mode == 0:
            self.move_mode_0()
            return
        time_period = self.calc_time_period(cur_time)  # 0:normal 1:morning peak 2:evening peak
        current_pos = [self.x, self.y]
        next_stop = self.stops[self.stop_num + 1][:2]
        self.slope = self.calc_direct(current_pos, next_stop)
        distance = self.calc_distance(current_pos, next_stop)
        stop_distance = self.calc_stop_distance(self.spd, self.max_acc)
        self.max_spd = self.calc_max_spd(time_period, weather)
        if self.judge_stop(current_pos, next_stop):
            self.x, self.y = next_stop[0], next_stop[1]
            self.move_mode_0()
        elif self.spd >= distance:
            self.x, self.y = next_stop[0], next_stop[1]
            self.move_mode_0()
        elif stop_distance >= distance:
            self.move_mode_3()
        elif self.spd + self.max_acc >= self.max_spd:
            self.move_mode_2()
        else:
            self.move_mode_1()

    def move_mode_0(self):
        self.mode = 0
        self.spd = 0
        if self.x == self.stops[-1][0] and self.y == self.stops[-1][1]:
            self.direction = 1 - self.direction
            self.stops = self.stops[::-1]
            self.stop_num = -1
        current_stop = self.stops[self.stop_num + 1]
        stop_flag = current_stop[2]
        if self.stop_time == 1:
            self.stop_time = 0
            self.stop_num += 1
            self.mode = 1
        elif self.stop_time > 0:
            self.stop_time -= 1
        else:
            if stop_flag:
                self.stop_time = 30  # stop time
            else:
                self.stop_time = random.randint(1, 60)  # traffic light

    def move_mode_1(self):
        self.mode = 1
        self.spd += self.max_acc
        self.distance += self.spd
        self.x, self.y = self.calc_new_pos(self.x, self.y, self.spd, self.slope)

    def move_mode_2(self):
        self.mode = 2
        self.spd = self.max_spd
        self.distance += self.spd
        self.x, self.y = self.calc_new_pos(self.x, self.y, self.spd, self.slope)

    def move_mode_3(self):
        self.mode = 3
        self.spd -= self.max_acc
        self.distance += self.spd
        self.x, self.y = self.calc_new_pos(self.x, self.y, self.spd, self.slope)

    def draw(self):
        pygame.draw.circle(self.scr, (0, 0, 0), (self.x * SCALE, self.y * SCALE), 4)

    @staticmethod
    def calc_direct(current_stop, next_stop):
        if abs(next_stop[0] - current_stop[0]) <= 1:
            if next_stop[1] - current_stop[1] > 0:
                return 90
            return 180
        if abs(next_stop[1] - current_stop[1]) <= 1:
            if next_stop[0] - current_stop[0] > 0:
                return 0
            return math.pi
        slope = (next_stop[1] - current_stop[1]) / (next_stop[0] - current_stop[0])
        direct = math.atan(slope)
        if (next_stop[1] - current_stop[1]) * direct < 0:
            direct += math.pi
        return direct

    @staticmethod
    def calc_distance(current_pos, next_stop):
        delta_x = (next_stop[0] - current_pos[0]) ** 2
        delta_y = (next_stop[1] - current_pos[1]) ** 2
        distance = math.sqrt(delta_x + delta_y)
        return distance

    @staticmethod
    def calc_stop_distance(spd, max_acc):
        distance = spd ** 2 / (max_acc * 2) + spd + max_acc
        return distance

    @staticmethod
    def judge_stop(current_pos, next_stop):
        delta_x = next_stop[0] - current_pos[0]
        delta_y = next_stop[1] - current_pos[1]
        if (abs(delta_x) <= 1) and (abs(delta_y) <= 1):  # 1 is maximum deviation
            return True
        return False

    @staticmethod
    def calc_new_pos(x, y, spd, direct):
        if direct == 90:
            return x, y + spd
        if direct == 180:
            return x, y - spd
        x1 = x + spd * math.cos(direct)
        y1 = y + spd * math.sin(direct)
        return x1, y1

    @staticmethod
    def calc_time_period(cur_time):
        if 480 <= cur_time <= 540:
            return 1
        if 1020 <= cur_time <= 1080:
            return 2
        return 0

    @staticmethod
    def calc_max_spd(time_period, weather):
        if time_period == 1:
            max_spd = 0.342
        elif time_period == 2:
            max_spd = 0.334
        else:
            max_spd = 0.388
        if weather == 1:
            speed_decrease = random.randint(3, 13)
            max_spd *= (100 - speed_decrease) / 100
        elif weather == 2:
            speed_decrease = random.randint(5, 15)
            max_spd *= (100 - speed_decrease) / 100
        return max_spd


class Framework(object):
    def __init__(self, buses):
        self.year = 2023
        self.month = 1
        self.month_days = [31, 30, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.day = 1
        self.min = 1
        self.rain_prob = [13.2, 17.1, 16.1, 8.7, 3.6, 0, 0, 0, 0, 1.1, 3.3, 12.1]
        self.rain_probability = int((13.2 / 2.5 / 24) * 100)
        self.weather_list = ['sunny', 'rainy', 'sand storm']
        self.buses = buses
        self.weather = self.generate_weather()
        self.start_time = time.time()

    def move(self):
        self.min += 1
        if self.min > 1440:
            self.min = 1
            self.day += 1
            self.weather = self.generate_weather()
        if self.day > self.month_days[self.month]:
            self.day = 1
            self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        if self.month > 2033:
            print(time.time() - self.start_time)
            pygame.quit()
            sys.exit()
        for i in range(len(self.buses)):
            bus = self.buses[i]
            bus.move(self.min, self.weather)

    def generate_weather(self):
        rain_probability = int((self.rain_prob[self.month] / 2.5 / 24) * 100)
        weather = self.judge_weather(rain_probability)
        print(f'{self.year}/{self.month}/{self.day}:{self.weather_list[weather]}')
        return weather

    @staticmethod
    def judge_weather(rain_probability):
        weather_num = random.randint(1, 10000)
        if 1 <= weather_num <= rain_probability:
            return 1  # rain
        if 9290 <= weather_num <= 10000:
            return 2  # sand storm
        return 0  # sun







# ----main----
bus_num_df = pd.read_excel('bus_num.xlsx')
traffic_lights = traffic_light_init()
bus_list = bus_init(1, traffic_lights, bus_num_df)
frame = Framework(bus_list)
current_time = 0
while True:
    current_time += 1
    print(current_time)
    for i in range(len(bus_list)):
        bus = bus_list[i]
        bus.move(current_time,0)
    if current_time > 54000:
        for bus in bus_list:
            print([bus.line_num, int(bus.distance)])
        sys.exit()


