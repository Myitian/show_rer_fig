print("Initializing...")
print("Importing module: matplotlib.pyplot")
import matplotlib.pyplot as plt
print("Importing module: numpy, re, os, OrderedDict, nbt")
import numpy as np
import re
import os
from collections import OrderedDict
from nbt import nbt

class Command:
    def __init__(self, command:str, action:str, name = "", desc = "", alias:list[str] = []):
        self.command = command
        self.action = action
        self.name = name
        self.desc = desc
        self.alias = alias

    def to_str(self, len0 = 10, len1 = 10, len2 = 10, sep = " | "):
        return sep.join((padright(self.command, len0), padright(", ".join(self.alias), len1), padright(self.name, len2), self.desc))

class CommandManager:
    def __init__(self, commands:list[Command] = []):
        self.commands = set()
        self.command_mappings = {}
        for command in commands:
            self.register(command)

    def register(self, command:Command):
        self.commands.add(command)
        self.command_mappings[command.command] = command
        for alias in command.alias:
            self.command_mappings[alias] = command

    def readcommand(self, cmd:str):
        return self.command_mappings.get(cmd)

    def showhelp(self):
        print("Help:")
        sep = " | "
        maxl0 = maxl1 = maxl2 = 0
        for c in self.commands:
            l0 = len(c.command)
            if l0 > maxl0:
                maxl0 = l0
            l1 = len(", ".join(c.alias))
            if l1 > maxl1:
                maxl1 = l1
            l2 = len(c.name)
            if l2 > maxl2:
                maxl2 = l2
        print(sep + sep.join((padright("[Command]", maxl0), padright("[Alias]", maxl1), padright("[Name]", maxl2), "[Description]")))
        for c in self.commands:
            print(sep + c.to_str(maxl0, maxl1, maxl2, sep))

def padright(s:str, l:str, fill = " "):
    l -= len(s)
    if l > 0:
        return s + fill * l
    return s

def read_worlds():
    basic_worlds = OrderedDict()
    ext_worlds = OrderedDict()
    try_read_world(basic_worlds, ".\\data\\rer_worldgen.dat", "minecraft:overworld")
    try_read_world(basic_worlds, ".\\DIM-1\\data\\rer_worldgen.dat", "minecraft:the_nether")
    try_read_world(basic_worlds, ".\\DIM1\\data\\rer_worldgen.dat", "minecraft:the_end")
    for x in search_file(".\\dimensions", "rer_worldgen.dat"):
        try_read_world(ext_worlds, x)
    basic_worlds.update(ext_worlds)
    return basic_worlds

def try_read_world(world_dic, rer_worldgen_dat:str, world_id = ""):
    if not world_id:
        world_id = rer_worldgen_dat.replace("\\", "/").strip("./").removeprefix("dimensions/").removesuffix("/data/rer_worldgen.dat").replace("/", ":", 1)
    if os.path.isfile(rer_worldgen_dat):
        world_dic[world_id] = rer_worldgen_dat

def search_file(root:str, filename:str):
    if not os.path.isdir(root) and os.path.basename(root) == filename:
        yield root
        return
    dirlist = os.listdir(root)
    for item in dirlist:
        fullname = os.path.join(root, item)
        if os.path.isdir(fullname):
            for x in search_file(fullname, filename):
                yield x
        elif os.path.basename(fullname) == filename:
            yield fullname

def to_id(s):
    if ":" not in s:
        return "minecraft:" + s
    return s

def read_blocks(world:tuple[str]):
    filename = world[1]
    print("Read file: " + filename)
    rer_worldgen = nbt.NBTFile(filename, "r")
    total_counts = np.asarray(rer_worldgen["data"]["total_counts_at_level"])
    block_counts = rer_worldgen["data"]["level_counts_for_block"]
    sorted_block_ids = sorted(block_counts)
    return rer_worldgen, total_counts, block_counts, sorted_block_ids



def command_help(*args:tuple[str]):
    cm.showhelp()
    return False
def command_list(*args:tuple[str]):
    type = "b"
    if len(args) > 0 and len(args[0]) > 0:
        type = args[0][0].strip()
    if type in ["world", "w"]:
        l = len(worlds)
        print("Showing worlds...")
        for b in worlds:
            print(b)
        print("Total:", l)
    elif type in ["block", "b"]:
        print(f"Showing block IDs in current world {current_world[0]} ...")
        for b in sorted_block_ids:
            print(b)
        print("Total:", len(sorted_block_ids))
    return False
def command_search(*args:tuple[str]):
    if len(args) > 0 and len(args[0]) > 0:
        regstr = "|".join(args[0])
    else:
        regstr = input("Enter regular expression pattern: ")
    regex = re.compile(regstr)
    print("Search results:")
    total = 0
    for b in sorted_block_ids:
        if regex.search(b):
            print(b)
            total += 1
    print("Total:", total)
    return False
def command_select(*args:tuple[str]):
    global current_world, rer_worldgen, total_counts, block_counts, sorted_block_ids
    if len(args) > 0 and len(args[0]) > 0:
        world_id = to_id(args[0][0])
    else:
        world_id = input("Enter world ID: ")
    if world_id in worlds:
        current_world = (world_id, worlds[world_id])
        rer_worldgen, total_counts, block_counts, sorted_block_ids = read_blocks(current_world)
    else:
        print(f"World {world_id} is not existed")
    return False
def command_quit(*args:tuple[str]):
    input("Press Enter to quit... ")
    return True



while __name__ == "__main__":
    try:
        pos = range(-64, 320)
        cm = CommandManager()
        cm.register(Command("!help", command_help, "Help", "Show help", ["!h", "!?"]))
        cm.register(Command("!listblocks", command_list, "Show List", "Show block ID list or world ID list", ["!l", "!ls", "!lst"]))
        cm.register(Command("!search", command_search, "Search Block ID", "Search block ID by regular expression", ["!s", "!find"]))
        cm.register(Command("!select", command_select, "Select World", "Select world by ID", ["!sel"]))
        cm.register(Command("!quit", command_quit, "Quit", "Quit program", ["!q", "!exit", "!esc"]))

        worlds = read_worlds()
        if len(worlds) == 0:
            print("Must have at least one world available!")
            break
        current_world = next(iter(worlds.items()))
        rer_worldgen, total_counts, block_counts, sorted_block_ids = read_blocks(current_world)
        print("Done!")
        print()

        while True:
                print()
                block = input("Block ID (Enter !help to show help) >>> ").strip().split()
                cmd = cm.readcommand(block[0])
                if cmd:
                    if cmd.action(block[1:]):
                        break
                    continue
                block = to_id(block[0])
                try:
                    block_count = block_counts[block]
                    block_data = np.asarray(block_count) / total_counts
                    block_name = block.replace(":",  "$")
                    world_name = current_world[0].replace(":",  "$").replace("/",  "+")
                    plt.figure().canvas.manager.set_window_title(f"Block spawn chance of {block_name} in {world_name}")
                    plt.title(block)
                    plt.plot(pos, block_data)
                    plt.show()
                except KeyError:
                    print(block + " does not exist.")
    except Exception as e:
        print(e)
    finally:
        break
