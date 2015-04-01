from random import*
import sys
import pygame
from pygame.locals import *
import pyganim
pygame.font.init()
pygame.init()
windowSurface = pygame.display.set_mode((700, 450), 0, 32)
font = pygame.font.Font(None, 30)

###################################CLASSES#####################################
class Character(object):
    def __init__(self, health, attack, defense, defMod, atkMod, speed, unDefSwitch, name, sprite):
        self.health = health
        self.attack = attack
        self.defense = defense
        self.defMod = defMod
        self.atkMod = atkMod
        self.speed = speed
        self.name = name
        self.unDefSwitch = unDefSwitch
        self.sprite = sprite
        self.attacked = False
        self.hpChange = False

    def attackThing(self, other):
        other.hpChange = True
        damage = (self.attack+self.atkMod) - other.defense
        if damage <= 0: damage = 0
        other.health -= damage
        if isinstance(self, Player):
            blitPlayerAttack(self, other)
        else:
            blitEnemyAttack(other, self)

    def defend(self):
        unDefSwitch = True #switch to remove defense mods after single turn defense is over
        self.defense += self.defMod
        print "%s is defending! %d added to defense stat. \n" % (self.name, self.defMod)

    def unDef(self):
        self.defense -= self.defMod
        #oops long
        print "%s has stopped defending. %s's defense has returned to %d. \n" % (self.name, self.name, self.defense)

    def  healthUp(self, impact):
        self.hpChange = True
        self.health += impact
        if impact >= 0: change = "increased"
        elif impact < 0: change = "decreased"
        print self.name,"'s health %s by %d! Health:" % (change, abs(impact)), self.health

    def atkUp(self, impact):
        self.attack += impact
        if impact >= 0: change = "increased"
        elif impact < 0: change = "decreased"
        if self.attack < 0: self.attack = 0
        print self.name, "'s attack %s by %d! Attack:" % (change, abs(impact)), self.attack 

    def defUp(self, impact):
        self.defense += impact
        if impact >= 0: change = "increased"
        elif impact < 0: change = "decreased"
        if self.defense < 0: self.defense = 0
        print self.name, "'s defense %s by %d! Defense:" % (change, abs(impact)), self.defense 

    def speedUp(self, impact):
        self.speed += impact
        if impact >= 0: change = "increased"
        elif impact < 0: change = "decreased"
        if self.speed < 0: self.speed = 0
        print self.name, "'s speed %s by %d! Speed:" % (change, abs(impact)), self.speed


class Player(Character):
    def __init__(self, health, attack, defense, defMod, atkMod, speed, unDefSwitch, gender, name, sprite):
        super(Player, self).__init__(health, attack, defense, defMod, atkMod, speed, unDefSwitch, name, sprite)
        self.name = name
        self.speed = speed

    def run(self, other):
        probability = randint(0, 10)
        if self.speed >= probability:
           print "You got away!\n"
           return True
        else:
            print "Well that didn't work.\n"
            return False
            
class Battle(object):
    def __init__(self, player, enemy, playerWin, enemyWin, isPlayerTurn, elements,
                 items, compounds, compoundSet):
        self.player = player
        self.enemy = enemy
        self.playerWin = False
        self.enemyWin = False
        self.isPlayerTurn = isPlayerTurn
        self.elements = elements
        self.items = items
        self.compounds = compounds
        self.compoundSet = compoundSet
        
    def enemyGen(self): #for when player info is already known (I literally just copy pasted this)
        randEnemy = randint(0, len(ENEMY_LIST)-1)
        self.enemy = ENEMY_LIST[randEnemy]
        
    def playerTurn(self, player, enemy):
        self.player.attacked = False
        self.player.hpChange = False
        self.player.unDefSwitch = False
        turn = blitTurnSelect(player, enemy)
        if turn == "attack":
            self.player.attackThing(self.enemy)
            self.attacked = True
        elif turn == "defend":
            self.player.unDefSwitch = True
            self.player.defend()
        elif turn == "run":
            if self.player.run(self.enemy) == True:
                self.playerWin == True
                windowSurface.blit(got_away, (0, 0))
                pygame.display.flip()
                self.playAgain()
        elif turn == "inventory":
            itemSet = blitInventorySelect(player, enemy)
            self.accessInventory(itemSet, self.compounds, self.compoundSet)
        else:
            print "Sorry, I couldn't understand that.\n"
            self.playerTurn(player, enemy)
        #and then actually remove mods
        if self.enemy.unDefSwitch == True:
            self.enemy.unDef()
        self.isPlayerTurn = False

    def enemyTurn(self, player, enemy):
        self.enemy.attacked = False
        self.enemy.hpChange = False
        self.enemy.unDefSwitch = False
        possibleTurns = ["attack", "defend"] 
        randTurn = randint(0, len(possibleTurns)-1)
        turn = possibleTurns[randTurn]
        if turn == "attack":
            self.enemy.attackThing(self.player)
        elif turn == "defend":
            self.enemy.unDefSwitch = True
            self.enemy.defend()
        if self.player.unDefSwitch == True:
            self.player.unDef()
        self.isPlayerTurn = True

    def statCheck(self, player, enemy):
        if self.enemy.health <= 0:
            self.playerWin = True
            print "You won!"
            windowSurface.blit(you_won, (0,0))
            pygame.display.flip()
            self.playAgain()
        elif self.player.health <= 0:
            self.enemyWin = True
            print "You lost..."
            windowSurface.blit(you_lose, (0,0))
            pygame.display.flip()
            self.playAgain()
        print self.player.name, ":", self.player.health, "\n", self.enemy.name, ":", self.enemy.health, "\n"

    def accessInventory(self, inventory, compounds, compoundSet):
        item = blitInventory(self, inventory)
        if item in self.items.inventory or item in self.compounds.inventory:
            if item != None: itemChoice = item.dispName
            else: itemChoice = None
            names = inventory.getNames()
            if (itemChoice in names):
                itemChoice = inventory.inventory[names.index(itemChoice)]
                toDo= eval(str(itemChoice) +".doTheThing()")
                eval(toDo)
                eval(str(inventory)+".removeItem(" +str(itemChoice) +")")
        else:
            self.combineElements(inventory, compounds, compoundSet, item)

    def combineElements(self, inventory, compounds, compoundSet, item):
        components = [item]
        choice = blitInventory(self, self.elements)
        while choice != None and choice.dispName != "done":
            components.append(choice)
            choice = blitInventory(self, self.elements)
            for compound in compoundSet:
                if compound.components == components:
                    compounds.addItem(compound)
                    print compound.dispName, "added to compound inventory!"
                    break
        
    def playAgain(self):
        if self.enemyWin == True:
            self.player.health +=25
        elif self.playerWin == True:
            self.enemy.health +=25
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        blitClean(self)
                        self.enemyGen()
                        self.enemyWin = False
                        self.playerWin = False
                        inBattle(self)
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            
#this is really just for storing data
class Element(object):
    def __init__(self, dispName, atomicNum, kind, index, trueName, sprite):
        self.dispName = dispName
        self.atomicNum = atomicNum # "complexity"
        self.kind = kind #denoted as "type" in -game
        # replace properties with descrip
        #self.properties = properties
        self.index = index
        self.trueName = trueName
        self.sprite = sprite

class StatModItem(object):
    def __init__(self, dispName, function, recipient, impact, index, trueName, sprite):
        self.dispName = dispName 
        self.function = function
        self.recipient = recipient # this and name are already strings also index I think
        self.impact = str(impact)
        self.index = index
        self.trueName = trueName
        self.sprite = sprite

    def doTheThing(self):
        #i.e. todo = self.enemy.attackUp(2), where enemy is self.recipient, attackUp is self. function,
        #and 2 is self.impact, and then it gets eval'd
        toDo = ("self." + self.recipient + "." +  self.function + "("+ self.impact + ")")
        return toDo

    def __str__(self):
        return self.trueName

class Compound(StatModItem):
    def __init__(self, dispName, function, recipient, impact, index, trueName, components, sprite):
        super(Compound, self).__init__(dispName, function, recipient, impact, index, trueName, sprite)
        self.components = components
        
class Inventory(object):
    def __init__(self, dispName, itemCount, trueName, sprite):
        self.dispName = dispName
        self.inventory = [None for val in xrange(itemCount)]
        self.trueName = trueName
        self.sprite = sprite
        
    def addItem(self, item):
        if item != None:
            self.inventory[item.index] = item

    def removeItem(self, item):
        self.inventory[item.index] = None

    def displayInventory(self):
        for item in self.inventory:
            if item != None:
                print item.dispName, ":", self.inventory.index(item)

    def getNames(self):
        names = []
        for item in self.inventory:
            if item != None:
                names.append(item.dispName)
            else:
                names.append("None")
        return names

    def getSprites(self):
        sprites = []
        for item in self.inventory:
            if item !=None:
                sprites.append(item.sprite)
            else:
                sprites.append("None")
        return sprites

    def __str__(self):
        return self.trueName

############################GAME SPECIFIC GLOBALS###########################
##################################helpity#########################################
helpingHand ="""This is the battle system for a chemistry based rpg:
You have been presented with a randomized enemy, and you
make choose to attack, defend, check your inventory or run. 

If you defend, your defense stats will increase for the duration
of one enemy turn. The same goes for your enemy. 

If you attack, you will use your trusty flamethrower to blast
your enemy.

If you check your inventory, you may find you have some useful
things (I've made sure to stock it fully) among your items.

If you check your elements inventory, you will see it is also fully stocked, 
and ready to be utilized. If you select the elements you wish to combine
and then select the "done" slot, if the elements you selected successfully
created a new compound, it will be added to your compound inventory and you
will be notified. 

Once you have added new items to you compound inventory, they may be used
for stat effects (Attack ++, Defense ++, etcetera) in the same fashion as items, 
but in that same vein, they are single-use. (Of course, your elements have
unlimited uses).

Press "backspace" or "escape" to exit your inventory-- remember that entering
your inventories uses up your turn, so be careful.

Good Luck!"""
#---------------------------------------------------------------IMAGES-------------------------------------------------------------------------------#

r_fthrow_stationary = pygame.image.load("r_fthrower_0.png")
r_fthrow0 = pygame.image.load("r_fthrower_0.png")
r_fthrow1 = pygame.image.load("r_fthrower_1.png") 
r_fthrow2 = pygame.image.load("r_fthrower_2.png") 

dragon_0 = pygame.image.load("dragon_0.png")
dragon_1 = pygame.image.load("dragon_1.png")
dragon_2 = pygame.image.load("dragon_2.png")

eagle_0 = pygame.image.load("eagle_0.png")
eagle_1 = pygame.image.load("eagle_1.png")
eagle_2 = pygame.image.load("eagle_2.png")

slime_0 = pygame.image.load("slime_0.png")
slime_2 = pygame.image.load("slime_2.png")

unicorn_0 = pygame.image.load("unicorn_0.png")
unicorn_1 = pygame.image.load("unicorn_1.png")
unicorn_2 = pygame.image.load("unicorn_2.png")
unicorn_3 = pygame.image.load("unicorn_3.png")
unicorn_4 = pygame.image.load("unicorn_4.png")
unicorn_5 = pygame.image.load("unicorn_5.png")
unicorn_6 = pygame.image.load("unicorn_6.png")
unicorn_7 = pygame.image.load("unicorn_7.png")
unicorn_8 = pygame.image.load("unicorn_8.png")
unicorn_9 = pygame.image.load("unicorn_9.png")
unicorn_10 = pygame.image.load("unicorn_10.png")
unicorn_11 = pygame.image.load("unicorn_11.png")
unicorn_12 = pygame.image.load("unicorn_12.png")

fireball_stationary = pygame.image.load("fireball_stationary.png")
fireball_0 = pygame.image.load("fireball_0.png")
fireball_1 = pygame.image.load("fireball_1.png")
fireball_2 = pygame.image.load("fireball_2.png")
fireball_3 = pygame.image.load("fireball_3.png")
fireball_4 = pygame.image.load("fireball_4.png")
fireball_5 = pygame.image.load("fireball_5.png")
fireball_6 = pygame.image.load("fireball_6.png")
fireball_7 = pygame.image.load("fireball_7.png")
fireball_8 = pygame.image.load("fireball_8.png")
fireball_9 = pygame.image.load("fireball_9.png")

enemy_fire_stationary = pygame.image.load("enemy_fire_stationary.png")
enemy_fire_0 = pygame.image.load("enemy_fire_0.png")
enemy_fire_1 = pygame.image.load("enemy_fire_1.png")
enemy_fire_2 = pygame.image.load("enemy_fire_2.png")
enemy_fire_3 = pygame.image.load("enemy_fire_3.png")
enemy_fire_4 = pygame.image.load("enemy_fire_4.png")
enemy_fire_5 = pygame.image.load("enemy_fire_5.png")
enemy_fire_6 = pygame.image.load("enemy_fire_6.png")
enemy_fire_7 = pygame.image.load("enemy_fire_7.png")
enemy_fire_8 = pygame.image.load("enemy_fire_8.png")
enemy_fire_9 = pygame.image.load("enemy_fire_9.png")

atk_up_lo = pygame.image.load("atk_up_lo.png")
atk_up_mid = pygame.image.load("atk_up_mid.png")
atk_up_hi = pygame.image.load("atk_up_hi.png")
def_up_lo = pygame.image.load("def_up_lo.png")
def_up_mid = pygame.image.load("def_up_mid.png")
def_up_hi = pygame.image.load("def_up_hi.png")
hp_up_lo = pygame.image.load("hp_up_lo.png")
hp_up_mid = pygame.image.load("hp_up_mid.png")
hp_up_hi = pygame.image.load("hp_up_hi.png")
spd_up_lo = pygame.image.load("spd_up_lo.png")
spd_up_mid = pygame.image.load("spd_up_mid.png")
spd_up_hi = pygame.image.load("spd_up_hi.png")
atk_kill_lo = pygame.image.load("atk_kill_lo.png")
atk_kill_mid = pygame.image.load("atk_kill_mid.png")
atk_kill_hi = pygame.image.load("atk_kill_hi.png")
def_kill_lo = pygame.image.load("def_kill_lo.png")
def_kill_mid = pygame.image.load("def_kill_mid.png")
def_kill_hi = pygame.image.load("def_kill_hi.png")
hp_kill_lo = pygame.image.load("hp_kill_lo.png")
hp_kill_mid = pygame.image.load("hp_kill_mid.png")
hp_kill_hi = pygame.image.load("hp_kill_hi.png")
spd_kill_lo = pygame.image.load("spd_kill_lo.png")
spd_kill_mid = pygame.image.load("spd_kill_mid.png")
spd_kill_hi = pygame.image.load("spd_kill_hi.png")

none = pygame.image.load("none_display.png")
done = pygame.image.load("done.png")

inventory_items = pygame.image.load("inventory_items.png")
inventory_elements = pygame.image.load("inventory_items.png")
inventory_compounds = pygame.image.load("inventory_items.png")
item_selector = pygame.image.load("item_selector.png")

inventory_choice = pygame.image.load("inventory_choice.png")

turn_choice = pygame.image.load("turn_choice.png")
turn_indicator = pygame.image.load("turn_indicator.png")

h = pygame.image.load("hydrogen.png")
li = pygame.image.load("lithium.png")
na = pygame.image.load("sodium.png")
k = pygame.image.load("potassium.png")
rb = pygame.image.load("rubidium.png")
be = pygame.image.load("beryllium.png")
mg = pygame.image.load("magnesium.png")
ca = pygame.image.load("calcium.png")
sr = pygame.image.load("strontium.png")
b = pygame.image.load("boron.png")
al = pygame.image.load("aluminum.png")
c = pygame.image.load("carbon.png")
si = pygame.image.load("silicon.png")
n = pygame.image.load("nitrogen.png")
p = pygame.image.load("phosphorus.png")
o = pygame.image.load("oxygen.png")
s = pygame.image.load("sulfur.png")
f = pygame.image.load("fluorine.png")
cl = pygame.image.load("chlorine.png")
br = pygame.image.load("bromine.png")


h2o2 = pygame.image.load("h2o2.png")
h4n2o3 = pygame.image.load("h4n2o3.png")
c3h8 = pygame.image.load("c3h8.png")
c4h10 = pygame.image.load("c4h10.png")

forest_bg = pygame.image.load("forest_bg.png")
you_lose = pygame.image.load("you_lose.png")
you_won = pygame.image.load("you_won.png")
start_screen = pygame.image.load("start_screen.png")
help_screen = pygame.image.load("help_screen.png")
got_away = pygame.image.load("got_away.png")

# create the PygAnimation objects
r_fthrower= pyganim.PygAnimation([(r_fthrow0, 0.1), (r_fthrow1, 0.1), (r_fthrow2, 0.8)],
                                 loop=False) 
r_fthrower_stationary = pyganim.PygAnimation([(r_fthrow_stationary, 0.1)])
eagle = pyganim.PygAnimation([(eagle_0, 0.2), (eagle_1, 0.2), (eagle_2, 0.2)])
dragon = pyganim.PygAnimation([(dragon_0, 0.2), (dragon_1, 0.2), (dragon_2, 0.2)])
slime = pyganim.PygAnimation([(slime_0, 0.4), (slime_2, 0.4)])
unicorn = pyganim.PygAnimation([(unicorn_0, 0.2), (unicorn_1, 0.2), (unicorn_2, 0.2), (unicorn_3, 0.2),
                                                        (unicorn_4, 0.2), (unicorn_5, 0.2), (unicorn_6, 0.2), (unicorn_6, 0.2),
                                                        (unicorn_7, 0.2), (unicorn_8, 0.2), (unicorn_9, 0.2), (unicorn_10, 0.2),
                                                        (unicorn_11, 0.2), (unicorn_12, 0.2)])
fireball = pyganim.PygAnimation([(fireball_0, 0.1), (fireball_1, 0.1), (fireball_2, 0.1), (fireball_3, 0.1),
                                                       (fireball_4, 0.1), (fireball_5, 0.1), (fireball_6, 0.1), (fireball_7, 0.1),
                                                       (fireball_8, 0.1), (fireball_9, 0.1)], loop = False)
enemy_fire = pyganim.PygAnimation([(enemy_fire_0, 0.1), (enemy_fire_1, 0.1), (enemy_fire_2, 0.1), (enemy_fire_3, 0.1),
                                                       (enemy_fire_4, 0.1), (enemy_fire_5, 0.1), (enemy_fire_6, 0.1), (enemy_fire_7, 0.1),
                                                       (enemy_fire_8, 0.1), (enemy_fire_9, 0.1)], loop = False)

#---------------------------------------------------------PLAYER STAT MODS------------------------------------------------------------#
#so these all effect the player and not the enemy
#ref: (dispName, function, recipient, impact, index, trueName)
HP_UP_LO = StatModItem("Cheap Potion", "healthUp", "player", 2, 0, "HP_UP_LO", hp_up_lo)
HP_UP_MID = StatModItem("Basic Potion", "healthUp", "player", 5, 1, "HP_UP_MID", hp_up_mid)
HP_UP_HI = StatModItem("Expensive Potion", "healthUp", "player", 8, 2, "HP_UP_HI", hp_up_hi)

ATK_UP_LO = StatModItem("steroids?", "atkUp", "player", 2, 3, "ATK_UP_LO", atk_up_lo)
ATK_UP_MID = StatModItem("Steroids.", "atkUp", "player", 5, 4, "ATK_UP_MID", atk_up_mid)
ATK_UP_HI = StatModItem("sTErOiDs", "atkUp", "player", 8, 5, "ATK_UP_HI", atk_up_hi)#I am feeling

DEF_UP_LO = StatModItem("Ice Pack", "defUp", "player", 2, 6, "DEF_UP_LO", def_up_lo)
DEF_UP_MID = StatModItem("Tylenol", "defUp", "player", 5, 7, "DEF_UP_MID", def_up_mid)
DEF_UP_HI = StatModItem("so many drugs", "defUp", "player", 8, 8, "DEF_UP_HI", def_up_hi) # a little

SPD_UP_LO = StatModItem("Cola", "speedUp", "player", 2, 9, "SPD_UP_LO", spd_up_lo)
SPD_UP_MID = StatModItem("Red Bull", "speedUp", "player", 5, 10, "SPD_UP_MID", spd_up_mid)
SPD_UP_HI = StatModItem("Gotta go fast", "speedUp", "player", 8, 11, "SPD_UP_HI", spd_up_hi)#destructively

#---------------------------------------------------------ENEMY STAT MODS--------------------------------------------------------------#
HP_KILL_LO = StatModItem("Fake Poison", "healthUp", "enemy", -2, 12, "HP_KILL_LO", hp_kill_lo)
HP_KILL_MID = StatModItem("Home-made Poison", "healthUp", "enemy", -5, 13, "HP_KILL_MID", hp_kill_mid)
HP_KILL_HI = StatModItem("Stolen Poison", "healthUp", "enemy", -8, 14, "HP_KILL_LO", hp_kill_hi)

ATK_KILL_LO = StatModItem("MAGIC DUST", "atkUp", "enemy", -2, 15, "ATK_KILL_LO", atk_kill_lo)
ATK_KILL_MID = StatModItem("Fairy Dust", "atkUp", "enemy", -5, 16, "ATK_KILL_MID", atk_kill_mid)
ATK_KILL_HI = StatModItem("Unicorn Dust", "atkUp", "enemy", -8, 17, "ATK_KILL_HI", atk_kill_hi)#creative

DEF_KILL_LO = StatModItem("sad internet pictures", "defUp", "enemy", -2, 18, "DEF_KILL_LO", def_kill_lo)
DEF_KILL_MID = StatModItem("nostalgia", "defUp", "enemy", -5, 19, "DEF_KILL_MID", def_kill_mid)
DEF_KILL_HI = StatModItem("cute animals", "defUp", "enemy", -8, 20, "DEF_KILL_HI", def_kill_hi)#sorry

SPD_KILL_LO = StatModItem("slow", "speedUp", "enemy", -2, 21, "SPD_KILL_LO", spd_kill_lo)
SPD_KILL_MID = StatModItem("SLOW", "speedUp", "enemy", -5, 22, "SPD_KILL_MID", spd_kill_mid)
SPD_KILL_HI = StatModItem("really SLOW", "speedUp", "enemy", -8, 23, "SPD_KILL_MID", spd_kill_hi)#not sorry

START_ITEMS = [HP_UP_LO, HP_UP_MID, HP_UP_HI, ATK_UP_LO, ATK_UP_MID, ATK_UP_HI,
                               DEF_UP_LO,  DEF_UP_MID, DEF_UP_HI, SPD_UP_LO, SPD_UP_MID, SPD_UP_HI,
                               HP_KILL_LO, HP_KILL_MID, HP_KILL_HI, ATK_KILL_LO, ATK_KILL_MID,
                                ATK_KILL_HI, DEF_KILL_LO, DEF_KILL_MID, DEF_KILL_HI, SPD_KILL_LO,
                               SPD_KILL_MID, SPD_KILL_HI]

#---------------------------------------------------------------ELEMENTS-------------------------------------------------------------------------#
#ref  (dispName, atomicNum, kind, index, trueName)
HYDROGEN = Element("Hydrogen", 1, "Powerful", 0, "HYDROGEN", h)
LITHIUM = Element("Lithium", 2, "Powerful", 1, "LITHIUM", li)
SODIUM = Element("Sodium", 9, "Powerful", 2, "SODIUM", na)
POTASSIUM = Element("Potassium", 16, "Powerful", 3, "POTASSIUM", k)
RUBIDIUM = Element("Rubidium", 19, "Powerful", 4,  "RUBIDIUM", rb)
BERYLLIUM = Element("Beryllium", 3, "Relaxed", 5, "BERYLLIUM", be)
MAGNESIUM = Element ("Magnesium", 10, "Relaxed", 6, "MAGNESIUM", mg)
CALCIUM = Element("Calcium", 17, "Relaxed", 7, "CALCIUM", ca)
STRONTIUM = Element("Strontium", 20, "Relaxed", 8, "STRONTIUM", sr)
BORON = Element("Boron", 4, "Basic", 9, "BORON", b)
ALUMINUM = Element("Aluminum", 11, "Basic", 10, "ALUMINUM", al)
CARBON = Element("Carbon", 5, "Basic", 11, "CARBON", c)
SILICON = Element("Silicon", 12, "Basic", 12, "SILICON", si)
NITROGEN = Element("Nitrogen", 6, "Basic", 13, "NITROGEN", n)
PHOSPHORUS = Element("Phosphorus", 13, "Basic", 14, "PHOSPHORUS", p)
OXYGEN = Element("Oxygen", 7, "Basic", 15, "OXYGEN", o)
SULFUR = Element("Sulfur", 14, "Basic", 16, "SULFUR", s)
FLUORINE = Element("Fluorine", 8, "Toxic", 17, "FLUORINE", f)
CHLORINE = Element("Chlorine", 15, "Toxic", 18, "CHLORINE", cl)
BROMINE = Element("Bromine", 18, "Toxic", 19, "BROMINE", br)
DONE = Element("Done", 19, "None", 20, "DONE", done)

ALL_ELEMENTS = [HYDROGEN, LITHIUM, SODIUM, POTASSIUM, RUBIDIUM,
                                    BERYLLIUM, MAGNESIUM, CALCIUM, STRONTIUM, BORON,
                                    ALUMINUM, CARBON, SILICON, NITROGEN, PHOSPHORUS,
                                    OXYGEN, SULFUR, FLUORINE, CHLORINE, BROMINE, DONE]

START_ELEMENTS = ALL_ELEMENTS

#---------------------------------------------------------------COMPOUNDS--------------------------------------------------------------------#
#ref: (dispName, function, recipient, impact, index, trueName, components)
HYDROGEN_PEROXIDE = Compound("H2O2", "healthUp", "enemy", -5, 0,
                                                                     "HYDROGEN_PEROXIDE",
                                                                     [HYDROGEN, HYDROGEN, OXYGEN, OXYGEN], h2o2)
AMMONIUM_NITRATE = Compound("H4N2O3", "healthUp", "enemy", -10,  1,
                                                                    "AMMONIUM_NITRATE", [HYDROGEN,
                                                                    HYDROGEN, HYDROGEN, 
                                                                    HYDROGEN, HYDROGEN, 
                                                                    NITROGEN, NITROGEN, OXYGEN,
                                                                                    OXYGEN, OXYGEN], h4n2o3)
BUTANE = Compound("C4H10", "healthUp", "enemy", -7,  2, "BUTANE", [CARBON, CARBON,
                                                                   CARBON, CARBON, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN], c4h10)
                                                                    #oh my god there must be a better way
PROPANE = Compound("C3H8", "healthUp", "enemy", -6, 3, "PROPANE", [CARBON, CARBON,
                                                                   CARBON, HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN], c3h8)

COMPOUND_SET = [HYDROGEN_PEROXIDE, AMMONIUM_NITRATE, BUTANE,
                                      PROPANE]
START_COMPOUNDS = []

#----------------------------------------------------------------------ENEMIES----------------------------------------------------------------------#
#Character(health, attack, defense, defMod, atkMod, speed, name)
SLIME = Character(10, 2, 2, 0, 0, 2, False, "Slime", slime)
EAGLE = Character(15, 4, 3, 1, 0, 4, False, "Eagle", eagle)
DRAGON = Character(20, 6, 5, 2, 2, 5, False, "Dragon", dragon)
UNICORN = Character(25, 8, 6, 3, 3, 8, False, "Mystical Sparkling Unicorn of the Forest", unicorn)

ENEMY_LIST = [EAGLE, DRAGON, SLIME, UNICORN]

USED = []

#------------------------------------------------------------INVENTORIES----------------------------------------------------------------------#

ELEMENTS = Inventory("Elements", 24, "ELEMENTS", inventory_elements)
STAT_MODIFIERS = Inventory("Items", 24, "STAT_MODIFIERS", inventory_items)
COMPOUNDS = Inventory("Compounds", 24, "COMPOUNDS", inventory_compounds)

###############################GAMEY GAME THINGS###########################
#for ref: blah = Battle(player, enemy, playerWin=False, enemyWin=False, playerTurn=True)
#also ref: blah = Player(health, attack, defense, defMod, atkMod, speed, unDefSwitch, gender, name)
#grab data necessary to facilitate battle
testPlayer = Player(20, 5, 5, 0, 0, 4, False, "girl", "You", r_fthrower)
testBattle = Battle(testPlayer, EAGLE, False, False, True, ELEMENTS, STAT_MODIFIERS,
                    COMPOUNDS, COMPOUND_SET)

def getInventories():
    elements = ELEMENTS
    items = STAT_MODIFIERS
    compoundSet = COMPOUND_SET
    compounds = COMPOUNDS
    gameStartInventoryStock(items)
    gameStartInventoryStock(elements)
    gameStartInventoryStock(compounds)
    

def getPlayer():
    player = Player(25, 3, 3, 0, 0, 4,False, "boy", "Avo", r_fthrower)
    return player

def getEnemy():
    randEnemy = randint(0, len(ENEMY_LIST)-1)
    while ENEMY_LIST[randEnemy] in USED:
        randEnemy = randint(0, len(ENEMY_LIST)-1)
    enemy = ENEMY_LIST[randEnemy]
    USED.append(enemy)
    if len(USED) == len(ENEMY_LIST):
        print "You beat all of them! Good job, you."
    return enemy

def dataGen():
    player = getPlayer()
    enemy = getEnemy()
    getInventories()
    return (player, enemy)
    
def gameStartInventoryStock(inventory):
    if inventory.dispName == "Items":
        for item in START_ITEMS:
            inventory.addItem(item)
    elif inventory.dispName == "Elements":
        for item in START_ELEMENTS:
            inventory.addItem(item)
    elif inventory.dispName == "Compounds":
        for item in START_COMPOUNDS:
            inventory.addItem(item)
    
def startBattle():
    USED = []
    (player, enemy) = dataGen()
    battle = Battle(player, enemy, False, False, True, ELEMENTS, STAT_MODIFIERS,
                    COMPOUNDS, COMPOUND_SET)
    player = battle.player
    enemy = battle.enemy
    if player.speed >= enemy.speed: battle.isPlayerTurn = True
    else: battle.isPlayerTurn = False
    inBattle(battle)
    

def inBattle(battle):
    while True:
        blitClean(battle)
        pygame.display.flip()
        print "A %s appeared!\n" % battle.enemy.name
        while battle.playerWin == False and battle.enemyWin == False:
            if battle.isPlayerTurn == True:
                battle.playerTurn(battle.player, battle.enemy)
                battle.statCheck(battle.player, battle.enemy)
            elif battle.isPlayerTurn == False: battle.enemyTurn(battle.enemy, battle.player)
            battle.statCheck(battle.player, battle.enemy)
            if battle.isPlayerTurn == True: battle.playerTurn(battle.player, battle.enemy)
            else: battle.enemyTurn(battle.enemy, battle.player)
        break

def blitClean(battle):
    windowSurface.blit(forest_bg, (0, 0))
    r_fthrower_stationary.blit(windowSurface, (520, 270))
    r_fthrower_stationary.play()
    battle.enemy.sprite.blit(windowSurface, (120, 250))
    battle.enemy.sprite.play()

# oh god look at this monstrous thing
def blitInventory(battle, inventory):
    startX = 38
    startY = 33
    selectorX = startX+93
    selectorY= startY+45
    chosenItemIndex = 0
    while True: # main loop
        windowSurface.blit(forest_bg, (0, 0))
        windowSurface.blit(inventory.sprite, (100, 50))
        windowSurface.blit(item_selector, (selectorX, selectorY))
        i = 1
        xDist = 74
        yDist = 89
        x = startX
        y = startY
        for event in pygame.event.get():
            rightBound = 550
            leftBound = 60
            topBound = 25
            bottomBound = 385
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    selectorX += xDist
                    chosenItemIndex +=1
                    if selectorX > rightBound:
                        selectorX = startX +93
                        selectorY += yDist
                        if selectorY > bottomBound:
                            selectorX = (startX + 93)
                            selectorY -=yDist
                            chosenItemIndex -=6
                elif event.key == K_LEFT:
                    selectorX -= xDist
                    chosenItemIndex -= 1
                    if selectorX < leftBound:
                        selectorX = (startX+93)+ (xDist*5)
                        selectorY -= yDist
                        if selectorY < topBound:
                            selectorX = (startX+93) +(xDist*5)
                            selectorY += yDist
                            chosenItemIndex += 6
                elif event.key == K_UP:
                    selectorY -= yDist
                    chosenItemIndex -=6
                    if selectorY < topBound:
                        selectorY = (startY + 45) + (yDist*3)
                        chosenItemIndex += 24
                elif event.key == K_DOWN :
                    selectorY += yDist
                    chosenItemIndex +=6
                    if selectorY > bottomBound:
                        selectorY = startY + 45
                        chosenItemIndex -=24
                elif event.key == K_z:
                    chosenItem = inventory.inventory[chosenItemIndex]
                    if chosenItem != None:
                        print chosenItem.dispName
                        blitClean(battle)
                        return chosenItem
                        break
                elif event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    return None
        for item in inventory.inventory:
            if item == None:
                index = inventory.inventory.index(item)
                inventory.sprite.blit(none, (x, y))
            else:
                index = inventory.inventory.index(item)
                inventory.sprite.blit(item.sprite, (x, y))
            x += xDist
            if i % 6 == 0:
                y+= yDist
                x = startX
            i += 1
        pygame.display.flip()

def blitTurnSelect(player, enemy):
    possibleTurns = ["attack", "defend", "inventory", "run"]
    turnsIndex = 0
    startX = 622
    startY = 387
    indicatorX = startX-10
    indicatorY = startY
    yDist = 13
    while True:
        windowSurface.blit(forest_bg, (0,0))
        forest_bg.blit(turn_choice, (600, 380))
        forest_bg.blit(turn_indicator, (indicatorX, indicatorY))
        enemy.sprite.blit(windowSurface, (120, 250))
        r_fthrower_stationary.blit(windowSurface, (520, 270))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_DOWN and indicatorY < startY + (3*yDist):
                    indicatorY += yDist
                    turnsIndex +=1
                elif event.key == K_UP and indicatorY > startY:
                    indicatorY -= yDist
                    turnsIndex -=1
                elif event.key == K_z:
                    turnChoice = possibleTurns[turnsIndex]
                    return turnChoice
                elif event.key == K_h:
                    print helpingHand
        pygame.display.flip()

def blitInventorySelect(player, enemy):
    possibleInventories = [STAT_MODIFIERS, ELEMENTS, COMPOUNDS]
    inventoriesIndex = 0
    startX = 622
    startY = 387
    indicatorX = startX-10
    indicatorY = startY
    yDist = 15
    while True:
        windowSurface.blit(forest_bg, (0,0))
        forest_bg.blit(inventory_choice, (600, 380))
        forest_bg.blit(turn_indicator, (indicatorX, indicatorY))
        enemy.sprite.blit(windowSurface, (120, 250))
        r_fthrower_stationary.blit(windowSurface, (520, 270))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_DOWN and indicatorY < startY + (2*yDist):
                    indicatorY += yDist
                    inventoriesIndex +=1
                elif event.key == K_UP and indicatorY > startY:
                    indicatorY -= yDist
                    inventoriesIndex -=1
                elif event.key == K_z:
                    inventoryChoice = possibleInventories[inventoriesIndex]
                    return inventoryChoice
                elif event.key == K_h:
                    print helpingHand
        pygame.display.flip()

def blitPlayerAttack(player, enemy):
    once = True
    i = 0
    while True:
        windowSurface.blit(forest_bg, (0, 0))
        r_fthrower.blit(windowSurface, (520, 270))
        r_fthrower.play()
        enemy.sprite.blit(windowSurface, (120, 250))
        enemy.sprite.play()
        fireball.blit(windowSurface, (130, 285))
        forest_bg.blit(fireball_stationary, (120, 270))
        if once == True:
            r_fthrower.play()
            fireball.play()
            once = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        i += 1
        if i == 60:
            break
    

#this is literally the same except with the enemy attack sprite sorry not sorry
def blitEnemyAttack(player, enemy):
    once = True
    i = 0
    while True:
        windowSurface.blit(forest_bg, (0, 0))
        r_fthrower.blit(windowSurface, (520, 270))
        r_fthrower.play()
        enemy.sprite.blit(windowSurface, (120, 250))
        enemy.sprite.play()
        enemy_fire.blit(windowSurface, (150, 285))
        forest_bg.blit(enemy_fire_stationary, (120, 270))
        if once == True:
            r_fthrower.play()
            enemy_fire.play()
            once = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        i += 1
        if i == 60:
            break

def start():
    windowSurface.blit(start_screen, (0,0))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_z:
                    windowSurface.blit(help_screen, (0,0))
                if event.key == K_RETURN:
                    startBattle()
            pygame.display.flip()


        
##########################testy###################################################       
#gameStartInventoryStock(STAT_MODIFIERS)
#blitInventory(testBattle, STAT_MODIFIERS)
#blitTurnSelect(testBattle)
#blitPlayerAttack(testBattle)
#blitEnemyAttack(testBattle)
#startBattle()
start()
