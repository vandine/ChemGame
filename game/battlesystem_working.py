from random import*

###################################CLASSES#####################################
class Character(object):
    #next to be added: sprite
    def __init__(self, health, attack, defense, defMod, atkMod, speed, unDefSwitch, name):
        self.health = health
        self.attack = attack
        self.defense = defense
        self.defMod = defMod
        self.atkMod = atkMod
        self.speed = speed
        self.name = name
        self.unDefSwitch = unDefSwitch

    def attackThing(self, other):
        damage = (self.attack+self.atkMod) - other.defense
        if damage < 0: damage = 0
        other.health -= damage
        print "%s did %d damage to %s! \n" % (self.name, damage, other.name)

    def defend(self):
        unDefSwitch = True #switch to remove defense mods after single turn defense is over
        self.defense += self.defMod
        print "%s is defending! %d added to defense stat. \n" % (self.name, self.defMod)

    def unDef(self):
        self.defense -= self.defMod
        #oops long
        print "%s has stopped defending. %s's defense has returned to %d. \n" % (self.name, self.name, self.defense)

    def  healthUp(self, impact):
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
        print self.name, "'s defense %s by %d! Speed:" % (change, abs(impact)), self.speed


class Player(Character):
    # gender is a player character specific trait
    def __init__(self, health, attack, defense, defMod, atkMod, speed, unDefSwitch, gender, name):
        super(Player, self).__init__(health, attack, defense, defMod, atkMod, speed, unDefSwitch, name)
        self.name = name
        self.speed = speed
        #this stuff wont work until graphics are functioning...
        #if gender == "boy": self.sprite = playerSprite[0]
        #elif gender == "girl": self.sprite = playerSprite[1]
       # else: print "excuse me"

    def attackThing(self, other):
        #super(Player, self).attackThing(other) ### I dont know why the BALLS this isn't working so
                                                                      ### copy paste for now
        damage = (self.attack+self.atkMod) - other.defense
        if damage < 0: damage = 0
        other.health -= damage
        print "You did %d damage to the %s!\n" % (damage, other.name)

    def defend(self):
        #super(Player, self).defend() ### same here
        self.defense += self.defMod
        print "You are defending!\nYour defense is now %d.\n" %(self.defense)

    def unDef(self):
        #super(Player, self).unDef() ### I feel like I've been lied to
        self.defense -= self.defMod
        print "You have stopped defending.\nYour defense has returned to %d.\n" % (self.defense)

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
        self.playerWin = playerWin
        self.enemyWin = enemyWin
        self.isPlayerTurn = isPlayerTurn
        self.elements = elements
        self.items = items
        self.compounds = compounds
        self.compoundSet = compoundSet
        
        
    def enemyGen(self): #for when player info is already known (I literally just copy pasted this)
        randEnemy = randint(0, len(ENEMY_LIST)-1)
        self.enemy = ENEMY_LIST[randEnemy]
        
    def playerTurn(self, player, enemy):
        self.player.unDefSwitch = False
        turn = raw_input("What would you like to do?\nYou can attack, defend, check inventory or run.\n")
        if turn in ["attack", "Attack", "atk", "Atk", "ATTACK"]: self.player.attackThing(self.enemy)
        elif turn in ["defend", "Defend", "def", "Def", "DEFEND"]:
            self.player.unDefSwitch = True
            self.player.defend()
        elif turn in ["run", "Run", "flee", "escape", "RUN", "asdfghjkl"]:
            if self.player.run(self.enemy) == True: self.playAgain()
        elif turn in ["inventory", "Inventory", "items"]:
            itemSet = raw_input("Which inventory would you like to access? Elements, compounds, or items?\n")
            if itemSet in ["elements", "Elements"]:
                itemSet = ELEMENTS
            elif itemSet in ["items", "Items"]:
                itemSet = STAT_MODIFIERS
            elif itemSet  in ["compounds", "Compounds"]:
                itemSet = COMPOUNDS
            self.accessInventory(itemSet, self.compounds, self.compoundSet)
        else:
            print "Sorry, I couldn't understand that.\n"
            self.playerTurn(player, enemy)
        #and then actually remove mods
        if self.enemy.unDefSwitch == True:
            self.enemy.unDef()
        self.isPlayerTurn = False

    def enemyTurn(self, player, enemy):
        self.enemy.unDefSwitch = False
        possibleTurns = ["attack", "defend"] # TODO not 50/50 defend/attack
                                                                #dependant on enemy type
        randTurn = randint(0, len(possibleTurns)-1)
        turn = possibleTurns[randTurn]
        if turn == "attack": self.enemy.attackThing(self.player)
        elif turn == "defend":
            self.enemy.unDefSwitch = True
            self.enemy.defend()
        if self.player.unDefSwitch == True:
            self.player.unDef()
        self.isPlayerTurn = True

    def statCheck(self, player, enemy):
        if self.enemy.health <= 0:
            self.playerWin = True
            self.gameOver(self.player, self.enemy)
        elif self.player.health <= 0:
            self.enemyWin = True
            self.gameOver(self.player, self.enemy)
        print self.player.name, ":", self.player.health, "\n", self.enemy.name, ":", self.enemy.health, "\n"

    def accessInventory(self, inventory, compounds, compoundSet):
        print "These are the items in the %s inventory:\n" % (inventory.dispName)
        inventory.displayInventory()
        if inventory.dispName == "Items" or inventory.dispName == "Compounds":
            itemChoice = raw_input("What would you like to use?\n")
            names = inventory.getNames()
            if (itemChoice in names):
                itemChoice = inventory.inventory[names.index(itemChoice)]
                toDo= eval(str(itemChoice) +".doTheThing()")
                eval(toDo)
                eval(str(inventory)+".removeItem(" +str(itemChoice) +")")
        else:
            self.combineElements(inventory, compounds, compoundSet)

    def combineElements(self, inventory, compounds, compoundSet):
        names = inventory.getNames()
        components = []
        choice = raw_input("Which do you want to use?\nEnter 'done' when you've finished.\n")
        while choice not in ["Done", "done"] and choice in names:
            choice = inventory.inventory[names.index(choice)]
            components.append(choice)
            choice = raw_input("Enter next.\n")
        if choice in ["Done", "done"]:
            for compound in compoundSet:
                if compound.components == components:
                    compounds.addItem(compound)
                    print "%s added to compound inventory!\n" % (compound.dispName)
                    for component in components:
                        inventory.removeItem(component)
                        
    def gameOver(self, player, enemy):
        if self.playerWin == True:
            print "You defeated the %s!\n" % self.enemy.name
            self.playAgain()
        elif self.enemyWin == True:
            print "%s defeated you...\n" % self.enemy.name
            self.playAgain()
        
    def playAgain(self):
        playAgain = raw_input("Would you like to play again?\n")
        if playAgain in ["yes", "y", "ye", "Yes"]:
            self.enemyGen()
            inBattle(self.player, self.enemy, self)
            
#this is really just for storing data
class Element(object):
    def __init__(self, dispName, atomicNum, kind, index, trueName):
        self.dispName = dispName
        self.atomicNum = atomicNum # "complexity"
        self.kind = kind #denoted as "type" in -game
        # replace properties with descrip
        #self.properties = properties
        self.index = index
        self.trueName = trueName

class StatModItem(object):
    def __init__(self, dispName, function, recipient, impact, index, trueName):
        self.dispName = dispName 
        self.function = function
        self.recipient = recipient # this and name are already strings also index I think
        self.impact = str(impact)
        self.index = index
        self.trueName = trueName

    def doTheThing(self):
        toDo = ("self." + self.recipient + "." +  self.function + "("+ self.impact + ")")
        return toDo

    def __str__(self):
        return self.trueName

class Compound(StatModItem):
    def __init__(self, dispName, function, recipient, impact, index, trueName, components):
        super(Compound, self).__init__(dispName, function, recipient, impact, index, trueName)
        self.components = components
        
class Inventory(object):
    def __init__(self, dispName, itemCount, trueName):
        self.dispName = dispName
        self.inventory = [None for val in xrange(itemCount)]
        self.trueName = trueName
        
    def addItem(self, item):
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

    def __str__(self):
        return self.trueName

############################GAME SPECIFIC GLOBALS###########################

#---------------------------------------------------------PLAYER STAT MODS------------------------------------------------------------#
#so these all effect the player and not the enemy
#ref: (dispName, function, recipient, impact, index, trueName)
HP_UP_LO = StatModItem("Cheap Potion", "healthUp", "player", 2, 0, "HP_UP_LO")
HP_UP_MID = StatModItem("Basic Potion", "healthUp", "player", 5, 1, "HP_UP_MID")
HP_UP_HI = StatModItem("Expensive Potion", "healthUp", "player", 8, 2, "HP_UP_HI")

ATK_UP_LO = StatModItem("steroids?", "atkUp", "player", 2, 3, "ATK_UP_LO")
ATK_UP_MID = StatModItem("Steroids.", "atkUp", "player", 5, 4, "ATK_UP_MID")
ATK_UP_HI = StatModItem("sTErOiDs", "atkUp", "player", 8, 5, "ATK_UP_HI")#I am feeling

DEF_UP_LO = StatModItem("Ice Pack", "defUp", "player", 2, 6, "DEF_UP_LO")
DEF_UP_MID = StatModItem("Tylenol", "defUp", "player", 5, 7, "DEF_UP_MID")
DEF_UP_HI = StatModItem("so many drugs", "defUp", "player", 8, 8, "DEF_UP_HI")# a little

SPD_UP_LO = StatModItem("Cola", "speedUp", "player", 2, 9, "SPD_UP_LO",)
SPD_UP_MID = StatModItem("Red Bull", "speedUp", "player", 5, 10, "SPD_UP_MID")
SPD_UP_HI = StatModItem("is that cocaine", "speedUp", "player", 8, 11, "SPD_UP_HI")#destructively

#---------------------------------------------------------ENEMY STAT MODS--------------------------------------------------------------#
HP_KILL_LO = StatModItem("Fake Poison", "healthUp", "enemy", -2, 12, "HP_KILL_LO")
HP_KILL_MID = StatModItem("Home-made Poison", "healthUp", "enemy", -5, 13, "HP_KILL_MID")
HP_KILL_HI = StatModItem("Stolen Poison", "healthUp", "enemy", -8, 14, "HP_KILL_LO")

ATK_KILL_LO = StatModItem("MAGIC DUST", "atkUp", "enemy", -2, 15, "ATK_KILL_LO")
ATK_KILL_MID = StatModItem("Fairy Dust", "atkUp", "enemy", -5, 16, "ATK_KILL_MID")
ATK_KILL_HI = StatModItem("Unicorn Dust", "atkUp", "enemy", -8, 17, "ATK_KILL_HI")#creative

DEF_KILL_LO = StatModItem("sad internet pictures", "defUp", "enemy", -2, 18, "DEF_KILL_LO")
DEF_KILL_MID = StatModItem("nostalgia", "defUp", "enemy", -5, 19, "DEF_KILL_MID")
DEF_KILL_HI = StatModItem("cute animals", "defUp", "enemy", -8, 20, "DEF_KILL_HI")#sorry

SPD_KILL_LO = StatModItem("Box Wine", "speedUp", "enemy", -2, 21, "SPD_KILL_LO")
SPD_KILL_MID = StatModItem("Pina Colada", "speedUp", "enemy", -5, 22, "SPD_KILL_MID")
SPD_KILL_HI = StatModItem("Tequila", "speedUp", "enemy", -8, 23, "SPD_KILL_MID")#not sorry

START_ITEMS = [HP_UP_LO, ATK_UP_LO, DEF_UP_LO, SPD_UP_LO,
                                HP_KILL_LO, ATK_KILL_LO, DEF_KILL_LO, SPD_KILL_LO]

#---------------------------------------------------------------ELEMENTS-------------------------------------------------------------------------#
#ref  (dispName, atomicNum, kind, index, trueName)
#ignore the 'kind' for now its a little bit ridiculous, I'm also not sure what its for? oops I forgot 
HYDROGEN = Element("Hydrogen", 1, "Powerful", 0, "HYDROGEN")
LITHIUM = Element("Lithium", 2, "Powerful", 1, "LITHIUM")
SODIUM = Element("Sodium", 9, "Powerful", 2, "SODIUM")
POTASSIUM = Element("Potassium", 16, "Powerful", 3, "POTASSIUM")
RUBIDIUM = Element("Rubidium", 19, "Powerful", 4,  "RUBIDIUM")
BERYLLIUM = Element("Beryllium", 3, "Relaxed", 5, "BERYLLIUM")
MAGNESIUM = Element ("Magnesium", 10, "Relaxed", 6, "MAGNESIUM")
CALCIUM = Element("Calcium", 17, "Relaxed", 7, "CALCIUM")
STRONTIUM = Element("Strontium", 20, "Relaxed", 8, "STRONTIUM")
BORON = Element("Boron", 4, "Basic", 9, "BORON")
ALUMINUM = Element("Aluminum", 11, "Basic", 10, "ALUMINUM")
CARBON = Element("Carbon", 5, "Basic", 11, "CARBON")
SILICON = Element("Silicon", 12, "Basic", 12, "SILICON")
NITROGEN = Element("Nitrogen", 6, "Basic", 13, "NITROGEN")
PHOSPHORUS = Element("Phosphorus", 13, "Basic", 14, "PHOSPHORUS")
OXYGEN = Element("Oxygen", 7, "Basic", 15, "OXYGEN")
SULFUR = Element("Sulfur", 14, "Basic", 16, "SULFUR")
FLUORINE = Element("Fluorine", 8, "Toxic", 17, "FLUORINE")
CHLORINE = Element("Chlorine", 15, "Toxic", 18, "CHLORINE")
BROMINE = Element("Bromine", 18, "Toxic", 19, "BROMINE")
IODINE =Element("Iodine", 21, "Toxic", 20, "IODINE")
NICKEL = Element("Nickel", 22, "Metal", 22, "NICKEL")


ALL_ELEMENTS = [HYDROGEN, LITHIUM, SODIUM, POTASSIUM, RUBIDIUM,
                                    BERYLLIUM, MAGNESIUM, CALCIUM, STRONTIUM, BORON,
                                    ALUMINUM, CARBON, SILICON, NITROGEN, PHOSPHORUS,
                                    OXYGEN, SULFUR, FLUORINE, CHLORINE, BROMINE, IODINE]

#this is just for now
START_ELEMENTS = ALL_ELEMENTS

#---------------------------------------------------------------COMPOUNDS--------------------------------------------------------------------#
#ref: (dispName, function, recipient, impact, index, trueName, components)
HYDROGEN_PEROXIDE = Compound("H2O2", "healthUp", "enemy", -5, 0,
                                                                     "HYDROGEN_PEROXIDE",
                                                                     [HYDROGEN, HYDROGEN, OXYGEN, OXYGEN])
AMMONIUM_NITRATE = Compound("H4N2O3", "healthUp", "enemy", -10,  1,
                                                                    "AMMONIUM_NITRATE", [HYDROGEN,
                                                                    HYDROGEN, HYDROGEN, 
                                                                    HYDROGEN, HYDROGEN, HYDROGEN,
                                                                    NITROGEN, NITROGEN,
                                                                    NITROGEN, OXYGEN, OXYGEN])
BUTANE = Compound("C4H10", "healthUp", "enemy", -7,  2, "BUTANE", [CARBON, CARBON,
                                                                   CARBON, CARBON, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN])
                                                                    #oh my god there must be a better way
PROPANE = Compound("C3H8", "healthUp", "enemy", -6, 3, "PROPANE", [CARBON, CARBON,
                                                                   CARBON, HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN, HYDROGEN,
                                                                   HYDROGEN, HYDROGEN])

COMPOUND_SET = [HYDROGEN_PEROXIDE, AMMONIUM_NITRATE, BUTANE,
                                      PROPANE]
START_COMPOUNDS = []

#----------------------------------------------------------------------ENEMIES----------------------------------------------------------------------#
#Character(health, attack, defense, defMod, atkMod, speed, name)
SLIME = Character(10, 2, 2, 0, 0, 2, False, "Slime")
WOLF = Character(15, 4, 3, 1, 0, 4, False, "Wolf")
DRAGON = Character(20, 6, 5, 2, 2, 5, False, "Dragon")
MYSTICAL_UNICORN = Character(25, 4, 3, 2, 1, 8, False, "Mystical Fabulous Unicorn")

ENEMY_LIST = [SLIME, WOLF, DRAGON, MYSTICAL_UNICORN]

#------------------------------------------------------------INVENTORIES----------------------------------------------------------------------#

ELEMENTS = Inventory("Elements", 21, "ELEMENTS")
STAT_MODIFIERS = Inventory("Items", 24, "STAT_MODIFIERS")
COMPOUNDS = Inventory("Compounds", 4, "COMPOUNDS")

###############################GAMEY GAME THINGS###########################
#for ref: blah = Battle(player, enemy, playerWin=False, enemyWin=False, playerTurn=True)
#also ref: blah = Player(health, attack, defense, defMod, atkMod, speed, unDefSwitch, gender, name)
#grab data necessary to facilitate battle

def getInventories():
    elements = ELEMENTS
    items = STAT_MODIFIERS
    compoundSet = COMPOUND_SET
    compounds = COMPOUNDS
    gameStartInventoryStock(items)
    gameStartInventoryStock(elements)
    gameStartInventoryStock(compounds)
    

def getPlayer():
    name = raw_input("What is your name?\n")
    gender = raw_input("Are you a boy or a girl?\n")
    if gender not in ["boy", "girl"]: gender = raw_input("Sorry, could you say that again?\n")
    player = Player(20, 3, 3, 0, 0, 4,False, gender, name)
    print "Your name is %s, and you are a %s.\n" % (name, gender)
    return player

def getEnemy():
    randEnemy = randint(0, len(ENEMY_LIST)-1)
    enemy = ENEMY_LIST[randEnemy]
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
    
#PLEASE REMEMBER THAT IF IT IS battle.enemyTurn the ARGUMENTS NEED TO
#BE REVERSED OR ELSE IT WILL BE GABIES TURN FOREVER
def startBattle():
    print "This is the main battle system for a chemistry rpg."
    print "Your character has just encountered some monster in his/her travels."
    print "It is your job to decide how to fight the monster."
    print "You will not know the monsters attack, defense, or health until you begin to fight."
    print "You can use items in your inventory to do damage to your enemy's power, or to aid yourself."
    print "You also have materials in your inventory-- these are reffered to as elements because I\n was not feeling creative."
    print "If you know some chemistry, perhaps you can make weapons or other stat modifying items out of them!"
    print "Hinty: compounds available for creation are H2O2, H4N2O3, C4H10, C3H8."
    print "Good luck!"
    (player, enemy) = dataGen()
    battle = Battle(player, enemy, False, False, True, ELEMENTS, STAT_MODIFIERS,
                    COMPOUNDS, COMPOUND_SET)
    player = battle.player
    enemy = battle.enemy
    if player.speed >= enemy.speed: battle.isPlayerTurn = True
    else: battle.isPlayerTurn = False
    inBattle(player, enemy, battle)
    

def inBattle(player, enemy, battle):
    print "A %s appeared!\n" % enemy.name
    while battle.playerWin == False and battle.enemyWin == False:
        if battle.isPlayerTurn == True:
            battle.playerTurn(player, enemy)
        elif battle.isPlayerTurn == False: battle.enemyTurn(enemy, player)
        battle.statCheck(player, enemy)
        if battle.isPlayerTurn == True: battle.playerTurn(player, enemy)
        else: battle.enemyTurn(enemy, player)
    
startBattle()

#EVERYTHING WORKS, but probably implement a quantity tracking system 


    
    
        





    
    
    

        
        

        
        
