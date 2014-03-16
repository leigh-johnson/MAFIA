from kivy.app import App
from kivy.clock import Clock
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
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

gameSetups = JsonStore('gameSetups.json')

class TimerButton(Button):

    def __init__(self, seconds, **kwargs):
        super(TimerButton, self).__init__(**kwargs)
        self.seconds = seconds
        self.text = 'Phase ends in %s seconds' %self.seconds

    def on_press(self):
        Clock.schedule_once(self.timeCall, 1)

    def timeCall(self, dt):
        if self.seconds > 0:
            self.seconds -= 1
            self.text = "Time left: %s seconds" % self.seconds
            Clock.schedule_once(self.timeCall, 1)
        elif Mafia.phase == 'day':
            sm.add_widget(Day(name='Day %s' % Mafia.dayCount))
            sm.current = 'Day %s' % Mafia.dayCount
        elif Mafia.phase == 'night':
            sm.add_widget(Night(name='Night %s' % Mafia.nightCount))
            sm.current = 'Night %s' % Mafia.nightCount

class multiLineLabel(Label):
    def __init__(self, **kw):
        super(multiLineLabel, self).__init__(**kw)
        self.bind(size=self.setter('text_size'))

class multiLineButton(Button):
    def __init__(self, **kw):
        super(multiLineButton, self).__init__(**kw)
        self.bind(size=self.setter('text_size'))

class IconButton(Button):
    '''subclass created for buttons with icon overlay'''
    icon = StringProperty()

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
        self.ids.setupAccordion.clear_widgets(children=self.ids.setupAccordion.children)
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
        self.ids.playerGrid.clear_widgets(children=self.ids.playerGrid.children)
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
        self.ids.roleGrid.clear_widgets(children=self.ids.roleGrid.children)
        for player in Mafia.aliveList:
            roleButton = Button(text=player.name)
            roleButton.name = player.name
            roleButton.bind(on_press=self.buildPopup)
            self.ids.roleGrid.add_widget(roleButton)


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
                for entry in Mafia.aliveList:
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
            size_hint=(.8, .8), auto_dismiss=False)
        rolePopup.name = instance.text
        #dismissButton = Button(text='Destroy this message')
        #dismissButton.bind(on_press=rolePopup.dismiss)
        button = Button(text='Destroy this message')
        content.add_widget(button)
        button.bind(on_press=rolePopup.dismiss)
        rolePopup.bind(on_dismiss=self.removeButton)
        rolePopup.open()

    def removeButton(self, instance):
        '''Removes a child of ids.roleGrid, playerName passed as instance.name'''
        '''Implemented to avoid awkward situations where user has access to already-viewed roles'''
        #instance of RolePopup()
        for child in self.ids.roleGrid.children:
            if child.name == instance.name:
                self.ids.roleGrid.remove_widget(child)
        #after all the roles are distributed, add a Start button
        if self.ids.roleGrid.children == []:
            sm.current = 'deadlineTimer'

class deadlineTimer(Screen):
    '''Counts down from settings.deadline'''
    def buildContent(self):
        self.ids.deadlineBox.clear_widgets(children=self.ids.deadlineBox.children)
        self.ids.deadlineBox.add_widget(Label(text=
        'With %(alive)s living, it takes %(threshold)s to lynch' % {'alive': len(Mafia.aliveList), 'threshold' : len(Mafia.aliveList)/2 +1}))
        self.ids.deadlineBox.add_widget(TimerButton(2))

class Flip(Screen):

    def buildContent(self):
        self.ids.flipBox.clear_widgets(children=self.ids.flipBox.children)
        entry = Mafia.deadList[-1]
        flipLabel= multiLineLabel(text='%(name)s is dead, he was a %(role)s aligned with the %(faction)s'
        % {'name' : entry.name, 'role' : entry.role, 'faction': entry.faction}, font_size=20,
        halign='center', valign='middle')

        button = multiLineButton(text='Continue', size=(1, .3), halign='center', valign='middle')
        button.bind(on_press=self.resolver)
        self.ids.flipBox.add_widget(flipLabel)

    def resolver(self):
        '''Routes to the next Screen depending on fulfilled wincons, setup variant'''
        #if game is still ongoing
        if self.winCheck() == True:
            if Mafia.setup == 'Vengeful' and len(Mafia.deadList) == 1:
                if Mafia.deadList[0].faction == 'Town' and len(Mafia.deadList) == 1:
                    sm.add_widget(vengefulKill(name='vengefulKill'))
                    sm.current = 'vengefulKill'
                else:
                    sm.current = 'deadlineTimer'
            elif gameSetups.get(Mafia.setup). get('nightkill') == True:
                if Mafia.phase == 'day':
                    sm.current = 'twilightTimer'
                    Mafia.phase = 'night'
                elif Mafia.phase == 'night':
                    sm.current = 'deadlineTimer'
                    Mafia.phase = 'day'
            else:
                sm.current = 'deadlineTimer'
        else:
            sm.current = 'endGame'

    def winCheck(self):
        ongoing = True
        if Mafia.setup == 'Vengeful' and len(Mafia.deadList) == 1:
            #lynching the Godfather ends the game
            if len(Mafia.deadList) == 1 and Mafia.deadList[0].role == 'Godfather':
                Mafia.winningTeam = 'Town'
                ongoing = False
        #living mafia outnumber or equal living town
        elif (len([entry for entry in Mafia.aliveList if entry.faction =='Mafia']) >= len([entry for entry in Mafia.aliveList if entry.faction == 'Town'])):
            Mafia.winningTeam = 'Mafia'
            ongoing = False
        #ll mafia are dead
        elif len([entry for entry in Mafia.aliveList if entry.faction =='Mafia']) == 0:
            Mafia.winningTeam = 'Town'
            ongoing = False
        return ongoing


class Day(Screen):

    def buildContent(self):
        self.ids.dayGrid.clear_widgets(children=self.ids.dayGrid.children)
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
        Mafia.dayCount = Mafia.dayCount + 1
        sm.current = 'Flip'

class Night(Screen):

    #tracks kill; if one member preforms option will not be available in future popups
    mafiaKill = False

    killTarget = StringProperty()
    protectTarget = StringProperty()
    investigateTarget = StringProperty('')

    def buildContent(self):
        self.ids.nightGrid.clear_widgets(children=self.ids.nightGrid.children)
        for entry in Mafia.aliveList:
            button = Button(text=entry.name)
            button.bind(on_press=self.buildPopup)
            self.ids.nightGrid.add_widget(button)

    def buildPopup(self, instance):
        '''Builds a popup instance.text = player.name'''
        content = BoxLayout(orientation='vertical')
        for entry in Mafia.aliveList:
            if entry.name == instance.text:
                player = entry
        popup = Popup(title=player.role, content = content,
            size_hint=(.8, .8), auto_dismiss=False)
        dismissButton = Button(size_hint=(1, .3), text='Take no action')
        if gameRoles.get(player.role).get('target') == True:
            actionGrid = GridLayout(cols=2, padding=5, spacing=5)
            content.add_widget(actionGrid)
            #adds feedback to button text
            if player.faction == 'Mafia':
                if self.mafiaKill == True:
                    label = Label(text='One of your partners has already preformed your team kill')
                    content.add_widget(label)
                else:
                    self.mafiaKill = True
                    label = Label(text='Preform the Mafia faction kill.', size_hint=(1, .2))
                    content.add_widget(label)
                    for entry in [i for i in Mafia.aliveList if i.faction == 'Town']:
                        button = ToggleButton(text=entry.name, group='Town')
                        button.action = 'kill'
                        button.bind(on_press=self.update)
                        actionGrid.add_widget(button)
                        dismissButton.text = ('Submit action: %(action)s %(target)s ' %
                        {'action': button.action, 'target': self.killTarget})
            elif player.role == 'Doctor':
                label = Label(text=gameRoles.get('Doctor').get('info'), size_hint=(1, .2))
                for entry in [i for i in Mafia.aliveList if i.name != player.name]:
                    button = Button(text=entry.name)
                    button.action = 'protect'
                    button.bind(on_press=self.update)
                    actionGrid.add_widget(button)
            elif player.role == 'Cop':
                label = Label(text=gameRoles.get('Cop').get('info'), size_hint=(1, .2))
                for entry in [i for i in Mafia.aliveList if i.name != player.name]:
                    button = Button(text=entry.name)
                    button.action = 'investigate'
                    button.bind(on_press=self.investigate)
                    button.bind(on_press=self.clearGrid)
                    actionGrid.add_widget(button)
        else:
            content.add_widget(Label(text='Hello %s' % player.name))
        popup.name = instance.text
        content.add_widget(dismissButton)
        dismissButton.bind(on_press=popup.dismiss)
        popup.bind(on_dismiss=self.removeButton)
        popup.open()

    def clearGrid(self, instance):
        '''Clears the actionGrid except for instance'''
        instance.unbind(on_press=self.investigate)
        instance.parent.clear_widgets(children=[i for i in instance.parent.children if i != instance])
    def toggleState(self, instance):
        instance.text = 'You did it!'
    def investigate(self, instance):
        '''Returns an investigation result
        for use in vanilla cop games, where investigation result is delivered immediately'''
        for entry in Mafia.aliveList:
            if instance.text == entry.name:
                player = entry
        if player.faction == 'Town':
            instance.text = 'Town'
        elif player.faction == 'Mafia':
            instance.text = 'Mafia'

    def update(self, instance):
        '''Updates Night class instance attributes for resolver logic'''
        print('%(action)s on %(player)s' % {'action': instance.action, 'player': instance.text})
        if instance.action == 'kill':
            self.killTarget = instance.text
        elif instance.action == 'protect':
            self.protectTarget = instance.text
        elif instance.action == 'investigate':
            self.investigateTarget = instance.text

    def removeButton(self, instance):
        '''Removes a child of ids.actionGrid, playerName passed as instance.text'''
        '''Implemented to avoid awkward situations where user has access to already-viewed roles'''
        #instance of RolePopup()
        for child in self.ids.nightGrid.children:
            if child.text == instance.name:
                self.ids.nightGrid.remove_widget(child)
        #after all the roles are distributed, add a Start button
        if self.ids.nightGrid.children == []:
            self.resolver()

    def resolver(self):
        '''Resolves night actions, updates Mafia.aliveList & deadList to reflect results
        proceeds to flip'''
        Mafia.nightCount = Mafia.nightCount+1
        if self.protectTarget == self.killTarget:
            print('no kill tonight')
            sm.current = 'protectScreen'
        else:
            print('Going to the flip screen')
            for target in Mafia.aliveList:
                if target.name == self.killTarget:
                    Mafia.deadList.append(target)
                    Mafia.aliveList.remove(target)
                    sm.current = 'Flip'

class protectScreen(Screen):
    pass
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
                Mafia.deadList.append(entry)
                Mafia.aliveList.remove(entry)
        sm.current = 'Flip'

class hitoKill(Screen):

    def buildContent(self):
        '''If town lynched Day 1, scum must kill one of their own
        If scum lynched Day 1, scum may kill 1 town member and become lovers
        Nightless'''
        if Mafia.deadList[0].faction == 'Town':
            for entry in Mafia.aliveList:
                if entry.faction == 'Mafia':
                    button = Button(text=entry.name)
                    button.bind(on_press=self.update)
                    self.ids.hitoGrid.add_widget(button)
        else:
            for entry in Mafia.aliveList:
                if entry.faction == 'Town':
                    button = Button(text=entry.name)
                    button.bind(on_press=self.update)
                    self.ids.hitoGrid.add_widget(button)
    def update(self, instance):
        pass

class endGame(Screen):

    def buildContent(self):
        self.ids.endGameLabel.text = '%s faction is victorious!' % Mafia.winningTeam

    def reset(self):
        Mafia.phase = 'day'
        Mafia.dayCount = 1
        Mafia.nightCount = 1
        Mafia.aliveList[:] = []
        Mafia.deadList[:] = []
        Mafia.setup = StringProperty()
        Mafia.playerNumber = NumericProperty(0)
        winningTeam = ''
        sm.current = 'titleScreen'

class twilightTimer(Screen):

    def buildContent(self):
        self.ids.twilightBox.clear_widgets(children=self.ids.twilightBox.children)
        #value provided by settings
        self.ids.twilightBox.add_widget(multiLineLabel(
            text='Heads down, Mafia look up. Everybody may wake up when the buzzer rings',
            halign = 'center', valign = 'middle'))
        self.ids.twilightBox.add_widget(TimerButton(2))

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
sm.add_widget(twilightTimer(name='twilightTimer'))
sm.add_widget(protectScreen(name='protectScreen'))

class Mafia(App):
    phase = 'day' #'day' or 'night'
    dayCount = 1
    nightCount = 1
    aliveList = []
    deadList = []
    setup = StringProperty()
    #setup = 'Vengeful'
    playerNumber = NumericProperty()
    #playerNumber = 5
    winningTeam = ''


    def build(self):
        root = NavigationDrawer()

        menu = BoxLayout(orientation='vertical')

        resetButton = Button(text='New Game', background_disabled_normal='/img/flat-reset.png')
        settingsButton = Button(text='Settings')
        helpButton = Button(text='Help')
        menu.add_widget(resetButton)
        menu.add_widget(settingsButton)
        menu.add_widget(helpButton)

        root.add_widget(menu)

        content = BoxLayout(orientation='vertical')

        toggleButton = IconButton (size_hint=(.1, .15), icon="atlas://img/iconatlas/icon-menu")
        toggleButton.bind(on_press=lambda j: root.toggle_state())


        content.add_widget(toggleButton)
        content.add_widget(sm)
        root.add_widget(content)
        sm.current = 'titleScreen'
        return root

if __name__ == '__main__':
    Mafia().run()