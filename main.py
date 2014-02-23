from kivy.app import App
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.garden.navigationdrawer import NavigationDrawer
import random

Builder.load_file('screens.kv')

gameValues = JsonStore('gameValues.json')
gameSetups = JsonStore('gameSetups.json')
players = JsonStore('players.json')


class multiLineLabel(Label):
    def __init__(self, **kw):
        super(multiLineLabel, self).__init__(**kw)
        self.bind(size=self.setter('text_size'))

class multiLineButton(Button):
    def __init__(self, **kw):
        super(multiLineButton, self).__init__(**kw)
        self.bind(size=self.setter('text_size'))

class titleScreen(Screen):
    def wipeJson(self):
        gameValues.clear()
        players.clear()
class setNumber(Screen):

    def putNumber(self):
        '''JsonStore.put(key, value=thingy)'''
        gameValues.put('playerNumber', value=int(self.ids.playerNumberSlider.value))

class setSetup(Screen):

    #to-do: add image src to gameSetup arrays
    def buildContent(self):
        setupList = []
        for key in gameSetups.keys():
            if gameSetups.get(key).get('playerNumber') == gameValues.get('playerNumber').get('value'):
                setupList.append(str(key))
        for setup in setupList:
            item = AccordionItem(title=setup)
            itemContent = multiLineLabel(text=gameSetups.get(setup).get('description'), halign='center', valign='middle')
            item.add_widget(itemContent)
            self.ids.setupAccordion.add_widget(item)

    def putSetup(self):
        for child in self.ids.setupAccordion.children:
            if child.collapse_alpha == 0:
                gameValues.put('setupName', value=child.title)

class setPlayers(Screen):

    def buildContent(self):
        for i in range(gameValues.get('playerNumber').get('value')):
            text = TextInput(hint_text='Enter player name', multiline=False, focus=True)
            self.ids.playerGrid.add_widget(text)

    def putPlayers(self):
        #to-do: add check for empty field
        playerList = []
        for child in self.ids.playerGrid.children:
            playerList.append(child.text)
        gameValues.put('playerList', value=playerList)

class roleDistribution(Screen):

    def randomize(self):
        roleList = []
        playerList = gameValues.get('playerList').get('value')
        setupName = gameValues.get('setupName').get('value')
        for role in gameSetups.get(setupName).get('roles'):
            roleList.append(str(role))

        random.shuffle(roleList)
        for player in playerList:
            players.put(player, role=roleList[0])
            roleList.pop(0)


    def buildContent(self):
        playerList = gameValues.get('playerList').get('value')
        self.ids.roleSpinner.values = playerList

    def updateContent(self, instance):
        '''a roleSpinner instance'''
        playerName = instance.text
        role = players.get(playerName).get('role')
        winCon = 'Your wincon goes here'
        #roleText = role.json.get(role)

        if role == 'Vanilla Scum' or 'masonTown':
            print ('I have not matched your buddy yet')
        else:
            roleText = 'The role descriptions are not written yet'
            self.ids.rolePanel.text = ('Hello', playerName, '\n', 'You are a', role, roleText, winCon)
        self.ids.destroyButton.text = ('Cast this message into the flames')

    def destroyContent(self, instance):
        self.ids.rolePanel.text = 'initial text'



class Day(Screen):
    pass

class Night(Screen):
    pass
sm = ScreenManager()

sm.add_widget(titleScreen(name='titleScreen'))
sm.add_widget(setNumber(name='setNumber'))
sm.add_widget(setSetup(name='setSetup'))
sm.add_widget(setPlayers(name='setPlayers'))
sm.add_widget(roleDistribution(name='roleDistribution'))
sm.add_widget(Day(name='Day'))
sm.add_widget(Night(name='Night'))

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