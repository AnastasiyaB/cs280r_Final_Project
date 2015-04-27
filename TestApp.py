import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.clock import Clock
from kivy.lang import Builder

import firesim

class FireUI(BoxLayout):
    pass

class FireModel(GridLayout):
    pass

class CustomLayout(Widget):
    def __init__(self, cols, x, y, sz, cellType = "fuel", intensity = None, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)
        self.cols = cols
        self.x = x
        self.y = y
        self.sz = sz
        self.cellType = cellType
        self.intensity = intensity
        
        #with widget.canvas:
        with self.canvas.before:
            #Color(.7, .7, .7, 1)  # gray; colors range from 0-1 instead of 0-255
            #if self.intensity:
            Color(rgb = self.generateColor())
            #else:
            #Color((self.x + self.y)/float(cols*2), 0, 0, 1)
            #self.rect = Rectangle(size=self.size, pos=self.pos)
            self.rect = Rectangle(pos=(self.sz*self.x+(self.sz/2), self.sz*self.x+(self.sz/2)), size=(self.sz, self.sz))

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def generateColor(self):
        rgb = (0, 0, 0)
        i = self.intensity
        if self.cellType == "fuel":
            rgb = (0, i, 0)
        else:
            rgb = (1, i, 0)
        return rgb

    def update(self, intensity):
        self.intensity = intensity
        with self.canvas.before:
            Color(rgb = self.generateColor())
            self.rect = Rectangle(pos=(self.sz*self.x+(self.sz/2), self.sz*self.x+(self.sz/2)), size=(self.sz, self.sz))


class FireApp(App):
    def __init__(self, cols, size, iters = 50, **kwargs):
        super(FireApp, self).__init__(**kwargs)
        self.cols = cols
        self.size = size
        self.slabel = Label(text='0', size_hint=(1, .05))
        self.model = None
        self.vals = []
        self.iters = iters
        self.currIter = 0

    def OnSliderValueChange(self, instance, value):
        self.slabel.text = str(value)
        self.currIter = int(value)
        self.updateCells()

    def generateSim(self):
        sim = firesim.AreaSimulation(self.cols)
        sim.initialize()
        for i in range(self.iters):
            self.vals.append(sim.grid)
            sim.gnew()

    def updateCells(self):
        if self.model and self.model.children:
            self.model.clear_widgets()
        subSize = self.size/self.cols
        for x in range(self.cols):
            for y in range(self.cols):
                if self.vals:
                    fire_inten = self.vals[self.currIter][(x, y)].fire_inten
                    if x == 0 and y == 0:
                        print self.vals[self.currIter][(x, y)].fire_inten
                        #self.grid[(1,2)].fire_inten = .55

                    ct = "fire" if fire_inten else "fuel"
                    it = fire_inten if fire_inten else self.vals[self.currIter][(x, y)].veg_inten
                    c = CustomLayout(self.cols, x, y, subSize, cellType = ct, intensity = it)
                else:
                    c = CustomLayout(self.cols, x, y, subSize)
                self.model.add_widget(c)
        
    def build(self):
        self.generateSim()
        
        root = FireUI(orientation='vertical', size=(800, 1000))
        
        self.model = FireModel(cols = self.cols, size_hint=(1, .8))
        self.updateCells()

        s = Slider(max = self.iters-1, step = 1, size_hint=(1, .15))
        s.bind(value = self.OnSliderValueChange)
        
        root.add_widget(self.model)
        root.add_widget(s)
        root.add_widget(self.slabel)
        #Clock.schedule_interval(game.update, 1.0 / 60.0)
        return root


if __name__ == '__main__':
    FireApp(30, 300).run()
