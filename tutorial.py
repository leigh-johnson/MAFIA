from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.animation import Animation
from main import multiLineLabel

class tutorial1(Screen):
    pass

class tutorial2(Screen):

    pass
class tutorial3(Screen):
    lillyPopup = Popup(title='Lilly',
        content=multiLineLabel(text='You are an ordinary citizen, with no special powers or knowledge. You win when all threats to The Village are eliminated',
             halign='center', valign='middle'),
        size_hint=(.6, .6))
    snapePopup = Popup(title='Snape',
        content=multiLineLabel(text="You are a Goon. You want to wrest control of The Village from its citizens. You win when living Mafia players make up a majority of The Village. ",
             halign='center', valign='middle'),
        size_hint=(.6,.6), halign='center', valign='middle')

class tutorial3(Screen):
    pass

class tutorial4(Screen):
    pass

class tutorial5(Screen):
    pass


Builder.load_file('tutorial.kv')
Builder.load_file('styles.kv')
sm = ScreenManager()
sm.add_widget(tutorial1(name='tutorial1'))
sm.add_widget(tutorial2(name='tutorial2'))
sm.add_widget(tutorial3(name='tutorial3'))
sm.add_widget(tutorial4(name='tutorial4'))
sm.add_widget(tutorial5(name='tutorial5'))

class tutorial(App):

    def build(self):

        return sm

tutorial().run()
