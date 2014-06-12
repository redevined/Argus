#!/usr/bin/env python


import sys, os
import socket, argparse
# Import the game mechanics
import homeworlds


# Functions for handling commands from irc messages
def help(*args) :
    manual = open(os.path.join("manual.txt"))
    for line in manual :
        send(line.replace("@", irc["indicator"]))
    manual.close()
     
        
def start(player, data) :
    game.add_player(player, data[0:2], data[2])


def attack(player, data) :
    if game.run :
        game.action_attack(player, int(data[0]), data[1])
    else :
        error("No game has been started by now")
        
        
def build(player, data) :
    if game.run :
        game.action_build(player, int(data[0]), data[1])
    else :
        error("No game has been started by now")
        
        
def move(player, data) :
    if game.run :
        game.action_move(player, int(data[0]), data[1], data[2])
    else :
        error("No game has been started by now")
        
        
def trade(player, data) :
    if game.run :
        game.action_trade(player, int(data[0]), data[1], data[2])
    else :
        error("No game has been started by now")
    
    
def drop(player, data) :
    if game.run :
        game.action_sacrifice(player, int(data[0]), data[1])
    else :
        error("No game has been started by now")
    
    
def cata(player, data) :
    if game.run :
        game.action_catastrophe(player, int(data[0]))
    else :
        error("No game has been started by now")


def waive(player, data) :
    if game.run :
        game.action_waive(player)
    else :
        error("No game has been started by now")


def board(*args) :
    game.print_board()
    
    
def stash(*args) :
    game.print_stash()
    
    
def save(player, data) :
    # Create a savefile in the directory saves/ with 'name'.save
    savefile = open(os.path.join("saves/" + data[0] + ".save"), "w")
    # Get the current variables of the game
    variables = vars(game)
    for var in variables :
        # Show variable as string in the savefile if it is a string
        if type(var) == type("str") :
            line = "game.{} = '{}'\n"
        else :
            line = "game.{} = {}\n"
        try :
            # Works in Python 2.x
            savefile.write(line.format(var, variables[var]))
        except TypeError :
            # Works in Python 3.x
            savefile.write(line.format(var, variables[var]).encode(encoding="UTF-8"))
    savefile.close()
    send("Game saved.")
       
       
def load(player, data) :
    try :
        # Open savefile 'name'.save
        savefile = open(os.path.join("saves/" + data[0] + ".save"), "r")
        game.__init__()
        for setting in savefile :
            # Set all variables of the game to the variables in the file
            try :
                exec(setting)
            except Exception :
                error("Corrupt file")
        savefile.close()
        send("Game loaded, {} it's your turn.".format(variables["turn"]))
    except IOError :
        error("There are no saved games with this name")


def quit(player, data) :
    game.__init__()
    send("{} left the game. The game has been resetted.".format(player))


def debug(*args) :
    send("Entering debug mode...")
    # Get and print current variables of the game
    variables = vars(game)
    print("Vars of {}\n".format(game))
    for var in variables :
        print("game.{} = {}".format(var, variables[var]))
    print("")
    debugging = True
    while debugging :
        # Let the user input a command
        try :
            # Works in Python 2.x
            cmd = raw_input("debug.mode@" + irc["botnick"] + " >>> ")
        except NameError :
            # Works in Python 3.x
            cmd = input("debug.mode@" + irc["botnick"] + " >>> ")
        # Execute command
        if not cmd :
            debugging = not debugging
        else :
            try :
                exec(cmd)
            except Exception as fail:
                print(fail)
    send("Debug mode closed.")



# Functions for basic IRC actions
def ping() :
    try :
        ircsock.send("PONG :Pong\n")
    except TypeError :
        ircsock.send("PONG :Pong\n".encode(encoding="UTF-8"))


def send(msg) :
    try :
        ircsock.send("PRIVMSG {} :\x0310{}\x03\n".format(irc["channel"], msg))
    except TypeError :
        ircsock.send("PRIVMSG {} :\x0310{}\x03\n".format(irc["channel"], msg).encode(encoding="UTF-8"))


def error(msg) :
    try :
        ircsock.send("PRIVMSG {} :\x02\x0305ERROR: {}\x03\x02\n".format(irc["channel"], msg))
    except TypeError :
        ircsock.send("PRIVMSG {} :\x02\x0305ERROR: {}\x03\x02\n".format(irc["channel"], msg).encode(encoding="UTF-8"))


def join(chan) :
    try :
        ircsock.send("JOIN {}\n".format(chan))
    except TypeError :
        ircsock.send("JOIN {}\n".format(chan).encode(encoding="UTF-8"))


def argumentor() :

    # Build ArgumentParser for command-line arguments
    parser = argparse.ArgumentParser(description = "Homeworlds IRC Bot")

    # Command-line flags
    parser.add_argument("-s", "--server", help = "Define the server the bot will connect to", default = "127.0.0.1")
    parser.add_argument("-p", "--port", help = "Define the port the bot will connect to", default = "6667")
    parser.add_argument("-c", "--channel", help = "Specify the channel the bot will join", default = "#homeworlds")
    parser.add_argument("-n", "--botnick", help = "Choose a nickname for the bot", default = "Argus")
    parser.add_argument("-i", "--indicator", help = "Set a character the bot will listen to", default = "@")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Return them as a dictionary
    return vars(args)


def collect_msgs() :
    for msg in game.collect_sends() :
        send(msg)
    for msg in game.collect_errors() :
        error(msg)



# Basic variables for the IRC connection
irc = argumentor()

# Connect to an IRC server    
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((irc["server"], int(irc["port"])))
try :
    # Works in Python 2.x
    ircsock.send("USER {} {} {} :Homeworlds Bot\n".format(*[irc["botnick"]]*3))
    ircsock.send("NICK {}\n".format(irc["botnick"]))
except TypeError :
    # Works in Python 3.x
    ircsock.send("USER {} {} {} :Homeworlds Bot\n".format(*[irc["botnick"]]*3).encode(encoding="UTF-8"))
    ircsock.send("NICK {}\n".format(irc["botnick"]).encode(encoding="UTF-8"))

# Join the specified channel
join(irc["channel"])

# Initialize the game
game = homeworlds.Game()
send("Hello, I am {} your personal Homeworlds Bot. To see a list of commands, type {}help.".format(irc["botnick"], irc["indicator"]))

# Main loop
while True :

    # Receive messages and remove unnecessary \n
    ircmsg = ircsock.recv(2048).decode(encoding="UTF-8").strip('\n\r')
    print(ircmsg)
    
    # Reply if the server pings you
    if ircmsg.find("PING :") != -1 :
        ping()
    
    # If you find a message for you with a command in it
    if ircmsg.find("PRIVMSG {} :{}".format(irc["channel"], irc["indicator"])) != -1 :
        data = ircmsg.replace("!", ":").split(":")
        user = data[1]
        cmd = data[3].split(" ")
        
        # Call the according function
        try :
            eval(cmd[0][1:])(user, cmd[1:])
            collect_msgs()
        except Exception :
            error("Unknown command or invalid arguments")


