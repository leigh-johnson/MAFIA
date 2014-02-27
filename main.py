from kivy.app import App
from kivy.clock import Clock
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.garden.navigationdrawer import NavigationDrawer
from gameRoles import gameRoles
import random

Builder.load_file('screens.kv')

gameValues = JsonStore('gameValues.json')
gameSetups = JsonStore('gameSetups.json')
players = JsonStore('players.json')

class TimerButton(Button):

    def __init__(self, seconds, **kwargs):
        super(TimerButton, self).__init__(**kwargs)
        self.seconds = seconds
        self.text = 'Start Day: %s seconds' %self.seconds

    def on_press(self):
        Clock.schedule_once(self.timeCall, 1)

    def timeCall(self, dt):
        if self.seconds > 0:
            self.seconds -= 1
            self.text = "Day ends in: %s seconds" % self.seconds
            Clock.schedule_once(self.timeCall, 1)
        else:
            sm.current = 'dayResolution'

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

        #small hack to account for RNG in 9p Cop+Town/Masons
        if setupName == "Cop & Vanilla OR Masons":
            #array is [0, 1, n] where 0, 1 are [faction_Role-faction_role] pairs
            subList = gameSetups.get("Cop & Vanilla OR Masons").get('roles')[0:2]
            random.shuffle(subList)
            roleList.append(subList[0].split("-")[0])
            roleList.append(subList[0].split("-")[1])
            for role in gameSetups.get(setupName).get('roles')[2:]:
                roleList.append(str(role))

        #role array of other setups is 1-1
        else:
            for role in gameSetups.get(setupName).get('roles'):
                roleList.append(str(role))

        random.shuffle(roleList)

        for player in playerList:
            splitList = roleList[0].split("_")
            players.put(player, faction=splitList[0], role=splitList[1])
            roleList.pop(0)

    def buildContent(self):
        playerList = gameValues.get('playerList').get('value')

        for player in playerList:
            roleButton = Button(text=player)
            roleButton.name = player
            roleButton.bind(on_press=self.buildPopup)
            self.ids.roleLayout.add_widget(roleButton)


    def buildPopup(self, instance):
        roleName = players.get(instance.text).get('role')
        content = BoxLayout(orientation='vertical')
        content.add_widget(multiLineLabel(text=gameRoles.get(roleName).get('info'),
            halign='center', valign='middle' ))
        if gameRoles.get(roleName).get('partner') == True:
            if roleName == 'Mason':
                partners = list(players.find(role='Mason'))
                #removes playerName
                partners[:] = [i for i in partners if i[0] != instance.text]
                partnerStr = ''
                for n in partners:
                    partnerStr += '\n' + str(n[0]) + ' the Mason'
            else:
                partners = list(players.find(faction='Mafia'))
                #removes playerName from set via instance.text
                partners[:] = [i for i in partners if i[0] != instance.text]
                partnerStr = ''
                #build a string
                for n in partners:
                    partnerStr += '\n ' + str(n[0]) + ' the '
                    partnerStr += str(n[1].get('role')) + '\n'
            content.add_widget(Label(text=('You are teamed up with:  [b]%s[/b]' % partnerStr), markup=True,
            halign='center', valign='middle'))
        rolePopup = Popup(title =roleName, content=content,
            size_hint=(.6, .6))
        rolePopup.name = instance.text
        rolePopup.bind(on_dismiss=self.removeButton)
        rolePopup.open()

    def removeButton(self, instance):
        '''Removes a child of ids.roleLayout, playerName passed as instance.name'''
        '''Implemented to avoid awkward situations where user has access to already-viewed roles'''
        #instance of RolePopup()
        for child in self.ids.roleLayout.children:
            if child.name == instance.name:
                self.ids.roleLayout.remove_widget(child)
        #after all the roles are distributed, add a Start button
        if self.ids.roleLayout.children == []:
            sm.current = 'deadlineTimer'

class deadlineTimer(Screen):
    '''Counts down from settings.deadline'''
    def buildContent(self):
        self.add_widget(TimerButton(2))

class dayResolution(Screen):

    def buildContent(self):
        for i in players.keys():
            playerButton = Button(text=i)
            playerButton.bind(on_press=self.lynchPlayer)
            self.ids.dayLayout.add_widget(playerButton)

    def lynchPlayer(self, instance):
        print(instance.text + ' is dead')

class Night(Screen):
    pass

class Settings(Screen):

    #from kivy.uix.settings
    pass



sm = ScreenManager()

sm.add_widget(titleScreen(name='titleScreen'))
sm.add_widget(setNumber(name='setNumber'))
sm.add_widget(setSetup(name='setSetup'))
sm.add_widget(setPlayers(name='setPlayers'))
sm.add_widget(roleDistribution(name='roleDistribution'))
sm.add_widget(deadlineTimer(name='deadlineTimer'))
sm.add_widget(dayResolution(name='dayResolution'))
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