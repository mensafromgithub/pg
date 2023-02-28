import pygame
from PIL import Image
from random import randint, shuffle
import sys
import time
import json
import pandas as pd
import torch
from Sap_alt import Sap_alt


def to_pd(csv, cont):
    df = pd.read_csv(csv, sep=',')
    df.loc[len(df.index)] = [json.dumps(i) for i in cont]
    df.to_csv(path_or_buf=csv, sep=',', header=True, index=False)


def create_pole(n1, n2, im1, im2, pams):
    im = Image.new('RGB', (pams[0] * n1, pams[1] * n2), (0, 0, 0))
    pole = Image.open(im1).resize((pams[0], pams[1]))
    pole2 = Image.open(im2).resize((pams[0], pams[1]))
    for i in range(n1):
        for j in range(n2):
            if i == 0 or j == 0 or i == n1 - 1 or j == n2 - 1:
                im.paste(pole2, (pams[0] * i, pams[1] * j))
            else:
                im.paste(pole, (pams[0] * i, pams[1] * j))
    im.save('new_pole.png')

def pram(cont):
    return [j for i in cont for j in i]


def depram(cont, s1, s2):
    return [[cont[s2 * x + y] for y in range(s2)] for x in range(s1)]


class Timer:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.c =  0


    def start(self):
        self.start_time = time.time()

    def end(self):
        if not self.c:
            self.end_time = time.time()
            self.c = 1


class Game:
    def __init__(self, size, config=None):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.image = pygame.image.load('pg_data/doroga.png')
        self.image = pygame.transform.scale(self.image, self.screen.get_size())
        self.sts = 1
        self.conets = 0
        self.timer = Timer()
        self.game()

    def game(self):
        self.start()
        self.board = Board(30, 16, bombs=100)
        self.board.set_view2(20, 20, 20, 20, self.screen, 100)
        print(self.board.pole, self.board.board[0][0])
        self.bombed = 0
        self.show = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                if event.type == pygame.MOUSEBUTTONDOWN and (not self.sts) and (not self.conets):
                    self.bombed = self.board.get_click(event.pos)
                    self.conets = self.bombed
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 and self.sts:
                        self.sts = 0
                        self.board = self.st()
                    if event.key == pygame.K_1 and (not self.sts) and (self.conets) and (not self.show):
                        self.conets = 0
                        self.bombed = 0
                        self.board = self.st()
                    if event.key == pygame.K_2 and (not self.sts) and (self.conets):
                        self.show = not self.show
            if self.show:
                self.board.show_bombs()
                self.board.render2(self.screen)
                pygame.display.flip()
            elif self.conets and self.bombed:
                self.fin('bombed')
            elif pram(self.board.board).count(self.board.pole) == self.board.bombs:
                print(self.board.bombs)
                self.conets = 1
                self.fin('win')
            elif not self.sts:
                self.board.render2(self.screen)
                pygame.display.flip()

    def start(self):
        surf = pygame.Surface(self.screen.get_size())
        font = pygame.font.Font(None, 30)
        string_rendered = font.render('Нажмите [1] для начала в режиме игры 30X16 клеток', 1, pygame.Color('white'))
        x, y = self.screen.get_size()
        box = string_rendered.get_rect()
        surf.blit(self.image, (0, 0))
        surf.blit(string_rendered, (10 + box[2] // 2, y - 10 - box[3] // 2))
        self.screen.blit(surf, (0, 0))
        pygame.display.flip()

    def st(self):
        self.timer.start()
        board = Board(30, 16, bombs=100) #x, y
        board.set_view2(20, 20, 20, 20, self.screen, 100)
        return board

    def fin(self, status=None):
        self.timer.end()
        font = pygame.font.Font(None, 30)
        if status == 'win':
            string_rendered = font.render(f'Победа Время: {self.timer.end_time - self.timer.start_time}', 1, pygame.Color('white'))
        elif status == 'bombed':
            string_rendered = font.render(f'Game over Time: {self.timer.end_time - self.timer.start_time}', 1, pygame.Color('white'))
        x, y = self.screen.get_size()
        box = string_rendered.get_rect()
        string_rendered2 = font.render('Нажмите [1] для начала в режиме игры 30X16 клеток', 1, pygame.Color('white'))
        box2 = string_rendered2.get_rect()
        string_rendered3 = font.render('Нажмите [2] для просмотра поля', 1, pygame.Color('white'))
        surf = pygame.Surface(self.screen.get_size())
        surf.blit(self.image, (0, 0))
        surf.blit(string_rendered, (x // 2 - box[2] // 2, y // 2 - box[3] // 2))
        surf.blit(string_rendered2, (10 + box2[2] // 2, y - 10 - box2[3] // 2))
        surf.blit(string_rendered3, (10 + box2[2] // 2, y - 30 - box2[3] // 2))
        self.screen.blit(surf, (0, 0))
        pygame.display.flip()

    def make_config(self):
        cols = ['board', 'coords', 'bomb_pole', 'counts_pole', 'left', 'right', 'top', 'bottom', 'cell_w', 'cell_h']
        df = pd.DataFrame(columns=cols)
        pass

    def terminate(self):
        pygame.quit()
        sys.exit()


class Bomb:
    def __init__(self, cell_w, cell_h):
        self.bomb = pygame.transform.scale(pygame.image.load('pg_data/mini-bombr.png'), (cell_w, cell_h))


class Board:
    def __init__(self, width, height, bombs=0, cell_w=50, cell_h=50):
        self.pole = pygame.transform.scale(pygame.image.load('pg_data/defaultr.jpg'), (cell_w, cell_h))
        self.pole2 = pygame.transform.scale(pygame.image.load('pg_data/src.jfif'), (cell_w, cell_h))
        self.board = [[self.pole] * width for i in range(height)]
        self.coords = [[(0, 0)] * width for i in range(height)]
        self.bomb_pole = [[0] * width for i in range(height)]
        self.counts_pole = [[0] * width for i in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.bombs = bombs
        self.right = self.left
        self.bottom = self.top
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.gen_bomb_pole()
        self.nums = {0: self.pole2,
                     1: pygame.image.load('pg_data/1.png'),
                     2: pygame.image.load('pg_data/2.png'),
                     3: pygame.image.load('pg_data/3.png'),
                     4: pygame.image.load('pg_data/4.png'),
                     5: pygame.image.load('pg_data/5.png'),
                     6: pygame.image.load('pg_data/6.png'),
                     7: pygame.image.load('pg_data/7.png'),
                     8: pygame.image.load('pg_data/8.png')}
        self.sap = torch.load('pg_data/sap')

    def gen_bomb_pole(self):
        c = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if c < self.bombs:
                    self.bomb_pole[i][j] = Bomb(self.cell_w, self.cell_h)
                    c += 1
                else:
                    self.bomb_pole[i][j] = 0
        self.bomb_pole = pram(self.bomb_pole)
        shuffle(self.bomb_pole)
        self.bomb_pole = depram(self.bomb_pole, len(self.board), len(self.board[0]))
        self.counts_up()

    def counts_up(self):
        c = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if 0 <= i + x < len(self.board) and 0 <= j + y < len(self.board[0]):
                            c += 0 if self.bomb_pole[i + x][j + y] == 0 else 1
                self.counts_pole[i][j] = c
                c = 0

        # настройка внешнего вида
    def set_view(self, left, top, cell_size, screen, bombs=0):
        self.bombs = bombs
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.render(screen)

    def set_view2(self, left, right, top, bottom, screen, bombs=0):
        self.bombs = bombs
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.cell_w = (screen.get_size()[0] - self.left - self.right) // len(self.board[0])
        self.cell_h = (screen.get_size()[1] - self.top - self.bottom) // len(self.board)
        self.res_pole()
        self.render2(screen)
        self.gen_bomb_pole()

    def res_pole(self):
        self.pole = pygame.transform.scale(self.pole, (self.cell_w, self.cell_h))
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j] = self.pole

    def render(self, screen):
        surf = pygame.Surface(screen.get_size())
        image = pygame.image.load('pg_data/doroga.png')
        surf.blit(image, (0, 0))
        st = (self.left, self.top)
        for i in range(1, len(self.board) + 1):
            for j in range(1, len(self.board[0]) + 1):
                pygame.draw.rect(surf, (255, 255, 255), (st, (self.cell_size, self.cell_size)), 1)
                st = (st[0] + self.cell_size, st[1])
                self.coords[i - 1][j - 1] = (self.left + self.cell_size * j, self.top + self.cell_size * i)
            st = (self.left, st[1] + self.cell_size)
        screen.blit(surf, (0, 0))

    def render2(self, screen):
        surf = pygame.Surface(screen.get_size())
        image = pygame.image.load('pg_data/doroga.png')
        image = pygame.transform.scale(image, screen.get_size())
        surf.blit(image, (0, 0))
        st = (self.left, self.top)
        for i in range(1, len(self.board) + 1):
            for j in range(1, len(self.board[0]) + 1):
                surf.blit(self.board[i - 1][j - 1], st)
                pygame.draw.rect(surf, (255, 255, 255), (st, (self.cell_w, self.cell_h)), 1)
                st = (st[0] + self.cell_w, st[1])
                self.coords[i - 1][j - 1] = (self.left + self.cell_w * j, self.top + self.cell_h * i)
            st = (self.left, st[1] + self.cell_h)
        screen.blit(surf, (0, 0))

    def show_bombs(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.bomb_pole[i][j] != 0:
                    self.board[i][j] = self.bomb_pole[i][j].bomb

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        return self.on_click(cell)

    def get_cell(self, pos):
            for i in range(len(self.coords)):
                for j in range(len(self.coords[0])):
                    if (self.coords[i][j][0] - self.cell_size < pos[0] < self.coords[i][j][0]) and (self.coords[i][j][1] - self.cell_size < pos[1] < self.coords[i][j][1]):
                        return (j, i)

    def on_click(self, cell):
        try:
            otk = depram([1 if i != self.pole else 0 for i in pram(self.board)], len(self.board), len(self.board[0]))
            bomb_pole = depram([1 if i != 0 else 0 for i in pram(self.bomb_pole)], len(self.board), len(self.board[0]))
            a = self.sap.z_on([bomb_pole, otk, self.counts_pole], n=100)
            for i in range(len(self.bomb_pole)):
                for j in range(len(self.bomb_pole[0])):
                    if self.board[i][j] == self.pole and a[i][j] == 2:
                        self.bomb_pole[i][j] = Bomb(self.cell_w, self.cell_h)
                    else:
                        self.bomb_pole[i][j] = 0
            self.counts_up()
            if self.bomb_pole[cell[1]][cell[0]]:
                self.board[cell[1]][cell[0]] = pygame.transform.scale(self.bomb_pole[cell[1]][cell[0]].bomb, (self.cell_w, self.cell_h))
                return 1
            else:
                self.board[cell[1]][cell[0]] = pygame.transform.scale(self.nums[self.counts_pole[cell[1]][cell[0]]], (self.cell_w, self.cell_h))
            y = [1 if i != self.pole else 0 for i in pram(self.board)]
            to_pd('pg_data/df.csv', [bomb_pole, otk, self.counts_pole, y])
            print(pram(self.bomb_pole).count(0))
            return 0
        except:
            pass


if __name__ == '__main__':
    Game((1200, 1000))