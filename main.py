import csv
import os
import sys

#os.path.join(sys.path[0], "data\charData.csv")
class Map:
    def __init__(self) -> None:

        self.map = [["" for j in range(20)] for i in range(30)] # generate 2d array for map
        
        self.level = 1 # init level
        self.level_list = {1:"map_data\\level_1\\level1_imported.csv",2:"map_data\\level_2\\level2.csv"} # list of levels and file paths

        # declare tuples for important map locations

        self.spawn_location = (0,0)
        self.exit_location = (0,0)
    
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
                    self.spawn_location = (y,x)
                elif obj == "E":
                    self.exit_location = (y,x)


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
        self.player_x, self.player_y = self.spawn_location


        # player stats
        self.items = []
        self.hp = 5
        self.gold = 0

        self.under_char

    def move_char(self,x,y):
        self.map[self.player_y][self.player_x] = " "
        




map = Map()
map.map_import()
map.print_map()


