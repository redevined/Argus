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
    savefile = open(os.path.join("saves/" + data[0] + ".save"), "w")
    variables = vars(game)
    for var in variables :
        savefile.write("game.{} = {}\n".format(var, variables[var]))
    savefile.close()
       
       
def load(player, data) :
    try :
        savefile = open(os.path.join("saves/" + data[0] + ".save"), "r")
        for setting in savefile :
            exec(setting)
        savefile.close()
    except IOError :
        error("There are no saved games with this name")


def quit(player, data) :
    game.__init__()
    send("{} left the game. The game has been resetted.".format(player))


def debug(*args) :
    send("Entering debug mode...")
    variables = vars(game)
    print("Vars of {}".format(game))
    print
    for var in variables :
        print("game.{} = {}".format(var, variables[var]))
    print
    
    debugging = True
    while debugging :
        cmd = raw_input("debug.mode@" + irc["botnick"] + " >>> ")
        if not cmd :
            debugging = not debugging
        else :
            try :
                exec(cmd)
            except Exception :
                print(Exception)



# Functions for basic IRC actions
def ping() :
    ircsock.send("PONG :Pong\n")


def send(msg) :
    ircsock.send("PRIVMSG {} :\x0310{}\x03\n".format(irc["channel"], msg))


def error(msg) :
    ircsock.send("PRIVMSG {} :\x02\x0305ERROR: {}\x03\x02\n".format(irc["channel"], msg))


def join(chan) :
    ircsock.send("JOIN {}\n".format(chan))


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
ircsock.send("USER {} {} {} :Homeworlds Bot\n".format(*[irc["botnick"]]*3))
ircsock.send("NICK {}\n".format(irc["botnick"]))

# Join the specified channel
join(irc["channel"])

# Initialize the game
game = homeworlds.Game()
send("Hello, I am {} your personal Homeworlds Bot. To see a list of commands, type {}help.".format(irc["botnick"], irc["indicator"]))

# Main loop
while True :

    # Receive messages and remove unnecessary \n
    ircmsg = ircsock.recv(2048).strip('\n\r')
    
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


