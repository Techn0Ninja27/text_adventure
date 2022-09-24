import csv
import os
import sys
from dataclasses import dataclass


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

        # declare tuples for important map locations

        self.spawn_location = (0, 0)
        self.exit_location = (0, 0)

        # map boundaries, preload to increase performanceS
        self.boundx = range(20)
        self.boundy = range(30)

        self.impassable = ["b", "w", 'W', "D", "u", "r", "p", "T"]

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
        self.map[self.spawn_location[0]][self.spawn_location[1]] = "@"

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
        self.can_break = {"axe": "T", "machete": "u", "key": "D"}


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

        Raises:
            OutOfBounds: If x or y is outside of map area

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

        # catches IndexErrors, when x or y is outside of map
        except IndexError:
            raise OutOfBounds("coordinates out of map bounds")

    def item_pickup(self, name):
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


game = Player()
test_item = InvItem("test", "test item", 1, ["test"])

game.inventory.append(test_item)

game.item_pickup("test")
print(game.inventory)
while True:
    x = int(input("x "))
    y = int(input("y "))
    print(game.describe(x, y))
    game.print_map()
