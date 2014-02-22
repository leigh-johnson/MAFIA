from kivy.app import App
from kivy.uix.accordion import Accordtion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.garden.navigationdrawer import NavigationDrawer


sm = ScreenManager()


class Mafia(App):

    def build(self):
        root = NavigationDrawer()

        menu = BoxLayout(orientation='vertical')

        resetButton = Button(text='New Game')
        settingsButton = Button(text='Settings')
        helpButton = Button(text='Help')
        menu.add_widget(resetButton)
        menu.add_widget(settingsButton)
        menu.add_widget(helpButton)

        root.add_widget(menu)

        content = BoxLayout(orientation='horizontal')

        toggleButton = Button (text='Menu', size_hint=(.2, 1))
        toggleButton.bind(on_press=lambda j: root.toggle_state())

        content.add_widget(sm)
        content.add_widget(toggleButton)
        root.add_widget(content)
        return root

if __name__ == '__main__':
    Mafia().run()