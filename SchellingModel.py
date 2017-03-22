# -*- coding: utf-8 -*-
"""
@author1: vwood: Created on Feb 16 2012, https://gist.github.com/vwood/1841911
mods: py3 syntax, hex_col -> RGB, +quantized-tile.size, +tk.rect.no.border,
+border-corner-conditions, vNeumann->Moore-neighbours, +perturbate()
+multiprocessing, +tk.window.position (quadview),
+force happiness.check m-times before move_to_empty(), +racefrequency(weight)
"""

import tkinter as Tk
from random import randint
from multiprocessing import Process

class Schelling():
    """Schelling's ethnic segregation model."""
    def __init__(self, width, height, races, tile, neighbours, freespace):
        self.width, self.height = width, height
        self.races = races
        self.tile = tile
        self.neighbours = neighbours
        self.freespace = freespace
        self.race_array = [[0] * self.height for x in range(self.width)] 
        self.tk_array = [[0] * self.height for x in range(self.width)] 
        self.empty_spaces = []

        race_frequency = []
        for race in range(self.races):
            race_frequency.append((int(self.races-(race-1))**2))
        race_counter = [0,0,0,0,0]
        self.race_frequency = race_frequency[0:self.races]        
        self.race_counter = race_counter[0:self.races]
        self.copy_counter = self.race_counter[:]
        self.raceRGB = ((0,200,255), #Caucasian
                   (255,0,0), #Asian
                   (255,200,0), #Latino Hispanic
                   (0,255,0), #African
                   (180,0,180)) #Native American
        self.race_colors_list = []
        for i in range(self.races):
             self.race_colors_list.append('#%02x%02x%02x' % self.raceRGB[i])
        self.race_colors = ()
        self.race_colors = self.race_colors_list[:]
        print(self.race_colors,race_frequency)


    def populate_list(self):
        self.empty_spaces = []
        for x in range(self.width):
            for y in range(self.height):
                flag = False
                if randint(0, self.freespace) == 0:
                    self.race_array[x][y] = 0
                    self.empty_spaces.append((x, y))
                else:
                    while flag == False:
                        race = randint(0,self.races-1)
                        if self.race_counter[race] < self.race_frequency[race]:
                            self.race_array[x][y] = race+1
                            self.race_counter[race] += 1
                            flag = True
                        elif self.race_counter == self.race_frequency:
                            self.race_counter = self.copy_counter[:]

    def perturbate_list(self, lifetime=40, m=20):
        for i in range(lifetime):
            x = randint(0, self.height-1)
            y = randint(0, self.width-1)
            if self.race_array[x][y] != 0:
                newrace = randint(1, self.races)
                self.race_array[x][y] = newrace
                self.canvas.itemconfig(self.tk_array[x][y],
                                       fill=self.race_colors[newrace-1])
                if self.happiness(x, y) == False:
                    j = 0
                    happy = False
                    while (happy == False) and (j < m):
                        j += 1
                        HappyCoords = self.move_to_empty(x, y)
                        happy = self.happiness(HappyCoords[0], HappyCoords[1])
                        x = HappyCoords[0]
                        y = HappyCoords[1]

    def fill_canvas(self, canvas):
        """Fills the canvas with objects"""
        self.canvas = canvas
        tile = self.tile
        for x in range(self.width):
            for y in range(self.height):
                if self.race_array[x][y] == 0:
                    self.tk_array[x][y] = 0
                else:
                    race = self.race_array[x][y]
                    self.tk_array[x][y] = self.canvas.create_rectangle(
                        x * tile, y * tile,
                        (x+1) * tile, (y+1) * tile,
                        fill=self.race_colors[race-1],
                        width=0)

    def update(self, n, m=20):
        """Check hapiness() n times. """
        for i in range(n):
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            if self.happiness(x, y) == False:
                j = 0
                happy = False
                while (happy == False) and (j < m):
                    j += 1
                    HappyCoords = self.move_to_empty(x, y)
                    happy = self.happiness(HappyCoords[0], HappyCoords[1])
                    x = HappyCoords[0]
                    y = HappyCoords[1]

    def updateborder(self, m=20):
        """Check whole boder."""
        width = self.width
        height = self.height
        n = (width-1) * 2 + (height-1) * 2
        Border = []
        for i in range(0, width):
            CoordsTop = (0, i)
            Border.append(CoordsTop)
            CoordsBottom = (height-1, i)
            Border.append(CoordsBottom)
        for j in range(1, height-1):
            CoordsLeft = (j, 0)
            Border.append(CoordsLeft)
            CoordsRight = (j, width-1)
            Border.append(CoordsRight)   

        for i in range(n):
            x = Border[i][0]
            y = Border[i][1]
            if self.happiness(x,y) == False:
                j = 0
                happy = False
                while (happy == False) and (j < m):
                    j += 1
                    HappyCoords = self.move_to_empty(x,y)
                    happy = self.happiness(HappyCoords[0], HappyCoords[1])
                    x = HappyCoords[0]
                    y = HappyCoords[1]

    def move_to_empty(self, x1, y1):
        """Moves to an empty cell."""
        new_cell = randint(0, len(self.empty_spaces) - 1)
        x2, y2 = self.empty_spaces[new_cell]
        tile = self.tile

        self.race_array[x1][y1], self.race_array[x2][y2] = \
        self.race_array[x2][y2], self.race_array[x1][y1]
        
        self.canvas.coords(self.tk_array[x1][y1], \
        x2 * tile, y2 * tile, (x2+1) * tile, (y2+1) * tile)

        self.tk_array[x1][y1], self.tk_array[x2][y2] = \
        self.tk_array[x2][y2], self.tk_array[x1][y1]

        self.empty_spaces[new_cell] = (x1,y1)
        return (x2,y2)

    def happiness(self, x, y):
        """Agent is unhappy with less than
        i same race neighbours. Empty squares are never unhappy.
        Special border and corner conditions apply."""
        agent = self.race_array[x][y]
        if agent == 0:
            return True
        if x > 0 and x < self.width-1 and y > 0 and y < self.height-1:
            return self.infield_hapiness(x, y, agent)
        else:
            return self.border_hapiness(x, y, agent)

    def infield_hapiness(self, x, y, agent):
        """Check Moore neighbourhood for at least i neighbours."""
        counter = 0
        for a in range(-1,2):
            for b in range(-1,2):
                if self.race_array[x+a][y+b] == agent:
                    counter += 1
                elif self.race_array[x+a][y+b] == 0:
                    counter += (self.neighbours/10)
        return int(counter) >= self.neighbours


    def border_hapiness(self, x, y, agent):
        """Check border/corner neighbourhood for at least i neighbours."""
        counter = 0
        missing = 0
        satisfaction = self.neighbours
        for a in range(-1,2):
            for b in range(-1,2):
                if x == 0 and y == 0:
                    pass
                if x+a < 0 or y+b < 0:
                    missing += 1
                else:
                    try:
                        if self.race_array[x+a][y+b] == agent:
                            counter += 1
                    except:
                        missing += 1
        if missing == 5:
            satisfaction = int(self.neighbours-(self.neighbours/2))
        elif missing== 3:
            satisfaction = int(self.neighbours-(self.neighbours/3))
        return counter >= satisfaction


class SchellingApp():
    def __init__(self, w = 300, h = 300, tile = 10,
                 neighbours = 4, freespace = 9, races = 2,
                 offsetx = 1, offsety = 1):
        self.neighbours = neighbours
        if self.neighbours > 8:
            self.neighbours = 8
        self.freespace = freespace
        if self.freespace < 1:
            self.freespace = 1
        self.races = races
        if self.races > 5:
            self.races = 5
        self.offsetx = offsetx
        self.offsety = offsety
        self.Clock = 0
        self.tile = tile
        self.w, self.h = w, h

        self.SimScreen = Tk.Tk()
        self.SimScreen.title("%d Nachbarn & 1:%d Frei" % (self.neighbours,self.freespace+1))
        self.SimScreen.maxsize(w, h)
        self.SimScreen.configure(background ='#%02x%02x%02x' % (0,0,0))
        SimSW = self.SimScreen.winfo_screenwidth()
        SimSH = self.SimScreen.winfo_screenheight()
        x = (SimSW/2) - (w/2) + (self.offsetx*self.w/2)
        if self.offsety == 1:
            y = (SimSH/2) - (h/2) + (self.offsety*self.h/2)
        else:
            y = (SimSH/2) - (h/2) + (self.offsety*self.h/2) -30
        self.SimScreen.geometry('%dx%d+%d+%d' % (self.w, self.h, x, y))

        self.SimCanvas = Tk.Canvas(self.SimScreen,
                                   width = self.w, height = self.h)
        self.SimCanvas.configure(background ='#%02x%02x%02x' % (0,0,0))
        self.SimCanvas.configure(borderwidth=0, relief='flat')
        self.SimCanvas.bind("<Button-1>", self.restart)
        self.SimCanvas.pack()

        self.Sim = Schelling(int(self.w/self.tile), int(self.h/tile),
                             self.races, self.tile,
                             self.neighbours, self.freespace)
        self.Sim.populate_list()
        self.Sim.fill_canvas(self.SimCanvas)
        self.update()
        self.SimScreen.mainloop()

    def restart(self, cursorpos):
        self.SimCanvas.delete("all")
        self.Sim.populate_list()
        self.Sim.fill_canvas(self.SimCanvas)     

    def update(self):
        self.Clock += 1
        UpdateTimes = 250
        if self.Clock >= 10:
            self.Clock = 0
            #self.Sim.perturbate_list(10)
            self.Sim.updateborder()
            self.Sim.update(UpdateTimes)
            self.SimCanvas.after(1, self.update)
        else:
            self.Sim.update(UpdateTimes)
            self.SimCanvas.after(1, self.update)

if __name__ == '__main__':
    x,y = 300,300 #window.resolution.px
    t = 10 #tile.size.px
    f = 9 #freesspace 1:f
    r = 5 # race.diversity
    Sim1 = Process(target=SchellingApp, args=(x, y, t, 8, f, r, -1, -1))
    Sim2 = Process(target=SchellingApp, args=(x, y, t, 7, f, r, 1, -1))
    Sim3 = Process(target=SchellingApp, args=(x, y, t, 6, f, r, -1, 1))
    Sim4 = Process(target=SchellingApp, args=(x, y, t, 5, f, r, 1, 1))
    Sim1.start()    #left upper
    Sim2.start()    #right upper
    Sim3.start()    #left lower
    Sim4.start()    #right lower
