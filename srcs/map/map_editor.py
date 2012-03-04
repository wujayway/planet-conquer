#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
 MapEditor for Planet-Conquer
"""

import yaml
import copy
import string
import pygame
import sys

SIZE=40

class Editor:
    def __init__(self):
        pass

    def load_file(self, file_name):
        self.map = yaml.load(open(file_name).read())
        self.map['map'] = self.map['map'].strip().split('\n')

    def save_file(self, file_name):
        data = copy.deepcopy(self.map)
        data['map'] = string.join(data['map'], '\n')
        open(file_name, 'w').write(yaml.dump(data, default_flow_style=False))

    def create_planet(self, i, j):
        planet_name = self.generate_planet_name()
        if planet_name:
            self.map['map'][i] = self.map['map'][i][0:j]  + planet_name + self.map['map'][i][j+1:]
            self.map['planets'][planet_name] = {'def':0, 'res':1, 'cos':0, 'max':100 }

    def update_planet(self, planet_name, key, val):
        self.map['planets'][planet_name][key] = val

    def generate_planet_name(self):
        candi = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        dis = self.map['planets'].keys()
        for i in candi:
            if i not in dis:
                return i
        return ''

    def toggle_starts(self, planet_name):
        if planet_name in self.map['planets'].keys():
            if planet_name in self.map['starts']:
                self.map['starts'].remove(planet_name)
            else:
                self.map['starts'].append(planet_name)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DES = ['def', 'res', 'cos', 'max']
class EditorView:
    def __init__(self, editor):
        pygame.init()
        self.font = pygame.font.SysFont('sans', 12)
        self.editor = editor
        self.map = editor.map
        map = self.map['map']
        self.h = len(map)
        self.w = len(map[0])
        self.selected_i = -1
        self.selected_j = -1
        print map
        print self.h, self.w
        self.base_w = self.w*SIZE
        self.screen = pygame.display.set_mode((self.base_w + 200, max(100, self.h*SIZE)))
        self.menu_id = 0
        self.input_n = False

    def get_mouse_on(self):
        mx, my = pygame.mouse.get_pos()
        mx = mx / SIZE
        my = my / SIZE
        return mx, my

    def render_word(self, pos, c, w):
        self.screen.blit(self.font.render(w, True, c), pos)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = self.get_mouse_on()
                if x >= 0 and x < self.w and y >= 0 and y < self.h:
                    self.selected_i, self.selected_j = x, y
                    self.menu_id = 0
            elif event.type == pygame.KEYDOWN:
                if self.input_n:
                    if event.key == pygame.K_BACKSPACE:
                        if len(self.number) > 0:
                            self.number = self.number[:-1]
                    elif event.key == pygame.K_RETURN:
                        try:
                            planet_name = self.map['map'][self.selected_j][self.selected_i]
                            self.editor.update_planet(planet_name, DES[self.menu_id], float(self.number))
                            self.input_n = False
                        except:
                            pass
                    else:
                        self.number = self.number + event.unicode.encode('ascii')
                            
                else:
                    if event.key == pygame.K_UP:
                        self.menu_id = max(0, self.menu_id - 1)
                    elif event.key == pygame.K_DOWN:
                        self.menu_id = min(3, self.menu_id + 1)
                    elif event.key == pygame.K_RETURN:
                        self.on_key_ret()
                    elif event.key == pygame.K_t:
                        planet_name = self.map['map'][self.selected_j][self.selected_i]
                        if planet_name != '.':
                            self.editor.toggle_starts(planet_name)

    def render(self):
        self.update()
                
        self.screen.fill(BLACK)
        mx, my = self.get_mouse_on()
        for i in range(self.w):
            for j in range(self.h):
                color = (200, 200, 200)
                if i == self.selected_i and j == self.selected_j:
                    color = (170, 255, 172)
                elif i == mx and j == my:
                    color = (250, 170, 170)
                pygame.draw.circle(self.screen,
                                   color,
                                   (i * SIZE + SIZE / 2,
                                    j * SIZE + SIZE / 2),
                                   SIZE / 2 - 1)
        def draw_route(pos_s, pos_e, len):
            
        for r in self.map['routes']:
            draw_route(r[0], r[1], r[2])
            
        for i in range(self.w):
            for j in range(self.h):
                planet_name = self.map['map'][j][i]
                if planet_name != '.':
                    if planet_name in self.map['starts']:
                        pygame.draw.circle(self.screen,
                                           BLACK,
                                           (i * SIZE + SIZE / 2,
                                            j * SIZE + SIZE / 2),
                                           SIZE / 2 - 5, 2)
                    self.render_word((i * SIZE + SIZE / 2 - 6,
                                      j * SIZE + SIZE / 2 - 6),
                                     BLACK, planet_name)
                    
        self.render_planet_info()
        pygame.display.flip()

    def render_planet_info(self):
        if self.selected_j == -1:
            self.render_word((self.base_w + 2, 10), WHITE, 'no space selected.')
        else:
            planet_name = self.map['map'][self.selected_j][self.selected_i]
            if planet_name == '.':
                self.render_word((self.base_w + 2, 10), WHITE, 'empty space.')
            else:
                p = self.map['planets'][planet_name]
                pygame.draw.rect(self.screen, (100, 110, 100),
                                 pygame.Rect(self.base_w + 1, 26 + 15 * self.menu_id, 200, 13))
                planet_desc = planet_name
                if planet_name in self.map['starts']:
                    planet_desc += ' (start) '
                self.render_word((self.base_w + 2, 10), WHITE, 'Planet:%s' % planet_desc)
                self.render_word((self.base_w + 2, 25), WHITE, 'def: %f' % p['def'])
                self.render_word((self.base_w + 2, 40), WHITE, 'res: %f' % p['res'])
                self.render_word((self.base_w + 2, 55), WHITE, 'cos: %f' % p['cos'])
                self.render_word((self.base_w + 2, 70), WHITE, 'max: %f' % p['max'])

                if self.input_n:
                    self.render_word((self.base_w + 2, 90), WHITE, 'new_val: %s' % self.number)

    def on_key_ret(self):
        if self.selected_j == -1:
            return
        planet_name = self.map['map'][self.selected_j][self.selected_i]
        if planet_name == '.':
            self.editor.create_planet(self.selected_j, self.selected_i)
        else:
            self.input_n = True
            self.number = ''

def main():
    e = Editor()
    e.load_file('test.yml')
    view = EditorView(e)
    while True:
        view.render()
        

if __name__=='__main__':
    main()
    #e = Editor()
    #e.load_file('test.yml')
    #e.save_file('test2.yml')
    
    

            
