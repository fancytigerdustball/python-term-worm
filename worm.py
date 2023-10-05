''' Simple module for the game "Snake" (but with a worm instead) '''

# Import Libraries
from time import sleep, perf_counter as clock
from random import randint
import pygame as pg
import bext
import json
import os

filename = 'wormbest.json'
screen = pg.display.set_mode((100, 100))
width = height = 8
if os.name in ('nt, dos'):
    command = 'cls'
else:
    command = 'clear'

# Load/Create JSON file
try:
    with open(filename) as file:
        best = json.load(file)
except (json.decoder.JSONDecodeError, FileNotFoundError):
    best = 0
    with open(filename, 'w') as file:
        json.dump(best, file)

class HitSomethingError(RuntimeError):
    ''' The worm hit something '''
    pass

class Events:
    ''' Class for storing key-clicks '''
    w = a = s = d = False

    def fix_keys(self, key, boolean):
        ''' Set key attributes to boolean argument '''
        match key:
            case pg.K_q:
                if boolean:
                    pg.quit()
                    raise SystemExit

            case pg.K_w | pg.K_UP:
                self.w = boolean
            case pg.K_a | pg.K_LEFT:
                self.a = boolean
            case pg.K_s | pg.K_DOWN:
                self.s = boolean
            case pg.K_d | pg.K_RIGHT:
                self.d = boolean

    def stop(self):
        ''' Restart game '''
        raise HitSomethingError('Oh no I hit something')
    
    def get_wasd(self):
        ''' Return current key attributes '''
        return self.w, self.a, self.s, self.d

class Worm:
    ''' Class for storing the worm's coordinates and length '''

    def __init__(self):
        ''' Restart worm '''

        self.history = []
        self.length = 2
        self.head = (1, 1)
        self.angle = 'd'
    
    def get_tail(self):
        ''' Return worm's tail coordinates '''
        x, y = self.head
        tail = []
        for move in reversed(self.history):
            match move:
                case 'w':
                    y -= 1
                case 'a':
                    x -= 1
                case 's':
                    y += 1
                case 'd':
                    x += 1
            tail.append((x, y))

        # Check if the worm has collided with its tail or an edge
        try:
            tail = tail[len(tail) - self.length:]
            x, y = tail[-1]
            if (x < 0 or x >= width) or (y < 0 or y >= height):
                events.stop()
            if tail.count(tail[-1]) > 1:
                events.stop()
        except IndexError:
            pass
        return tail
    
    def update(self, pausing=False):
        ''' Update the worm '''
        new_angle = self.angle
        # Turn the worm
        if events.w:
            if self.angle != 's':
                event.w = False
                new_angle = 'w'
        else:
            if events.a:
                if self.angle != 'd':
                    event.a = False
                    new_angle = 'a'
            else:
                if events.s:
                    if self.angle != 'w':
                        event.s = False
                        new_angle = 's'
                else:
                    if events.d:
                        if self.angle != 'a':
                            event.d = False
                            new_angle = 'd'
        self.angle = new_angle

        if not pausing:
            self.history.insert(0, self.angle)
            try:
                tail = self.get_tail()
                if tail[-1] == apple:
                    # Make new apple
                    self.length += 1
                    tail = self.get_tail()
                    while True:
                        test_apple = (randint(0, width - 1), randint(0, height - 1))
                        if test_apple not in tail:
                            return test_apple
                        if self.length == width * height:
                            events.stop()
            except IndexError:
                pass
        return False
    
events = Events()

# This loop is to play the game over and over
while True:

    # Catches HitSomethingError
    try:

        apple = (4, 4)
        worm = Worm()
        # This loop is to play the game
        while True:
            # Clear and print to the terminal
            os.system(command)
            for y in range(height):
                for x in range(width):
                    block = 'ww'
                    color = 'green'
                    if (x, y) == apple:
                        color = 'red'
                        block = ' `'
                    tail = worm.get_tail()
                    for point in tail:
                        if (x, y) == point:
                            color = 'magenta'
                            if point == tail[-1]:
                                if worm.angle == 'w':
                                    block = "''"
                                elif worm.angle == 'a':
                                    block = ': '
                                elif worm.angle == 's':
                                    block = '..'
                                else:
                                    block = ' :'
                            else:
                                block = '  '
                            break
                    if block != 'ww':
                        fg = 'white'
                    else:
                        fg = 'green'
                    bext.bg(color)
                    bext.fg(fg)
                    print(block, end='')
                    bext.bg('reset')
                    bext.fg('reset')
                print()
            print(f'Score: {worm.length - 2}')
            print(f'Best: {best}')

            # Change apple if a coordinate was returned
            new_apple = worm.update()
            if new_apple:
                apple = new_apple
            if worm.length - 2 > best:
                # Update best
                best = worm.length - 2
                with open(filename, 'w') as file:
                    json.dump(best, file)

            start = clock()
            updated = False
            events.w = events.a = events.s = events.d = False
            start_wasd = events.get_wasd()
            # Pause
            while not clock() - start >= 0.2:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        events.stop()
                    elif event.type == pg.KEYDOWN:
                        events.fix_keys(event.key, True)
                    elif event.type == pg.KEYUP:
                        events.fix_keys(event.key, False)
                if not updated and start_wasd != events.get_wasd():
                    worm.update(True)
                    updated = True

    except HitSomethingError:
        print('Oh no!')
        sleep(1)
