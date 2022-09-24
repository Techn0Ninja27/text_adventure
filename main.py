import csv
import os
import sys
from dataclasses import dataclass
from terminaltables import AsciiTable


@dataclass
class InvItem:
    name: str
    lore: str
    quantity: int
    can_break: list

    def __str__(self) -> str:
        return self.lore


class OutOfBounds(Exception):
    pass


#os.path.join(sys.path[0], "data\charData.csv")
class Map:
    def __init__(self) -> None:

        # generate 2d array for map
        self.map = [["" for j in range(20)] for i in range(30)]

        self.level = 1  # init level
        self.level_list = {1: "map_data\\level_1\\level1_imported.csv",
                           2: "map_data\\level_2\\level2.csv"}  # list of levels and file paths

        self.last_level = 1

        # declare tuples for important map locations

        self.spawn_location = (0, 0)
        self.exit_location = (0, 0)

        # map boundaries, preload to increase performanceS
        self.boundx = range(20)
        self.boundy = range(30)

        self.impassable = ["b", "w", 'W', "D", "u", "r", "p", "T"]

        # map object : item name
        self.pick_able = {"$": "sword", "K": "key",
                          "&": "machete", "8": "axe", "?": "shield", "R": "rope"}

    def map_import(self):
        try:
            with open(os.path.join(sys.path[0], self.level_list[self.level]), "r", newline='') as map:
                # imports csv map using current level
                map_csv = csv.reader(map, dialect="excel")
                # generate csv obj

                # iter through array, place each object into list in memory
                for y, line in enumerate(map_csv):

                    for x, obj in enumerate(line):
                        self.map[y][x] = obj
        except KeyError:
            pass

        # goes through map and finds locations for spawn and exit
        for y, row in enumerate(self.map):
            for x, obj in enumerate(row):
                if obj == "s":
                    self.spawn_location = (x, y)
                elif obj == "E":
                    self.exit_location = (x, y)

        # places char at spawn
        self.map[self.spawn_location[1]][self.spawn_location[0]] = "@"

    # prints map, debug only
    def print_map(self):
        for i in self.map:
            string = ""
            for j in i:
                string += j
            print(string)


class Lore:
    def __init__(self) -> None:
        # item name and description
        self.item_descs = {}
        self.map_descs = {}

        # loads descriptions for items and the map

        with open(os.path.join(sys.path[0], "map_data\\item_desc.txt"), "r") as items:
            for line in items:
                name, description = line.rstrip("\n").split("=")
                self.item_descs[name] = description

        with open(os.path.join(sys.path[0], "map_data\\map_desc.txt")) as maps:
            for line in maps:
                name, description = line.rstrip("\n").split("=")
                self.map_descs[name] = description

        # list of items and the map objects they can break
        self.can_break = {"axe": "T", "machete": "u", "key": "D", "rope": "p"}


class Player(Map, Lore):
    def __init__(self) -> None:
        Map.__init__(self)
        Lore.__init__(self)
        self.map_import()

        # sets player coordinates to spawn location
        self.player_x, self.player_y = self.spawn_location

        # player stats
        self.inventory = []
        self.hp = 5
        self.gold = 0

        # keeps the map object which the character is currently on
        self.under_char = "s"

    def move_char(self, x, y):
        """moves character to point on map

        Args:
            x (int): x coordinate
            y (int): y coordinate

        Raises:
            OutOfBounds: x or y out of map bounds
        """
        # if x and y are within map bounds
        if (x in self.boundx) and (y in self.boundy):
            try:
                # removes character from map, replacing what was under
                self.map[self.player_y][self.player_x] = self.under_char
                # then sets under_char to object at new position
                self.under_char = self.map[y][x]
                # places character at new location
                self.map[y][x] = "@"
                # changes player coords
                self.player_x, self.player_y = x, y

            except IndexError:
                pass
        else:
            # raises custom exception
            raise OutOfBounds("Coords out of bounds")

    def move_check(self, x, y):
        """checks if point in map is passable

        Args:
            x (int): x coordinate
            y (int): y coordinate


        Returns:
            bool: point passability
        """
        try:
            # checks if map object is in list of impassable objects
            # returns true or false
            if self.map[y][x] in self.impassable:
                return False
            else:
                return True

        # cannot move to spot if outside map
        except IndexError:
            return False

    def item_add_to_inv(self, name):
        """Generates InvItem object and appends to inventory

        Args:
            name (str): name of item
        """
        # declare variables
        can_break = []
        item_desc = ""

        # checks if item is in inventory
        item_in_inventory = False
        for i, item in enumerate(self.inventory):

            if item.name == name:
                # increments quantity of item by 1
                item_in_inventory = True
                self.inventory[i].quantity += 1

        # if item not in inv
        if item_in_inventory is False:
            # gets item description
            try:
                item_desc = self.item_descs[name]
            except KeyError:
                item_desc = "MISSING"

            # if item has can break attribute
            if name in self.can_break:
                can_break.append(self.can_break[name])

            # creates InvItem object using collected info
            picked_item = InvItem(name, item_desc, 1, can_break)

            # appends object to inventory
            self.inventory.append(picked_item)

    def describe(self, x, y):
        """Describes point on map

        Args:
            x (int): x coordinate
            y (int): y coordinate

        Raises:
            OutOfBounds: x or y out of map area

        Returns:
            str: description of point
        """
        item = ""
        description = "MISSING"
        # finds item on map, if item out of bounds, raises out of bounds
        try:
            item = self.map[y][x]
        except IndexError:
            raise OutOfBounds

        # retrieves item description from map_descs dict
        try:
            description = self.map_descs[item]
        except KeyError:
            pass

        return description

    def describe_direct(self, obj):
        """Directly describes map object

        Args:
            obj (str): map_object

        Returns:
            str: object description
        """

        # describes objects on the map directly
        try:
            description = self.map_descs[obj]
        except KeyError:
            description = "MISSING"

        return description

    def surrounding_describe(self, x, y):
        """Prints table of descriptions of surroundings

        Args:
            x (int): x coordinate
            y (int): y coordinate

        Raises:
            OutOfBounds: x or y out of map
        """

        # checks if x and y are within map boundaries
        if not((x in self.boundx) and (y in self.boundy)):
            raise OutOfBounds
            return

        data = [["" for i in range(3)] for j in range(3)]

        # i cant figure out a smart way to do this
        # basicaly it just goes and makes a grid of descriptions

        try:
            data[1][1] = self.describe_direct(self.under_char)
        except OutOfBounds:
            pass
        try:
            data[0][1] = self.describe(x, y-1)
        except OutOfBounds:
            pass
        try:
            data[2][1] = self.describe(x, y+1)
        except OutOfBounds:
            pass
        try:
            data[1][0] = self.describe(x-1, y)
        except OutOfBounds:
            pass
        try:
            data[1][2] = self.describe(x+1, y)
        except OutOfBounds:
            pass

        # ascii table
        table = AsciiTable(data)
        table.inner_column_border = True
        table.inner_row_border = True
        print(table.table)

    def avaliable_moves(self, x, y):
        """prints and returns all possible moves at location

        Args:
            x (int): x coordinate
            y (int): y coordinate

        Raises:
            OutOfBounds: out of map bounds

        Returns:
            list: list of possible moves
        """
        if not((x in self.boundx) and (y in self.boundy)):
            raise OutOfBounds
            return

        # declare list
        avaliable_move = []

        # checks cardinal directions for passability
        if self.move_check(x, y-1) is True:
            avaliable_move.append("north")
        if self.move_check(x+1, y) is True:
            avaliable_move.append("east")
        if self.move_check(x, y+1) is True:
            avaliable_move.append("south")
        if self.move_check(x-1, y) is True:
            avaliable_move.append("west")

        # checks if object under character can be picked up
        if self.under_char in self.pick_able:
            avaliable_move.append(f"pick")

        # checks items in inventory
        # checks for the items that can be broken by that item in the cardinal directions
        for item in self.inventory:
            if item.can_break:
                breakable_obj = self.can_break[item.name]
                if (self.map[y-1][x] == breakable_obj) or (self.map[y+1][x] == breakable_obj) or (self.map[y][x-1] == breakable_obj) or (self.map[y][x+1] == breakable_obj):
                    avaliable_move.append("break")

        # prints moves
        print("Avaliable Moves")
        for i in avaliable_move:
            print(i)

        return avaliable_move

    def pick_item(self):
        """Takes item from under char to inventory
        """
        self.item_add_to_inv(self.pick_able[self.under_char])
        self.under_char = " "

    def break_item(self, x, y):
        """breaks object with item

        Args:
            x (int): x coordinate
            y (int): y coordinate
        """
        for item in self.inventory:
            if item.can_break:
                breakable_obj = self.can_break[item.name]
                if self.map[y-1][x] == breakable_obj:
                    self.map[y-1][x] = " "
                if self.map[y+1][x] == breakable_obj:
                    self.map[y+1][x] = " "
                if self.map[y][x-1] == breakable_obj:
                    self.map[y][x-1] = " "
                if self.map[y][x+1] == breakable_obj:
                    self.map[y][x+1] = " "

    def inventory_view(self):
        """prints inventory contents and their tags
        """
        for i in self.inventory:
            print(
                f"{i.name}: {i.lore}. Quantity: {i.quantity}. Can break{i.can_break}")

    def user_input(self):
        """takes turn input from user

        Returns:
            str: move
        """
        while True:
            # while true to prevent wrong information from breaking game
            print("Turn")
            move = input("")

            # cheat codes

            # item give
            if move == "ITEM":
                item_give = input("ITEM NAME: ")
                self.item_add_to_inv(item_give)

            # teleport
            elif move == "TP":
                while True:
                    while True:
                        try:
                            x = int(input("x: "))
                            y = int(input("y: "))
                        except ValueError:
                            pass
                        else:
                            break
                    try:
                        self.move_char(x, y)
                    except OutOfBounds:
                        print("out of bounds")
                    else:
                        break

            # prevent empty strings
            try:
                move[0]
            except IndexError:
                move = " "

            # makes input lowercase
            move = move.lower()

            # checks moves and returns
            if move[0] == "n":
                return "n"
                break
            elif move[0] == "e":
                return "e"
                break
            elif move[0] == "s":
                return "s"
                break
            elif move[0] == "w":
                return "w"
                break
            elif move[0] == "p":
                return "p"
                break
            elif move[0] == "b":
                return "b"
                break

            print("unsupported move")

    def turn(self):
        """Single game turn
        """

        # prints map
        print()
        self.print_map()

        # surroundings
        print()
        print("Your Surroundings")
        self.surrounding_describe(self.player_x, self.player_y)

        # inventory
        print("inventory:")
        self.inventory_view()

        # prints avaliable moves
        print()
        move_options = self.avaliable_moves(self.player_x, self.player_y)

        # takes user input
        move = self.user_input()

        # legit just a switch case
        if "north" in move_options:
            if move == ("n"):
                self.move_char(self.player_x, self.player_y-1)
        if "west" in move_options:
            if move == "w":
                self.move_char(self.player_x-1, self.player_y)
        if "south" in move_options:
            if move == "s":
                self.move_char(self.player_x, self.player_y+1)
        if "east" in move_options:
            if move == "e":
                self.move_char(self.player_x+1, self.player_y)
        if "pick" in move_options:
            if move == "p":
                self.pick_item()
        if "break" in move_options:
            if move == "b":
                self.break_item(self.player_x, self.player_y)

    def level_up(self):
        """increases level
        """

        # increments level
        self.level += 1
        # imports new map
        self.map_import()
        # sets new player spawn location
        self.player_x, self.player_y = self.spawn_location

    def play(self):
        """plays game
        """
        print("             _                 _                   ")
        print("    /\      | |               | |                  ")
        print("   /  \   __| |_   _____ _ __ | |_ _   _ _ __ ___  ")
        print("  / /\ \ / _` \ \ / / _ \ '_ \| __| | | | '__/ _ \ ")
        print(" / ____ \ (_| |\ V /  __/ | | | |_| |_| | | |  __/ ")
        print("/_/    \_\__,_| \_/ \___|_| |_|\__|\__,_|_|  \___| ")

        while True:
            while True:
                if self.under_char == "E":
                    break
                else:
                    self.turn()
            self.level_up()
            if self.level > self.last_level:
                break

            print()
            print(f"level {self.level}")
            print()

        print("          _______                      _______  _        _ ")
        print("|\     /|(  ___  )|\     /|  |\     /|(  ___  )( (    /|( )")
        print("( \   / )| (   ) || )   ( |  | )   ( || (   ) ||  \  ( || |")
        print(" \ (_) / | |   | || |   | |  | | _ | || |   | ||   \ | || |")
        print("  \   /  | |   | || |   | |  | |( )| || |   | || (\ \) || |")
        print("   ) (   | |   | || |   | |  | || || || |   | || | \   |(_)")
        print("   | |   | (___) || (___) |  | () () || (___) || )  \  | _ ")
        print("   \_/   (_______)(_______)  (_______)(_______)|/    )_)(_)")


game = Player()


game.play()
