import csv
import os
import sys

class OutOfBounds(Exception):
    pass





#os.path.join(sys.path[0], "data\charData.csv")
class Map:
    def __init__(self) -> None:

        self.map = [["" for j in range(20)] for i in range(30)] # generate 2d array for map
        
        self.level = 1 # init level
        self.level_list = {1:"map_data\\level_1\\level1_imported.csv",2:"map_data\\level_2\\level2.csv"} # list of levels and file paths

        # declare tuples for important map locations

        self.spawn_location = (0,0)
        self.exit_location = (0,0)
    
        # map boundaries, preload to increase performanceS
        self.boundx = range(20)
        self.boundy = range(30)
    
    def map_import(self):
        try:
            with open(os.path.join(sys.path[0], self.level_list[self.level]), "r", newline='') as map:
                # imports csv map using current level
                map_csv = csv.reader(map,dialect="excel")
                # gen csv obj

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
                    self.spawn_location = (x,y)
                elif obj == "E":
                    self.exit_location = (x,y)


        # places char at spawn
        self.map[self.spawn_location[0]][self.spawn_location[1]] = "@"

    # prints map, debug only
    def print_map(self):
        for i in self.map:
            string=""
            for j in i:
                string +=j
            print(string)


class Player(Map):
    def __init__(self) -> None:
        super().__init__()
        self.map_import()
        self.player_x, self.player_y = self.spawn_location


        # player stats
        self.items = []
        self.hp = 5
        self.gold = 0

        self.under_char = "s"

    def move_char(self,x,y):
        if x in self.boundx and y in self.boundy:
        try:
            self.map[self.player_y][self.player_x] = self.under_char
            self.under_char = self.map[y][x]
            self.map[y][x] = "@"
                self.player_x,self.player_y = x,y
                
        except IndexError:
            pass
        else:
            raise OutOfBounds("Coords out of bounds")
        
            




game = Player()

game.print_map()
print(game.spawn_location)
print(game.player_x,game.player_y)
print(game.under_char)
game.map[game.player_y][game.player_x] = game.under_char
print(game.under_char)
game.print_map()
while True:
    x = int(input("x "))
    y = int(input("y "))
    game.move_char(x,y)
    game.print_map()
    

