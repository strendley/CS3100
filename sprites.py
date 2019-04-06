import pygame as pg
from attr import *
import random

suits = ['clubs', 'diamonds', 'hearts', 'spades']
names = list(range(2, 11)) + ['ace', 'jack', 'queen', 'king']

class Player(pg.sprite.Sprite):
    def __init__(self, name, num):
        pg.sprite.Sprite.__init__(self)
        self.name = name
        self.num = num
        self.cash = 1900
        self.PotAmount = 100
        self.hand = []
        self.pressedhit = False
        self.holding = False
        self.busted = False
        self.image = pg.Surface([0,0])
        self.rect = self.image.get_rect()
        self.rect.topleft = HAND_PLACEMENT[self.num]
        self.playing = True
    
    def reset(self):
        self.hand = []
        self.pressedhit = False
        self.holding = False
        self.playing = True

    def getPoints(self):
        amt = 0
        for card in self.hand:
            amt += card.value
        return amt
    
    def PlayerWon(self):
        self.cash = self.cash + (self.PotAmount * 2)
        self.cash = self.cash - 100
        self.PotAmount = 100
        self.playing = False

    def PlayerLost(self):
        self.cash = self.cash - 100
        self.PotAmount = 100
        self.playing = False

    def PlayerHit21(self):
        self.cash = self.cash + (self.PotAmount * 2.5) 
        self.cash = self.cash - 100
        self.PotAmount = 100   
        self.playing = False        

    def drawHand(self):
        new_width = (CARD_WIDTH + (len(self.hand) * 25))
        new_height = (CARD_HEIGHT + ((len(self.hand) / 5) * 10))
        self.image = pg.Surface([new_width, new_height], pg.SRCALPHA, 32).convert_alpha()
        xPos = 0
        yPos = 0
        cardCount = 0
        for card in self.hand:
            cardCount+=1
            pos = (xPos, yPos)
            self.image.blit(card.image, pos)
            xPos += 15
            if cardCount == 5:
                cardCount = 0
                yPos+=15
                xPos=0

    def update(self):
        #redraw the updated hand with new cards etc.
        self.drawHand()


class Card(pg.sprite.Sprite):
    def __init__(self, suit, name):
        pg.sprite.Sprite.__init__(self)

        #game-logic stuff
        self.suit = suit
        self.name = name
        self.color = 'red' if suit == 'diamonds' or suit == 'hearts' else 'black'
        self.value = self.getValue(name)
        
        #pygamestuff
        self.image = pg.image.load('img/cards/' + str(self.name) + '_of_' + self.suit + '.png').convert_alpha()
        self.image = pg.transform.smoothscale(self.image, (CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect()

    def getValue(self, name):
        value = 0
        if name == 'ace':
            value = 11
        elif name == 'jack' or name == 'queen' or name == 'king':
            value = 10
        else:
            value = int(name)
        # Red is worth negative
        if self.color == 'red':
            value = value * -1
        return value


class Deck(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.deck = self.gen()
        self.image = pg.image.load('img/cards/card_back.jpg')
        self.image = pg.transform.smoothscale(self.image, [CARD_WIDTH, CARD_HEIGHT])
        self.rect = self.image.get_rect()
        self.shuffle()

    def deal(self, player, amt):
        print("%s has been dealt %s card(s)" % (player.name, amt))
        if len(self.deck) == 0:
            print("RESTOCKED THE DECK!")
            self.deck = self.gen()
            random.shuffle(self.deck)
        for i in range(amt):
            player.hand.append(self.deck.pop())

    def shuffle(self):
        random.shuffle(self.deck)
    
    def gen(self):
        return [Card(suit,name) for suit in suits for name in names]
