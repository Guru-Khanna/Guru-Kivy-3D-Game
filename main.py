from kivy.config import Config

Config.set("graphics", "width", "900")
Config.set("graphics", "height", "400")

from kivy.app import App
# import os
from kivy.lang.builder import Builder
from kivy.uix.relativelayout import RelativeLayout
from random import randint
from kivy import platform
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Quad
from kivy.graphics.vertex_instructions import Triangle
from kivy.graphics.vertex_instructions import Line
from kivy.core.window import Window

Builder.load_file("menu.kv")

class EscapeTheRoadApp(App):
    pass

class MainWidget(RelativeLayout):

    # Variables

    ppx=NumericProperty()
    ppy=NumericProperty()
    menu_widget=ObjectProperty()
    menutitle=StringProperty("E    S    C    A    P    E        T    H    E        R    O    A    D")
    menubuttontitle=StringProperty("S T A R T")
    score_txt=StringProperty()

    carcoords=[0, 0, 0]
    
    "Vertical"
    
    vlines=[]
    vlinesno=16
    vlinespacing=.4
    xofsett=0
    speedx=0

    "Horizontal"

    hlines=[]
    hlinesno=6
    hlinespacing=0.2
    offsety=0
    speed=0.010

    tilesno=16
    tiles=[]
    tilecoords=[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
    loopno=0

    car=None
    carwidth=0.1
    carheight=0.035
    carbasey=0.04

    lava=[]
    lavacoords=[]

    isgo=False
    isstart=False
    isstarted=False

    # Initialising

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawvlines()
        self.drawhlines()
        self.initlava()
        # self.makelavaquards()
        # self.updatelava()
        # self.inittiles()
        self.maketilequards()
        # self.drawlava()
        Clock.schedule_interval(self.update, 1/55)
        if self.device():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
            self.inittiles()
        
        self.drawcar()
        self.score_txt='Score: 0'

    def resetgame(self):
        self.tilecoords=[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
        self.loopno=0
        self.offsety=0
        self.xofsett=0
        self.maketilequards()
        self.isgo=False
        

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard.unbind(on_key_up=self.on_keyboard_up)
        self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.speedx=0.03
        elif keycode[1] == 'right':
            self.speedx=-0.03
        return True

    def on_keyboard_up(self, keyboard, keycode):
        self.speedx=0

    def device(self):
        if platform in ("linux", "win", "macosx"):
            return True
        return False

    # Updating the lines

    # Vertical line display

    def drawvlines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.vlinesno):
                self.vlines.append(Line())

    def getvlinesbyindex(self, index):
        linecenterx=self.ppx
        offset=index-0.5
        spacev=self.vlinespacing*self.width
        linex=linecenterx+offset*spacev+self.xofsett
        return linex

    def updatevlines(self):
        sindex=-int(self.vlinesno/2)+1
        for i in range(sindex, sindex+self.vlinesno):
            self.linex=self.getvlinesbyindex(i)
            x1, y1=self.transform(self.linex, 0)
            x2, y2=self.transform(self.linex, self.height)
            self.vlines[i].points=[x1, y1, x2, y2]
    
    # Horizotal Line display
    
    def drawhlines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.hlinesno):
                self.hlines.append(Line())
    
    def gethlinesbyindex(self, index):
        spacingy=self.hlinespacing*self.height
        liney=index*spacingy-self.offsety
        return liney
    
    def updatehlines(self):
        sindex=-int(self.vlinesno/2)+1
        eindex=sindex+self.vlinesno-1

        xmin=self.getvlinesbyindex(sindex)
        xmax=self.getvlinesbyindex(eindex)
        for i in range(0, self.hlinesno):
            self.liney=self.gethlinesbyindex(i)
            x1, y1=self.transform(xmin, self.liney)
            x2, y2=self.transform(xmax, self.liney)
            self.hlines[i].points=[x1, y1, x2, y2]

    # Transformation

    def transform(self, x, y):
        # return x, y
        return self.transformperspective(x, y)
    
    def transformperspective(self, x, y):
        ty=y*self.ppy/self.height
        if ty > self.ppy:
            ty=self.ppy

        diffx=x-self.ppx
        diffy=self.ppy-ty
        propy=diffy/self.ppy
        propy=propy**3

        tx=self.ppx+(diffx*propy)
        ty2=self.ppy-propy*self.ppy

        return int(tx), int(ty2)

    def gettilecoordinates(self, tx, ty):
        ty=ty-self.loopno
        y=self.gethlinesbyindex(ty)
        x=self.getvlinesbyindex(tx)
        return x, y

    def getlavacoordinates(self, tx, ty):
        y=self.gethlinesbyindex(ty)
        x=self.getvlinesbyindex(tx)
        return x, y

    def inittiles(self):
        with self.canvas:
            Color(0.5,0.5,.5)
            for i in range(0, self.tilesno):
                self.tiles.append(Quad())

    def maketilequards(self):
        lasty=0
        lastx=0

        for i in range(len(self.tilecoords)-1, -1, -1):
            if self.tilecoords[i][1]<self.loopno:
                del self.tilecoords[i]

        if len(self.tilecoords)>0:
            lastcoords=self.tilecoords[-1]
            
            lastx=lastcoords[0]
            lasty=lastcoords[1]+1

        for i in range(len(self.tilecoords), self.tilesno):
            r=randint(0,2)

            sindex=-int(self.vlinesno/2)+1
            eindex=sindex+self.vlinesno-2

            if lastx<=sindex:
                r=2
            if lastx>=eindex:
                r=1
            
            self.tilecoords.append((lastx, lasty))

            if r==1:
                    lastx-=1
                    self.tilecoords.append((lastx, lasty))
                    lasty+=1
                    self.tilecoords.append((lastx, lasty))
            if r==2:
                    lastx+=1
                    self.tilecoords.append((lastx, lasty))
                    lasty+=1
                    self.tilecoords.append((lastx, lasty))
            lasty+=1

    def updatetiles(self):
        for i in range(0, self.tilesno):
            tile=self.tiles[i]
            tilequads=self.tilecoords[i]
            xmin, ymin=self.gettilecoordinates(tilequads[0], tilequads[1])
            xmax, ymax=self.gettilecoordinates(tilequads[0]+1, tilequads[1]+1)
            x1, y1=self.transform(xmin, ymin)
            x2, y2=self.transform(xmin, ymax)
            x3, y3=self.transform(xmax, ymax)
            x4, y4=self.transform(xmax, ymin)

            tile.points=[x1, y1, x2, y2, x3, y3, x4, y4]

    def initlava(self):
        with self.canvas:
            Color(1,0.5,0)
            for i in range((self.vlinesno-2)*10):
                self.lava.append(Quad())

    def makelavaquards(self):
        sindex=-int(self.vlinesno/2)+1
        lasty=0
        lastx=sindex

        if len(self.lavacoords)>0:
            lastcoords=self.lavacoords[-1]
            
            lastx=lastcoords[0]
            lasty=lastcoords[1]+1
        for i in range((self.vlinesno-2)*10):
            r=1

            sindex=-int(self.vlinesno/2)+1
            eindex=sindex+self.vlinesno-2

            if lastx==sindex:
                r=2
            if lastx==eindex:
                r=1
            
            self.lavacoords.append((lastx, lasty))

            if r==1:
                for i2 in range((self.vlinesno-2)):
                    lastx-=1
                    self.lavacoords.append((lastx, lasty))
            if r==2:
                for i3 in range((self.vlinesno-2)):
                    lastx+=1
                    self.lavacoords.append((lastx, lasty))
            lasty+=1

    def updatelava(self):
        for i in range((self.vlinesno-2)*10):
            tile=self.lava[i]
            tilequads=self.lavacoords[i]
            xmin, ymin=self.getlavacoordinates(tilequads[0], tilequads[1])
            xmax, ymax=self.getlavacoordinates(tilequads[0]+1, tilequads[1]+1)
            x1, y1=self.transform(xmin, ymin)
            x2, y2=self.transform(xmin, ymax)
            x3, y3=self.transform(xmax, ymax)
            x4, y4=self.transform(xmax, ymin)

            tile.points=[x1, y1, x2, y2, x3, y3, x4, y4]

    def drawcar(self):
        with self.canvas:
            Color(1, 0, 0)
            self.car=Triangle()

    def updatecar(self):
        basey=self.carbasey*self.height
        carheight=self.carheight*self.height
        halfwidth=self.carwidth*self.width/2
        self.carcoords[0]=(self.ppx-halfwidth, basey)
        self.carcoords[1]=(self.ppx, basey+carheight)
        self.carcoords[2]=(self.ppx+halfwidth, basey)
        x1, y1=self.transform(self.ppx-halfwidth, basey)
        x2, y2=self.transform(self.ppx, basey+carheight)
        x3, y3=self.transform(self.ppx+halfwidth, basey)
        self.car.points=[x1, y1, x2, y2, x3, y3]
    
    def collisioncar(self, tx, ty):
        xmin, ymin=self.gettilecoordinates(tx, ty)
        xmax, ymax=self.gettilecoordinates(tx+1, ty+1)
        for i in range(0, 3):
            px, py=self.carcoords[i]
            if xmin<=px<=xmax and ymin<=py<=ymax:
                return True
        return False

    def collision(self):
        for i in range(0, len(self.tilecoords)):
            tix, tiy=self.tilecoords[i]
            if tiy>self.loopno+1:
                return False
            if self.collisioncar(tix, tiy):
                return True

    def update(self, dt):
        self.updatevlines()
        self.updatehlines()
        self.updatetiles()
        self.maketilequards()
        self.updatecar()
        self.makelavaquards()
        self.updatelava()
        self.timef=dt*60

        if (not self.isgo) and self.isstart:
            self.offsety+=self.speed*self.height*self.timef

            spacingy=self.hlinespacing*self.height
            while self.offsety>=spacingy:
                self.offsety-=spacingy
                self.loopno+=1
                self.score_txt="Score: "+str(self.loopno)
                highscoreopen1=open('C:\\Users\\khann\\Desktop\\Escape the road\\HighScore.txt', 'r')
                highscoreread=highscoreopen1.read()
                # print(highscoreread[0:highscoreread.find(" ")])
                if self.loopno>=int(highscoreread[0:highscoreread.find(" ")]):
                    highscoreopen2=open('HighScore.txt', 'w')
                    highscoreopen2.write(f"{self.loopno} {self.mode}")
                    highscoreopen2.close()
                highscoreopen1.close()

            self.xofsett+=self.speedx*self.width*self.timef

            if self.isstarted:
                self.speed+=0.000004
            
        if not self.collision() and not self.isgo:
            self.isgo=True
            self.menu_widget.opacity=1
            self.menutitle="         Y  O  U    F  E  L  L    I  N    T  H  E    L  A  V  A\nA  N  D    Y  O  U    B  U  R  N  E  D    T  O    A  S  H  E  S"
            self.menubuttontitle="R E S T A R T"

    def startgameonclick(self):
        self.isstart=True
        self.isstarted=False
        self.isgo=False
        self.menu_widget.opacity=0
        self.speed=0.008
        self.resetgame()
        self.mode="Easy"

    def startgamemediumonclick(self):
        self.isstart=True
        self.isstarted=False
        self.isgo=False
        self.menu_widget.opacity=0
        self.speed=0.012
        self.resetgame()
        self.mode="Medium"

    def startgamehardonclick(self):
        self.isstart=True
        self.isstarted=False
        self.isgo=False
        self.menu_widget.opacity=0
        self.speed=0.02
        self.resetgame()
        self.mode="Hard"

    def startgamegisonclick(self):
        self.isstart=True
        self.isstarted=True
        self.isgo=False
        self.menu_widget.opacity=0
        self.speed=0.008
        self.resetgame()
        self.mode="Gradual Speed Increase"

ap=EscapeTheRoadApp()
ap.run()