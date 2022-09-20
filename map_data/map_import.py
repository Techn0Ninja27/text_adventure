import csv
import os

def map_import_dict_init(filename):
    import_rule_dict = {}

    # imported file example
    # empty=e
    # exit=E
    # goblin=g

    with open(filename, "r") as import_rule:
        for line in import_rule:
            line = line.replace("\n", "")
            line_content = line.split("=", 1)
            try:
                import_rule_dict[line_content[0]] = line_content[1][0]
            except IndexError:
                pass

    # output generates dict
    # empty:e
    # exit:E
    # goblin:g

    return import_rule_dict


def map_import(filename, ruleset):
    import_rule = map_import_dict_init(ruleset)
    new_file = filename.replace(".csv","")+"_imported.csv"

    if os.path.exists(new_file):
        os.remove(new_file)

    with open(filename,newline='') as csv_read, open(new_file, "w", newline='') as csv_write:
        read = csv.reader(csv_read,dialect="excel")
        write = csv.writer(csv_write,dialect="excel")
        for line in read:
            write_line = []
            for item in line:
                try:
                    write_line.append(import_rule[item])
                except KeyError:
                    write_line.append("#")
            write.writerow(write_line)





filename_ = input("filename ")

map_import(filename_, "map_import_control.txt")