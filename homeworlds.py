#!/usr/bin/env python


# The actual game mechanisms
class Game() :


    def __init__(self) :
    
        # Basic variables and arrays
        self.players = {}
        self.universe = []
        self.colors = ("r", "g", "b", "y")
        self.sizes = (1, 2, 3)
        
        # Stash: red=[s,m,l], green=[s,m,l], blue=[s,m,l], yellow=[s,m,l]
        self.stashsize = 5
        self.stash = [[self.stashsize for i in self.sizes] for j in self.colors]
        self.winner = []
        self.run = False
        
        # Variables for sacrifices
        self.executable = self.colors + ("x",)
        self.actioncounter = 1
        
        # Messages and Errors
        self.send_bag = []
        self.error_bag = []
   


    def add_player(self, player, homeworld, homeship) :
    
        # Current number of players
        self.playernumber = len(self.players)
        
        # Add player, if not enough players present
        if self.playernumber < 2 :
        
            # If input is valid
            if (int(homeworld[0][0]) in self.sizes and homeworld[0][1] in self.colors) and (int(homeworld[1][0]) in self.sizes and homeworld[1][1] in self.colors) and (int(homeship[0]) in self.sizes and homeship[1] in self.colors) :
            
                # Add key for playernumber
                self.playernumber += 1
                self.players[player] = self.playernumber
                # Add homeworld to the board
                self.universe.append([homeworld, [], []])
                self.universe[self.playernumber-1][self.players[player]].append(homeship)
                # Say hello to the new player
                self.send("Welcome to the game, {}. You are Player {}".format(player, self.playernumber))
                
                # Subtract starting elements from stash
                for item in (homeworld[0], homeworld[1], homeship) :
            
                    self.stashx, self.stashy = self.get_stash(item)
                    self.stash[self.stashy][self.stashx] -= 1
            
                # If 2 players are present, start game
                if len(self.players) == 2 :
                    self.start_game()
            
            else :
                # Throw error if elements do not match standard layout
                self.error("Please use Size+Color as the representation for ships and stars")
        
        else :
            # Throw error if game has already started
            self.error("The game has already started")
    


    def start_game(self) :
    
        # Start game and set player 1 as current player
        self.run = True
        self.turn = self.first()
        self.send("=== Starting Game. Current Players: ===")
        
        # Print the players
        self.send("Player 1: {}".format(self.first()))
        self.send("Player 2: {}".format(self.other(self.first())))
            
        # Print out the start layout of the game board
        self.print_board()
        self.print_stash()
        self.send("{}, you start.".format(self.turn))



    def print_board(self) :
    
        self.send("=======================================")
        
        # Print every system line by line
        for i in range(len(self.universe)) :
        
            # The 'strings' are the strings of stars and both players ships in the system
            self.unistrings = {}
            
            for div in range(3) :
                # Format the system so it can be easily printed
                self.unistrings[div] = str(self.universe[i][div]).replace("[", "").replace("]", "").replace(",", "").replace("'", "")
                
            # Print current system
            self.send("{}:    {} < {} > {}".format(i, self.unistrings[1], self.unistrings[0], self.unistrings[2]))

        self.send("=======================================")
        
        
        
    def print_stash(self) :
    
        # Print the current stash
        self.send("=======================================")
        self.send("          s m l")
        self.send("Red:      {} {} {}".format(*self.stash[0]))
        self.send("Green:    {} {} {}".format(*self.stash[1]))
        self.send("Blue:     {} {} {}".format(*self.stash[2]))
        self.send("Yellow:   {} {} {}".format(*self.stash[3]))
        self.send("=======================================")
    


    def first(self) :
    
        # Simply returns the name of the first player
        for player in self.players :
            if self.players[player] == 1 :
                return player


    
    def other(self, current) :
    
        # Simply returns the id of the opponent
        for player in self.players :
            if player != current :
                return player
            


    def next_turn(self, player) :
        
        # If there are no actions left
        if not self.actions_left() :
        
            # Swap the current player
            self.turn = self.other(player)
            # Print the board
            self.print_board()
        
            # Check if there is a winner
            if self.game_finish() :
            
                # If both players have won
                if len(self.winner) == 2 :
                    self.send("Game finished: Draw")
                else :
                    self.send("Game finished: {} has won the game!".format(*self.winner))
            
                # Reinitialize the game
                self.__init__()
            
            else :
                self.send("{}, it's your turn.".format(self.turn))



    def game_finish(self) :
    
        player = self.first()
        
        # Check if first player is defeated
        if not self.universe[0][1] or not self.universe[0][0]:
            self.winner.append(self.other(player))
            
        # Check if second player is defeated
        if not self.universe[len(self.universe)-1][2] or not self.universe[len(self.universe)-1][0] :
            self.winner.append(player)
            
        # Return True if there is a winner
        return bool(self.winner)



    def check_turn(self, player) :
    
        # Check if game has started
        if self.run :
        
            # Check if it is the turn of the sending player
            if player == self.turn :
                
                return True

            else :
                # Throw Error
                self.error("It is not your turn")
                return False
        
        else :
            # Throw Error
            self.error("No game has been started by now")
            return False



    def check_item(self, item, *sections) :

        # Check if item is a color
        if item in self.colors + ("x",) :
        
            # Check if the action is blocked through a sacrifice
            if item in self.executable :
            
                # Check it is either in the system or is part of a sacrifice action
                if len(self.executable) == 1 or item in str(sections) :
                
                    return True
                    
                else :
                    # Throw Error
                    self.error("You do not have this color in the current system")
                    return False
                
            else :
                # Throw Error
                self.error("You can not use this action right now")
                return False
                
        # Check if item is in the current system
        elif item in str(sections) :
        
            return True
        
        else :
            # Throw Error
            self.error("There is no such ship in the current system")
            return False



    def get_stash(self, item) :
    
        # Get stash y-coordinate from color code in item
        if item[1] == "r" :
            self.y = 0
        elif item[1] == "g" :
            self.y = 1
        elif item[1] == "b" :
            self.y = 2
        elif item[1] == "y" :
            self.y = 3
            
        # Get x-coordinate form size of item
        self.x = int(item[0]) - 1
        
        return self.x, self.y



    def actions_left(self) :
    
        # Decrease counter for actions during sacrifice
        self.actioncounter -= 1
        
        # If actions left
        if self.actioncounter > 0 :
        
            self.send("You have got {} action(s) left.".format(self.actioncounter))
            return True
        
        # If no actions left
        else :
            # Reset actioncounter and colors
            self.actioncounter = 1
            self.executable = self.colors + ("x",)
            return False



    def action_attack(self, player, sysid, target) :
        
        # Shorten list names
        try :
            self.star = self.universe[sysid][0]
            self.you = self.universe[sysid][self.players[player]]
            self.opponent = self.universe[sysid][self.players[self.other(player)]]
        except IndexError :
            self.error("Star system not existing")
            return None
        
        # Check if action can be executed
        if self.check_turn(player) and self.check_item("r", self.star, self.you) and self.check_item(target, self.opponent) :
        
            # Check if you have a larger or equal sized ship
            if target[0] <= max([ship[0] for ship in self.you]) :
            
                # Delete target from opponent's fleet
                self.opponent.remove(target)
                # Add it to your own fleet
                self.you.append(target)
                # Swap turns
                self.next_turn(player)
                
            else :
                # Throw Error
                self.error("You cannot attack a larger ship")



    def action_build(self, player, sysid, target) :
    
        # Shorten list names
        try :
            self.star = self.universe[sysid][0]
            self.you = self.universe[sysid][self.players[player]]
        except IndexError :
            self.error("Star system not existing")
            return None
        
        
        # Recursive function for checking the stash for smaller ships
        def check_stash(index) :
            
            try :
                # Try again if stash is empty
                if self.stash[self.stashy][index] == 0 :
                    return check_stash(index+1)
                
                # Stop if stash is not empty        
                else :
                    # Found smallest ship in stash, check if it is the same one the player is building
                    if index == self.stashx :
                        return True
                    else :
                        return False
                            
            except IndexError :
                return False
        
        
        # Check if action can be executed
        if self.check_turn(player) and self.check_item("g", self.star, self.you) and self.check_item(target[1], self.you) :
        
            # Get coordinates of target inside the stash
            self.stashx, self.stashy = self.get_stash(target)
            
            # Check if there are smaller ships or the stash is empty
            if check_stash(0) :
            
                # Reduce ship's position in stash
                self.stash[self.stashy][self.stashx] -= 1
                # Add it to your fleet
                self.you.append(target)
                # Swap turns
                self.next_turn(player)
            
            else :
                # Throw Error
                self.error("Target either not in stash or smaller ships are available")
        


    def action_move(self, player, sysid, target, location) :
    
        # Shorten list names
        try :
            self.star = self.universe[sysid][0]
            self.you = self.universe[sysid][self.players[player]]
            self.opponent = self.universe[sysid][self.players[self.other(player)]]
        except IndexError :
            self.error("Star system not existing")
            return None
        
        
        # Functions for checking star sizes and the move action
        def check_path(loc) :
        
            for star in self.star :
            
                if star[0] in loc :
                    # Throw Error
                    self.error("You can't travel to stars with the same size")
                    return False
                    
            return True
        
        def move_path(newsys) :
        
            # Move it to new location
            self.universe[newsys][self.players[player]].append(target)
            
            # Delete star system if it is left empty
            if not self.you and not self.opponent and len(self.star) == 1 :
            
                self.stashx, self.stashy = self.get_stash(*self.star)
                self.stash[self.stashy][self.stashx] += 1
                del(self.universe[sysid])
                    
            # Swap turns
            self.next_turn(player)
        
        
        # Check if action can be executed
        if self.check_turn(player) and self.check_item("y", self.star, self.you) and self.check_item(target, self.you) :
        
            # If location is an existing system
            if location.isdigit() :
                
                location = int(location)
                
                try :
                
                    if check_path(str(self.universe[location][0])) :
                    
                        # Delete target from current location
                        self.you.remove(target)
                    
                        # Actual move action
                        move_path(location)
                        
                except IndexError :
                    self.error("Star system not existing")
                    return None
                        
            # If location is a star
            elif int(location[0]) in self.sizes and location[1] in self.colors :
            
                # Check if stars have different sizes
                if check_path(location) :
                
                    self.stashx, self.stashy = self.get_stash(location)
                    
                    # Check if stash is not empty
                    if self.stash[self.stashy][self.stashx] != 0 :
                    
                        # Delete target from current location
                        self.you.remove(target)
                    
                        # Insert new star system at specific position
                        self.insertpos = (len(self.universe)-2) * (self.players[player]-1) + 1
                        self.universe.insert(self.insertpos, [[location], [], []])
                    
                        # Remove new star from stash
                        self.stash[self.stashy][self.stashx] -= 1
                    
                        # Actual move action
                        move_path(self.insertpos)
                    
                    else :
                        # Throw Error
                        self.error("Star not in stash")
                    
            else :
                # Throw Error
                self.error("No valid location, must be system ID or new star")



    def action_trade(self, player, sysid, target, trade) :
    
        # Shorten list names
        try :
            self.star = self.universe[sysid][0]
            self.you = self.universe[sysid][self.players[player]]
        except IndexError :
            self.error("Star system not existing")
            return None
        
        # Check if action can be executed
        if self.check_turn(player) and self.check_item("b", self.star, self.you) and self.check_item(target, self.you) :
        
            # Check if trade is valid
            if target[0] == trade[0] and target[1] != trade[1] :
            
                # Pick stashes
                self.stashtarget = self.get_stash(target)
                self.stashtrade = self.get_stash(trade)
                
                # Check if stash is not empty
                if self.stash[self.stashtrade[1]][self.stashtrade[0]] != 0 :
                
                    # Remove target and return it to stash
                    self.you.remove(target)
                    self.stash[self.stashtarget[1]][self.stashtarget[0]] += 1
                    
                    # Take trade from stash and append it to your fleet
                    self.you.append(trade)
                    self.stash[self.stashtrade[1]][self.stashtrade[0]] -= 1
                    
                    # Swap turns
                    self.next_turn(player)
                
                else :
                    # Throw Error
                    self.error("Ship not in stash")
            
            else :
                # Throw Error
                self.error("The ship you want to trade needs the same size but different color")



    def action_catastrophe(self, player, sysid) :
    
        # Shorten list names
        try :
            self.star = self.universe[sysid][0]
            self.you = self.universe[sysid][self.players[player]]
            self.opponent = self.universe[sysid][self.players[self.other(player)]]
        except IndexError :
            self.error("Star system not existing")
            return None
        
        
        # Generator that checks the system for possible catastrophes and yields the overpopulated colors
        def check_overpopulation() :
        
            for color in self.colors :
                if str(self.universe[sysid]).count(color) >= 4 :
                    yield color
        
        # Checks if element is affected from catastrophe and returns it to the stash if so
        def stasher(color, element) :
        
            if color in element :
            
                self.stashx, self.stashy = self.get_stash(element)
                self.stash[self.stashy][self.stashx] += 1
                return False
                
            else :
            
                return True
        
        
        # For every overpopulated color in the system
        for overpop in check_overpopulation() :
            
            # List comprehension removes overpopulated colors
            self.universe[sysid] = [ [ element for element in self.universe[sysid][section] if stasher(overpop, element) ] for section in range(len(self.universe[sysid])) ]
            self.send("A catastrophe has wiped out '{}' in system {}!".format(overpop, sysid))
            
        # If no star is left
        if not self.star :
        
            # If system is no homeworld
            if sysid not in (0, len(self.universe)-1) :
            
                # Return all elements in it to the stash
                for section in self.universe[sysid] :
                    for element in section :
                        self.stashx, self.stashy = self.get_stash(element)
                        self.stash[self.stashy][self.stashx] += 1
                
                # Delete the star system
                del(self.universe[sysid])
            
        # Don't change the turn, but print the board and check for finished game
        self.next_turn(self.other(player))
    
    
    
    def action_sacrifice(self, player, sysid, target) :
    
        # Shorten list names
        try :
            self.star = self.universe[sysid][0]
            self.you = self.universe[sysid][self.players[player]]
            self.opponent = self.universe[sysid][self.players[self.other(player)]]
        except IndexError :
            self.error("Star system not existing")
            return None
        
        # Check if action can be executed
        if self.check_turn(player) and self.check_item("x", "xoxo#yolo") and self.check_item(target, self.you) :
        
            # Set actioncounter and executable color
            self.actioncounter = int(target[0])
            self.executable = (target[1],)
            
            # Return sacrificed target to stash
            self.stashx, self.stashy = self.get_stash(target)
            self.stash[self.stashy][self.stashx] += 1
            
            self.send("You gain {} action(s).".format(self.actioncounter))
            self.you.remove(target)



    def action_waive(self, player) :
    
        # If the player has the turn
        if self.check_turn(player) :
        
            # Waive and pass the turn
            self.send("{} waived.".format(player))
            self.next_turn(player)



    def send(self, msg) :
        self.send_bag.append(msg)

    def error(self, msg) :
        self.error_bag.append(msg)

    def collect_sends(self) :
        for msg in range(len(self.send_bag)) :
            yield self.send_bag.pop(0)

    def collect_errors(self) :
        for msg in range(len(self.error_bag)) :
            yield self.error_bag.pop(0)


