# DWM Monsterdex
# Author:   Donny Ebel
# Created | Edited:   10/30/23 | 10/31/23

# Credits for data scraping (with great respect):
# Prima's Official Strategy Guide Dragon Warrior Monsters 2: Cobi's Journey & Tara's Adventure
# https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/19460
# https://gamefaqs.gamespot.com/gbc/525414-dragon-warrior-monsters-2-cobis-journey/faqs/14383

#   Updates:
#   10/31/23    -Cleaned up the file; commented out unfinished starts and triaged tasks for mental priority.
#               -Added credits
#               -Created repository
#               -Fixed family search, but does not take into account Slime/Slime family and Dragon/Dragon family atm
#               -Created monster_parent_pairs.txt, which is every breeding combination provided in the guide. Doesn't
#                   print them correctly yet, though.
#               -Created populate_library(), which does what it sounds like. It reads monster use, parents, and data
#                   text files into memory in the library.
#   10/30/23    -Created this main file and text files for storing data for monsters, skills, and the farm.
#               -Formulated basic design: user types in the name of a monster to see all of its data, but also has the
#                   option to add it to a "farm" in the program to track owned monsters, or at least monsters in
#                   question. Also added basic commands to view the farm
#               -Created process to read in monster data from a file. I did this to avoid searching a ton and provide
#                   an easy way to add things or fix mistakes later.
#               TODO:
#               -Add ALL monster parentage -- priority!
#               -Add functionality to enable printing a whole family at once
#               -Add text file manipulation to save and load farms
#               -Add toggle to show resistances
#               -Add toggle to automatically show farm after successful search
#               -Add DWM1 vs DWM2 toggle (include version differences)
#               - ^ Add monster locations ^
#               -Add rarity!
#               -Add colors
#               -Add clearFarm and clearScreen functionality
#               -Distinguish between Slime/Slime family and Dragon/Dragon family
#               -Add WonderEgg link note
#

# Helpful global lists:
FAMILY_LIST = ['slime', 'dragon', 'beast', 'bird', 'plant', 'bug', 'devil', 'zombie', 'material', 'water', '???']
resist_key = [
            'Blaze, Blazemore, Blazemost, BigBang, FireSlash',
            'Firebal, Firebane, Firebolt',
            'Bang, Boom, Explodet',
            'WindBeast, Vacuum, Infernos, Infermore, Infermost, MultiCut, VacuSlash',
            'Lightning, Bolt, Zap, Thordain, Hellblast, BoltSlash',
            'IceBolt, SnowStorm, Blizzard, IceSlash',
            'Radiant, Surround, SandStorm',
            'Sleep, NapAttack, SleepAir, SleepAll',
            'EerieLite, UltraDown, Beat, K.O.Dance, Defeat',
            'OddDance, RobDance, RobMagic',
            'StopSpell',
            'PaniDance, PanicAll',
            'Sap, Defense, SickLick',
            'Slow, SlowAll',
            'Sacrifice, Kamikaze, Ramming',
            'MegaMagic',
            'FireAir, BlazeAir, Scorching, WhiteFire',
            'FrigidAir, IceAir, IceStorm, WhiteAir',
            'PoisonHit, PoisonGas, PoisonAir',
            'Paralyze, PalsyAir',
            'Curse',
            'LegSweep, LushLicks, Ahhh, BigTrip, WarCry, LureDance',
            'DanceShut',
            'MouthShut',
            'RockThrow, CallHelp, YellHelp',
            'GigaSlash',
            'Geyser, Watershot, Tidalwave']


class Monster:
    def __init__(self, n, f):
        self.name = n           # Monster species; str
        self.family = f         # Family name; str
        self.stats = []         # Max Level, Exp Growth, HP MP AT DF AG IN
        self.skills = []        # skill1, skill2, skill3
        self.resists = []       # See README.md for list
        self.parent_pairs = {}  # Dict (pedigree, mate) = self.name
        self.used_in = {}
        self.rarity = []        # Rarity in *, scale .5-5
        self.locations = []     # Available Locations

    def print_data(self):
        # Print stats!
        print(self.name, " | ", self.family, " Family")
        print("LVL: ", self.stats[0], " ATK: ", self.stats[4])
        print("EXP: ", self.stats[1], " DEF: ", self.stats[5])
        print("HP:  ", self.stats[2], " AGL: ", self.stats[6])
        print("MP:  ", self.stats[3], " INT: ", self.stats[7])
        print("Skill 1: ", self.skills[0])
        print("Skill 2: ", self.skills[1])
        print("Skill 3: ", self.skills[2])

        # Print name and family, followed by possible parents involving self monster
        if self.parent_pairs:   # fixme
            print('')
            print(self.name, "Can Be Bred With:")
            for i in range(0, len(self.parent_pairs)):
                print(self.parent_pairs[i])
            print("")
        else:
            print("There is no way to breed", self.name, "!")

        # Print name and family, followed by unions involving self monster
        if self.used_in:
            print('')
            print(self.name, "Can Produce:")
            for child in self.used_in:
                print(child)
            print("")
        else:
            print(self.name, "is not used in any breeding patterns!")

        # Optionally Print Resists:
        print_resists = False
        if print_resists:
            for r in range(0, 27):
                print("Resistances:")
                print(self.resists[r], resist_key[r])

        print("")


class Library:  # A Library is a list of all of the monsters in DWM I+II
    def __init__(self):
        self.roster = []                # A list of Monsters, which contain ALL currently stored monster data
        self.monster_parents_dict = {}  # A dict of key:value(s) of monster_name:possible parents
        self.monster_uses_dict = {}     # A dict of key:value(s) of monster_name:unique possible children

    def print_everything(self):
        for monster in self.roster:
            monster.print_data()

    def print_family(self, input):
        for monster in self.roster:
            if monster.family == input:
                monster.print_data(0)


class Farm:  # The Farm is a list of monsters currently available to the user in this session
    def __init__(self):
        self.roster = []  # List of monsters on the farm

    def add_monster(self, mon):
        self.roster.append(mon)

    def print_everything(self):
        count = 0
        for mon in self.roster:
            count += 1
            print('#', count)
            print(mon, "\n")


# HELPER FUNCTIONS
def populate_library(lib):
    # First, import ALL monster "usage" data
    # Each line is a tuple of 2 or more monster names where the head is the parent monster in question and following are
    # the unique children of said parent.
    with open("monster_use_data.txt") as monster_use_data:
        lines = monster_use_data.readlines()
        count = 0

        # Look at each parent entry...
        for line in lines:
            # ...format, pop parent name, then update the dictionary with the name and the trimmed list of children...
            count += 1
            line = line.rstrip()
            line = line.split()
            parent_name = line.pop(0)
            lib.monster_uses_dict.update({parent_name: line})

    monster_use_data.close()

    # Next, import parents for every monster.
    with open("monster_parent_pairs.txt") as monster_parent_pairs:
        lines = monster_parent_pairs.readlines()
        count = 0

        for line in lines:
            count += 1
            line = line.rstrip()
            line = line.split()
            child_name = line.pop(0)
            lib.monster_parents_dict.update({child_name: line})

    monster_parent_pairs.close()

    # Finally, import ALL monster data from monster_data.txt into the library's roster
    # Each line holds data corresponding to the Monster class data type
    with open("monster_data.txt") as monster_data:
        lines = monster_data.readlines()
        count = 0

        for line in lines:
            count += 1
            line = line.rstrip()
            line = line.split()

            current_monster = Monster(line[0], line[1])
            current_monster.stats = [line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9]]
            current_monster.skills = [line[10], line[11], line[12]]
            current_monster.resists = [line[13], line[14], line[15], line[16], line[17], line[18], line[19], line[20],
                                       line[21], line[22], line[23], line[24], line[25], line[26], line[27], line[28],
                                       line[29], line[30], line[31], line[32], line[33], line[34], line[35], line[35],
                                       line[37], line[38], line[39]]
            current_monster.parent_pairs = lib.monster_parents_dict.get(current_monster.name)
            current_monster.used_in = lib.monster_uses_dict.get(current_monster.name)

            lib.roster.append(current_monster)

    monster_data.close()


# Title
print("DWM Monsterdex")
print("Author: Donny 'CPU!' Ebel")
print("Twitter X @misc_cpu\n")

# Create and populate library from file
library = Library()
populate_library(library)

# Create and populate farm from file
farm = Farm()
# populate farm later       fixme

# Main loop
farm_data = open("farm_data.txt", 'a')
accepting_input = True

while accepting_input:
    print('--> Enter a monster name to see its entry.')
    user_input = input('(Alt Commands: farm | library | family | save | exit)\n')
    print('')

    # Process user input
    user_input = user_input.lower()

    # First search for family name input
    if user_input in FAMILY_LIST:
        for monster in library.roster:
            if monster.family.lower() == user_input:
                monster.print_data()

    # Handle farm input (prints the NAME of all monsters currently on the farm)
    elif user_input == "farm":
        print("Will fix printing the farm in the future!")
        # farm.print_everything()       fixme

    # Handle library input (prints ALL monster data)
    elif user_input == "library":
        library.print_everything()

    # Handle save input
    elif user_input == "save":
        print("Will add file/farm functionality another time.")
    #    for monster in farm.roster:
    #        farm_data.write(monster.name)

    # Handle graceful exit
    elif user_input == "exit":
        accepting_input = False

    # Finally, handle printing monster data, optionally adding it to the farm
    else:
        for monster in library.roster:
            if monster.name.lower() == user_input:
                monster.print_data()
                user_input = input('--> Would you like to add this to the farm? (y/n) ').lower()
                print('')
                if user_input == 'y':
                    farm.add_monster(monster)

# Close the file
farm_data.close()
