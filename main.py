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
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.garden.navigationdrawer import NavigationDrawer
from gameRoles import gameRoles
import random


class Player():
    name = StringProperty()
    status = StringProperty() #'Alive or Dead'
    faction = StringProperty()
    role = StringProperty()

######
Reck = Player()
Reck.name = 'Reck'
Fate = Player()
Fate.name = 'Fate'
Nuwen = Player()
Nuwen.name = 'Nuwen'
Hito = Player()
Hito.name = 'Hito'
Hiro = Player()
Brock = Player()
Brock.name = 'Brock'
Gamma = Player()


dummyList = [Reck, Fate, Nuwen, Hito, Brock]

######

#gameValues = JsonStore('gameValues.json')
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
            sm.add_widget(Day(name='Day %s' % Mafia.dayCount))
            sm.current = 'Day %s' % Mafia.dayCount

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
        pass

class setNumber(Screen):

    def store(self):
        '''Stores slider value'''
        Mafia.playerNumber = int(self.ids.playerNumberSlider.value)

class setSetup(Screen):

    #to-do: add image src to gameSetup arrays
    def buildContent(self):
        setupList = []
        for key in gameSetups.keys():
            if gameSetups.get(key).get('playerNumber') == Mafia.playerNumber:
                setupList.append(str(key))
        for setup in setupList:
            item = AccordionItem(title=setup)
            itemContent = multiLineLabel(text=gameSetups.get(setup).get('description'), halign='center', valign='middle')
            item.add_widget(itemContent)
            self.ids.setupAccordion.add_widget(item)

    def store(self):
        for child in self.ids.setupAccordion.children:
            if child.collapse_alpha == 0:
                Mafia.setup = child.title

class setPlayers(Screen):

    def buildContent(self):
        for i in range(Mafia.playerNumber):
            text = TextInput(hint_text='Enter player name', multiline=False, focus=True)
            self.ids.playerGrid.add_widget(text)

    def store(self):
        '''Creates a Player(), stores it in Mafia.aliveList'''
        #iterate over TextInput() for .text
        for child in self.ids.playerGrid.children:
            player = Player()
            player.name = child.text
            #add Player() to aliveList
            Mafia.aliveList.append(player)


class roleDistribution(Screen):

    def randomize(self):
        roleList = []
        #small hack to account for RNG in 9p Cop+Town/Masons
        if Mafia.setup == "Cop & Vanilla OR Masons":
            #array is [0, 1, n] where 0, 1 are [faction_Role-faction_role] pairs
            subList = gameSetups.get("Cop & Vanilla OR Masons").get('roles')[0:2]
            random.shuffle(subList)
            roleList.append(subList[0].split("-")[0])
            roleList.append(subList[0].split("-")[1])
            for role in gameSetups.get(Mafia.setup).get('roles')[2:]:
                roleList.append(str(role))

        #role array of other setups is 1-1
        else:
            for role in gameSetups.get(Mafia.setup).get('roles'):
                roleList.append(str(role))

        random.shuffle(roleList)

        for player in Mafia.aliveList:
            splitList = roleList[0].split("_")
            player.faction = splitList[0]
            player.role = splitList[1]
            player.status = 'alive'
            roleList.pop(0)

    def buildContent(self):

        for player in Mafia.aliveList:
            roleButton = Button(text=player.name)
            roleButton.name = player.name
            roleButton.bind(on_press=self.buildPopup)
            self.ids.roleLayout.add_widget(roleButton)


    def buildPopup(self, instance):
        '''Builds a popup, instance.text == Player.name'''
        #search for Player()
        content = BoxLayout(orientation='vertical')
        for entry in Mafia.aliveList:
            if entry.name == instance.text:
                player = entry

        content.add_widget(multiLineLabel(text=gameRoles.get(player.role).get('info'),
            halign='center', valign='middle' ))
        if gameRoles.get(player.role).get('partner') == True:
            if player.role == 'Mason':
                #search for other masons
                partners = []
                for entry in aliveList:
                    if entry.role == 'Mason':
                        partners.append(entry)
                partners[:] = [i for i in partners if i != instance.text]
                partnerStr = ''
                for n in partners:
                    partnerStr += '\n' + n.name + ' the Mason'
            else:
                partners = []
                for entry in Mafia.aliveList:
                    if entry.faction == 'Mafia':
                        partners.append(entry)
                #removes playerName from set via instance.text
                partners[:] = [i for i in partners if i.name != instance.text]
                partnerStr = ''
                #build a string
                for n in partners:
                    partnerStr += '\n ' + n.name + ' the ' + n.role + '\n'
            content.add_widget(Label(text=('Hello, ' + player.name + ' You are teamed up with:  [b]%s[/b]' % partnerStr), markup=True,
            halign='center', valign='middle'))
        rolePopup = Popup(title =player.role, content=content,
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

class Flip(Screen):

    def buildContent(self):
        print Mafia.deadList[-1].name + 'is dead'
        #continue
        pass
        #flipLabel= multiLineLabel(text='%(name)s is dead, he was a %(role)s aligned with the %(faction)s'
        #% {'name' : entry.name, 'role' : entry.role, 'faction': entry.faction}, font_size=20,
        #halign='center', valign='middle')

        #button = multiLineButton(text='Continue', size=(1, .3), halign='center', valign='middle')


class Day(Screen):

    def buildContent(self):
        for entry in Mafia.aliveList:
            playerButton = Button(text=entry.name)
            playerButton.bind(on_press=self.update)
            self.ids.dayGrid.add_widget(playerButton)

    def update(self, instance):
        '''Updates playerList item.status, clears widget tree,
        rebuilds content for role reveal'''
        #match button text to player name
        for entry in Mafia.aliveList:
            if entry.name == instance.text:
                entry.status = 'dead'
                print (instance.text + ' is dead')
                Mafia.deadList.append(entry)
                Mafia.aliveList.remove(entry)
        sm.current = 'Flip'

    def increase(self, instance):
        Mafia.dayCount += 1

    def router(self, instance):
        '''Determines which screen to display next'''
        #is the game over?
        while self.winCheck == False:
            #check for Vengeful kill
            if Mafia.setup == 'Vengeful' and instance.entry.faction == 'Town' and Mafia.dayCount == 1 :
                sm.add_widget(vengefulKill(name='vengefulKill'))
                sm.current = 'vengefulKill'
            #if Hito's 8p
            #check for night phase
            elif gameSetups.get(Mafia.setup). get('nightkill') == True:
                sm.add_widget(Night(name='Night %s' % Mafia.nightCount))
                sm.current = 'Night %s' % Mafia.nightCount
            #the rest are nightless
            else:
                sm.current = 'deadlineTimer'


    def winCheck(self, instance):
        '''Checks if any win conditions are met, returns boolean, updates Mafia.winningTeam'''
        #has mafia won?
        livingMafia = 0
        for entry in Mafia.aliveList:
            if entry.faction == 'Mafia':
                livingMafia +=1
        if len(Mafia.aliveList)/2 <= livingMafia:
            Mafia.winningTeam = 'Mafia'
            return True
        elif len(livingMafia) == 0:
            Mafia.winningTeam = 'Town'
            return True

        return False

class vengefulKill(Screen):
    '''A modified night action Screen'''

    def buildContent(self):
        for entry in Mafia.aliveList:
            button = Button(text=entry.name)
            button.bind(on_press=self.update)
            self.ids.vengefulGrid.add_widget(button)

    def update(self, instance):
        'instance.text == entry.name'
        self.ids.vengefulGrid.clear_widgets(children=self.ids.vengefulGrid.children)
        for entry in Mafia.aliveList:
            if instance.text == entry.name:
                dead = entry
                entry.status = 'dead'
                self.ids.vengefulLabel.text = '%(name)s, %(faction)s %(role)s is dead. RIP' % {'name' : entry.name, 'faction':entry.faction, 'role': entry.role}
                Mafia.deadList.append(entry)
                Mafia.aliveList.remove(entry)
        if dead.faction == 'Town':
            self.ids.vengefulLabel.text += ('\n The game is over')
            Mafia.winningTeam = 'Mafia'
            button = Button(text='Summary')
            button.bind(on_press=self.summary)
            print ('The game is over')
        elif dead.faction == 'Mafia':
            button = Button(text='Continue')
            button.bind(on_press=self.test)
            self.ids.vengefulBox.add_widget(button)

    def test(self, instance):
        sm.current = 'deadlineTimer'

    def summary(self, instance):
        sm.current = 'endGame'

class Night(Screen):

    def buildContent(self, instance):
        pass

class endGame(Screen):

    def reset(self, instance):
        pass
class Settings(Screen):

    #from kivy.uix.settings
    pass

Builder.load_file('screens.kv')

sm = ScreenManager()
sm.add_widget(titleScreen(name='titleScreen'))
sm.add_widget(setNumber(name='setNumber'))
sm.add_widget(setSetup(name='setSetup'))
sm.add_widget(setPlayers(name='setPlayers'))
sm.add_widget(roleDistribution(name='roleDistribution'))
sm.add_widget(deadlineTimer(name='deadlineTimer'))
sm.add_widget(Night(name='Night'))
sm.add_widget(endGame(name='endGame'))
sm.add_widget(Flip(name='Flip'))

class Mafia(App):

    dayCount = 1
    nightCount = 1
    #playerList = []
    aliveList = dummyList
    deadList = []
    #setup = StringProperty()
    setup = 'Vengeful'
    #playerNumber = NumericProperty()
    playerNumber = 5
    winningTeam = ''


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
        sm.current = 'titleScreen'
        return root

if __name__ == '__main__':
    Mafia().run()