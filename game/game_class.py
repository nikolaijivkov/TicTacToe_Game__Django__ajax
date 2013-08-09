from random import randint
from time import sleep
import os
class TicTacToe(object):  #game class with bot logic and win_lost check inside
    def __init__(self, board=None):
        self.win_combos=['000102', '101112', '202122', '001020', '011121', '021222', '001122', '021120']

        if board:
            self.board=board
        else:
            self.board={
                '0':{'0':None, '1':None, '2':None},
                '1':{'0':None, '1':None, '2':None},
                '2':{'0':None, '1':None, '2':None},
            }
        
        self.home = 'X'
        self.away = 'O'
        self.win_lost = None

    def empty_slots_check(self):
        empty_slots=[]  #make empty list
        empty_generator = (i+j for i in self.board for j in self.board[i] if self.board[i][j]== None)  #make generator object for empty slots
        empty_slots.extend(empty_generator) #add values from empty_generator to the list
        empty_slots.sort()  #sort list just in case
        return empty_slots

    def win_lost_check(self, home=None, away=None):
        if not home: home=self.home
        if not away: away=self.away

        if(self.win_lost==None):
            for combo in self.win_combos:  #check all win_combos for match
                a, b, c = combo[0:2], combo[2:4], combo[4:6]
                if( self.board[a[0]][a[1]]!=None and (self.board[a[0]][a[1]] == self.board[b[0]][b[1]] == self.board[c[0]][c[1]])): #3 fields from win_combo has the same sign and that sign is not None
                    if(self.board[a[0]][a[1]]==self.home): #sign match home team -> win
                        self.win_lost='win'
                        return True
                    elif(self.board[a[0]][a[1]]==self.away): #sign match away team -> lost
                        self.win_lost='lost'
                        return True
                    else:
                        raise Exception('Sign does not match home or away signs! This should never happen!')
            if( len(self.empty_slots_check())==0):  #no more empty fields on the board -> tie
                self.win_lost='tie'
                return True
            else:
                return False  #no match found -> continue the game
        else:
            return True  #self.win_lost not None -> self.win_lost must be win, lost, or tie

    def bot_move(self, sign="O"):
        empty_slots=self.empty_slots_check() #get list of empty slots 
        
        if( len(empty_slots)):  #empty slots have found
            choice = empty_slots[randint(0,len(empty_slots)-1)]  #random choice of one of the empty slots
            
            self.board[choice[0]][choice[1]]=sign
            
            self.win_lost_check()  #make win_lost_check() to set win_lost variable for next move
        else:  #no empty slots -> tie
            self.win_lost='Tie'

"""
    #part of previous console version
    def player_move(self, sign="X"):
        empty_slots=self.empty_slots_check() #get list of empty slots

        if(len(empty_slots)):
            while 1:
                choice = str(raw_input("Enter one of above: ")) #random choice of one of many empty slots
                if(choice in empty_slots): break

            self.board[choice[0]][choice[1]]=sign

            self.win_lost_check()
        else:
            self.win_lost='Tie'
#"""