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
		if type(variables[var]) == type("str") :
			line = "game.{} = '{}'\n"
		else :
			line = "game.{} = {}\n"
		if irc["version"] == 3 :
			# Works in Python 3.x
			savefile.write(line.format(var, variables[var]).encode(encoding="UTF-8"))
		else :
			# Works in Python 2.x
			savefile.write(line.format(var, variables[var]))
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
	if irc["debug"] :
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
			if irc["version"] == 3 :
				# Works in Python 3.x
				cmd = input("debug.mode@" + irc["botnick"] + " >>> ")
			else :
				# Works in Python 2.x
				cmd = raw_input("debug.mode@" + irc["botnick"] + " >>> ")
			# Execute command
			if not cmd :
				debugging = not debugging
			else :
				try :
					exec(cmd)
				except Exception as fail:
					print(fail)
		send("Debug mode closed.")
	else :
		error("Use the --debug flag to enable the use of the debug mode")



# Argument parser
def argumentor() :

	# Build ArgumentParser for command-line arguments
	parser = argparse.ArgumentParser(description = "Homeworlds IRC Bot")

	# Command-line flags
	parser.add_argument("-s", "--server", help = "Define the server the bot will connect to", default = "127.0.0.1")
	parser.add_argument("-p", "--port", help = "Define the port the bot will connect to", default = "6667")
	parser.add_argument("-c", "--channel", help = "Specify the channel the bot will join", default = "#homeworlds")
	parser.add_argument("-n", "--botnick", help = "Choose a nickname for the bot", default = "Argus")
	parser.add_argument("-i", "--indicator", help = "Set a character the bot will listen to", default = "@")
	parser.add_argument("--no-color", help = "Disables colored outputs (Uses mIRC color codes by default)", action = "store_true")
	parser.add_argument("--debug", help = "Enables debugging mode and shows messages from the IRC server", action = "store_true")
	
	# Parse arguments
	args = parser.parse_args()
	
	# Return them as a dictionary
	return vars(args)



# Basic variables for the IRC connection
irc = argumentor()
irc["version"] = sys.version_info.major


# Set the color codes for outputs
if not irc["no_color"] :
	ccsend, ccsend_, ccerror, ccerror_ = "\x0310", "\x03", "\x02\x0305", "\x03\x02"
else :
	ccsend, ccsend_, ccerror, ccerror_ = "", "", "", ""


# Connect to an IRC server	  
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((irc["server"], int(irc["port"])))
if irc["version"] == 3 :
	# Works in Python 3.x
	ircsock.send("USER {} {} {} :Homeworlds Bot\n".format(*[irc["botnick"]]*3).encode(encoding="UTF-8"))
	ircsock.send("NICK {}\n".format(irc["botnick"]).encode(encoding="UTF-8"))
else :
	# Works in Python 2.x
	ircsock.send("USER {} {} {} :Homeworlds Bot\n".format(*[irc["botnick"]]*3))
	ircsock.send("NICK {}\n".format(irc["botnick"]))


# Functions for basic IRC actions
def ping() :
	if irc["version"] == 3 :
		ircsock.send("PONG :Pong\n".encode(encoding="UTF-8"))
	else :
		ircsock.send("PONG :Pong\n")


def send(msg, chan = irc["channel"]) :
	if irc["version"] == 3 :
		ircsock.send("PRIVMSG {} :{}{}{}\n".format(chan, ccsend, msg, ccsend_).encode(encoding="UTF-8"))
	else :
		ircsock.send("PRIVMSG {} :{}{}{}\n".format(chan, ccsend, msg, ccsend_))


def error(msg, chan = irc["channel"]) :
	if irc["version"] == 3 :
		ircsock.send("PRIVMSG {} :{}ERROR: {}{}\n".format(chan, ccerror, msg, ccerror_).encode(encoding="UTF-8"))
	else :
		ircsock.send("PRIVMSG {} :{}ERROR: {}{}\n".format(chan, ccerror, msg, ccerror_))


def join(chan = irc["channel"]) :
	if irc["version"] == 3 :
		ircsock.send("JOIN {}\n".format(chan).encode(encoding="UTF-8"))
	else :
		ircsock.send("JOIN {}\n".format(chan))


def collect_msgs() :
	for msg in game.collect_sends() :
		send(msg)
	for msg in game.collect_errors() :
		error(msg)


# Join the specified channel
join(irc["channel"])


# Initialize the game
game = homeworlds.Game()
send("Hello, I am {} your personal Homeworlds Bot. To see a list of commands, type {}help.".format(irc["botnick"], irc["indicator"]))


# Main loop
while True :

	# Receive messages and remove unnecessary \n
	if irc["version"] == 3 :
		# Works in Python 3.x
		ircmsg = ircsock.recv(2048).decode(encoding="UTF-8").strip('\n\r')
	else :
		# Works in Python 2.x
		ircmsg = ircsock.recv(2048).strip('\n\r')
	
	if irc["debug"] :
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
		#try :
		eval(cmd[0][1:])(user, cmd[1:])
		collect_msgs()
		#except Exception :
			#error("Unknown command or invalid arguments")


