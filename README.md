# Argus


Argus is an IRC Bot for playing Homeworlds.

> Start Argus like this:  
>`python bot.py [-h] [-s SERVER] [-p PORT] [-c CHANNEL] [-n BOTNICK] [-i INDICATOR] [--debug]`

> Use `python bot.py --help` for additional info on starting the Homeworlds Bot.


### General Commands:

* `@help` - Print this help.
* `@start [Star] [Star] [Ship]` - Join a new game with two _Stars_ and a starter _Ship_. If you are the second player joining the game, the game starts afterwards.
* `@save [Name]` - Save the current game under a specific name.
* `@load [Name]` - Load a previously saved game.
* `@quit` - Leave the current game. The game will be resetted.
* `@debug` - Enter the debug mode. This lets you see and manipulate all variables of the game.


### In-Game Commands:

* `@board` - Print the current situation of the game board.
* `@stash` - Print the current stash.
* `@attack [SysID] [Ship]` - Perform an attack action in the star system with _#SysID_ on the specified Ship.
* `@build [SysID] [Ship]` - Build the _Ship_ in system _#SysID_.
* `@move [SysID] [Ship] [SysID/Star]` - Move your _Ship_ from system _#SysID_ to either an existing star system (second _SysID_), or a new one (_Star_).
* `@trade [SysID] [Ship] [Ship]` - Trade a _Ship_ (first) from your fleet in system _#SysID_ for a new _Ship_ (second) with the stash.
* `@drop [SysID] [Ship]` - Sacrifice one of your own _Ships_ to get multiple actions according to its size.
* `@cata [SysID]` - Check a star system for overpopulations and trigger catastrophes on them.
* `@waive` - Waive and pass the turn to the next player. Useful if you can not use all of your sacrifice actions.


#### Legend:

* @: Indicator character. Use this to send commands to the bot.
* SysID: Integer number of the star system in which you like to perform the action, staring from 0.
* Ship: Representation consists of Size+Color, therefore [123][rgby], e.g. '3r' would be a large red ship.
* Star: The representation of stars is the same like Ships.


> To learn playing Homeworlds visit the official homepage and view the rules [here](http://www.looneylabs.com/rules/homeworlds).
