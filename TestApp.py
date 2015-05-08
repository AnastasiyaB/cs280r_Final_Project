import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.graphics import *
from kivy.clock import Clock
from kivy.lang import Builder

import firesim
import firetests

class FireUI(GridLayout):
    pass

class FireModel(GridLayout):
    pass

class FireFighters(GridLayout):
    pass

class InputPanel(BoxLayout):
    def __init__(self, size_hint, **kwargs):
        super(InputPanel, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = size_hint
        self.spacing = 3

class Fighter(Widget):
    def __init__(self, x, y, effectiveness, **kwargs):
        # make sure we aren't overriding any important functionality
        super(CustomLayout, self).__init__(**kwargs)
        self.cols = cols
        self.x = x
        self.y = y
        self.sz = sz
        self.cellType = cellType
        self.intensity = intensity    

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
        elif self.cellType == "fire":
            rgb = (1, i, 0)
        else:
            rgb = (0, 0, 1)
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
        self.slider = None
        self.vals = []
        self.iters = iters
        self.currIter = 0
        self.inputs = {}

    def OnSliderValueChange(self, instance, value):
        self.slabel.text = str(value)
        self.currIter = int(value)
        self.updateCells()

    def generateSim(self, value=0):
        self.currIter = 0
        self.vals = []
        sim = firesim.AreaSimulation(self.cols)
        sim.initialize()
        if self.inputs:
            params = {'Size': 0, 'Shape': 0, 'FF': 0}
            for i in range(len(self.inputs["Size"])):
                ipt = self.inputs["Size"][i]
                if ipt.active:
                    params['Size'] = i
            for i in range(len(self.inputs["Shape"])):
                ipt = self.inputs["Shape"][i]
                if ipt.active:
                    params['Shape'] = i
            for i in range(len(self.inputs["FF"])):
                ipt = self.inputs["FF"][i]
                if ipt.active:
                    params['FF'] = i

            testSize = self.cols
            totalNumFFs = int(self.inputs['numFFs'].text)
            fires = []
            center = (testSize/2, testSize/2)
            radius = params['Size'] + 1
            if params['Shape'] == 0:
                fire = firetests.generateRoundFire(center, radius)
            elif params['Shape'] == 1:
                fire = firetests.generateEllipseFire(center, radius*2, radius)
            else:
                fire = firetests.generateOddFire(center, radius)
            cells = fire
            c = 0
            for x, y, inten in cells:
                sim.grid[(x, y)].fire_inten = inten
                c += 1
            sim.num_fires = c
            if params['FF'] == 0:
                ff_config = firetests.generatePointFFs(center, radius, numFFs = totalNumFFs)
            elif params['FF'] == 1:
                ff_config = firetests.generateSurroundFFs(center, radius, numFFs = totalNumFFs)
            else:
                ff_config = sim.best_ff_config(totalNumFFs)

            for ff in ff_config:
                ff = firesim.FireFighter(ff[0], ff[1], sim, style = 'optimal', efficacy = 1)
                sim.fight_fire(ff)
            
        for i in range(self.iters):
            self.vals.append(sim.grid)
            print sim.num_fires
            if sim.num_fires == 0:
                print "victory"
            sim.gnew()

        if self.model:
            self.updateCells()
        if self.slider:
            self.slider.value = 0

    def updateCells(self):
        if self.model and self.model.children:
            self.model.clear_widgets()
        subSize = self.size/self.cols
        for x in range(self.cols):
            for y in range(self.cols):
                if self.vals:
                    if self.vals[self.currIter][(x, y)].firefighter:
                        c = CustomLayout(self.cols, x, y, subSize, cellType = "ff")
                    else:
                        fire_inten = self.vals[self.currIter][(x, y)].fire_inten
                        ct = "fire" if fire_inten else "fuel"
                        it = fire_inten if fire_inten else self.vals[self.currIter][(x, y)].veg_inten
                        c = CustomLayout(self.cols, x, y, subSize, cellType = ct, intensity = it)
                else:
                    c = CustomLayout(self.cols, x, y, subSize)
                self.model.add_widget(c)
        
    def build(self):
        self.generateSim()
        
        root = FireUI(cols=2, size=(800, 1000))
        
        self.model = FireModel(cols = self.cols, size_hint=(.7, .8))
        self.updateCells()

        self.slider = Slider(max = self.iters-1, step = 1, size_hint=(1, .15))
        self.slider.bind(value = self.OnSliderValueChange)

        panel = InputPanel(size_hint=(.27, .8))
        # deflt = {"Fire": [(1, 2, .55), (1, 1, .6), (2, 1, .31)], "FF": [(3, 2, 1), (4, 5, 1), (5, 1, 1)]}
        # inputs = {'Fire': [], 'FF': []}
        # for t in ['Fire', 'FF']:
        #     for i in range(1, 4):
        #         panel.add_widget(Label(text = str(t) + " " + str(i) + ' Coords: x, y, int', size_hint=(1, .15)))
        #         inpt = GridLayout(cols = 3, size_hint = (1, .15))
        #         tup = ()
        #         for j in range(3):
        #             txt = TextInput(text=str(deflt[t][i-1][j]), multiline = False)
        #             tup += (txt,)
        #             inpt.add_widget(txt)
        #         panel.add_widget(inpt)
        #         inputs[t].append(tup)
        # self.inputs = inputs

        deflt = {'Size': ['Small', 'Med', 'Large'], 'Shape': ['Round', 'Ellipse', 'Odd'], 'FF': ['Point', 'Surround', 'Optimal']}
        inputs = {'Size': [], 'Shape': [], 'FF': [], 'numFFs': None}
        panel.add_widget(Label(text = 'Num Firefighters', size_hint=(1, .15)))
        inputs['numFFs'] = TextInput(text='8', multiline = False)
        box = BoxLayout(size_hint=(1, .15))
        box.add_widget(inputs['numFFs'])
        panel.add_widget(box)
        for t in ['Size', 'Shape', 'FF']:
            panel.add_widget(Label(text = str(t), size_hint=(1, .15)))
            inpt = GridLayout(cols = len(deflt[t]), size_hint = (1, .15))
            for j in range(len(deflt[t])):
                inpt.add_widget(Label(text = str(deflt[t][j]), size_hint=(1, .05)))
            for j in range(len(deflt[t])):
                rdio = CheckBox(group = t)
                inpt.add_widget(rdio)
                inputs[t].append(rdio)
            panel.add_widget(inpt)
        self.inputs = inputs
        
        genBtn = Button(text="Generate!!", size_hint=(1, .15))
        panel.add_widget(genBtn)
        genBtn.bind(on_press = self.generateSim)
        
        root.add_widget(self.model)
        root.add_widget(panel)
        root.add_widget(self.slider)
        #root.add_widget(self.slabel)
        #Clock.schedule_interval(game.update, 1.0 / 60.0)
        return root


if __name__ == '__main__':
    FireApp(30, 300).run()
