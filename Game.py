import pygame as pg
from sys import exit
from attr import *
from sprites import *
from math import cos, sin, sqrt
import random
from random import randrange
import time

class Game:
    def __init__(self):
        # Initialize pygame
        pg.init()
        pg.mixer.init()
        
        # Plays background music
        pg.mixer.music.load('Music/Quirky-Puzzle-Game-Menu.mp3')
        pg.mixer.music.set_volume(0.25)
        pg.mixer.music.play(-1)
        self.music_playing = True
            
        # Creates the main SDL_SURFACE game window to blit an draw onto
        if FULLSCREEN:
            self.screen = pg.display.set_mode([WIDTH, HEIGHT], pg.HWSURFACE | pg.DOUBLEBUF | pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode([WIDTH, HEIGHT], pg.HWSURFACE | pg.DOUBLEBUF)

        # Customize the process
        pg.display.set_caption(TITLE)
        pg.display.set_icon(pg.image.load('img/icon.png'))
        
        # FPS Clock to keep the game running at the same rate even when waiting on keyevents, or loading data etc.
        self.clock = pg.time.Clock()
        
        # Needed game variables
        self.cont = True # keeps the game cycles ticking
        self.difficulty = 0 # 0 easy, 1 med, 2 hard
        self.playersAmt = 1 # 1-3
        self.buttons = {} # List of loaded buttons for the current screen to be checked for clicks

        # Loads the background surfaces
        self.background = pg.image.load('img/table.png')
        self.background = pg.transform.smoothscale(self.background, (WIDTH, HEIGHT))
        self.rect = self.background.get_rect()
        
        self.background_clear = pg.image.load('img/table_clear.png')
        self.background_clear = pg.transform.smoothscale(self.background_clear, (WIDTH, HEIGHT))

    # Starts a new game
    def new(self):
        # Sprite groups
        self.players = pg.sprite.Group()
        self.dealer = pg.sprite.Group()
        self.deck = Deck()
        self.GameOver = False
        
        # Make players
        for i in range(1, self.playersAmt + 1):
            playerObj = Player('Player %s' % i, i)
            self.players.add(playerObj)
        
        # Stores the player for the current turn
        self.playerObj = self.players.sprites()[0]
        
        # Make dealer
        self.dealerObj = Player('Dealer', 0)
        self.dealer.add(self.dealerObj)
    
        # Begin
        self.start()
    
    def start(self):
        # Clear old hands and deal cards
        for p in self.players.sprites():
            p.reset()
            self.deck.deal(p, 2)
        
        self.dealerObj.reset()
        self.deck.deal(self.dealerObj, 2)
        self.deck = Deck() #make sure the deck is randomized on start/restart
        # Start the game cycle
        self.run()
    
    # allows the player to continue the match after win/loss
    def progress(self):
        self.cont = True
        self.start()

    
    # wipes the balance
    def restart(self):
        self.cont = True
        self.new()

    # game cycle with events, player status, and screen updates
    def run(self):
        while self.cont:
            self.dt = self.clock.tick(FPS)
            self.events()
            self.draw()
            self.update()
            
            # Pauses the game if all players have won/loss
            pause = True
            for p in self.players.sprites():
                if p.playing:
                    pause = False
            if pause:
                self.cont = False
                self.hold_on_input()
            if self.GameOver == True:
                self.hold_on_input()

    def dealerAI(self):
        # base the AI on the player with the closest points to winning
        closestPlayer = self.playerObj
        closestPlayerPts = 21 - abs(closestPlayer.getPoints())
        for p in self.players.sprites():
            points = 21 - (abs(p.getPoints()))
            if (points < closestPlayerPts and p.busted == False) or closestPlayer.busted == True:
                closestPlayer = p
        print("AI is running based on player: " + p.name + " with points " + str(closestPlayer.getPoints()))
        
        #if both players bust, just have the dealer hold regardless of difficulty
        if closestPlayer.busted == True:
            self.dealerObj.holding = True
            return

        #if the difficulty is easy, the dealer will make random, legal moves.
        if self.difficulty == 0:
            rand = randrange(0,10)
            if rand <= 7:
                if self.dealerObj.holding == False:
                    self.play_sound('card.wav')
                    self.deck.deal(self.dealerObj, 1)
            else:
                self.dealerObj.holding = True

        
        #if the difficult is medium, the dealer will make smart moves.
        elif self.difficulty == 1:
            dealerPoints = 21 - abs(self.dealerObj.getPoints())
            playerPoints = 21 - abs(closestPlayer.getPoints())
            if playerPoints >= dealerPoints:
                self.dealerObj.holding = True
            else:
                if self.dealerObj.holding == False:
                    self.play_sound('card.wav')
                    self.deck.deal(self.dealerObj, 1)

        #if the difficult is hard, the dealer will attempt to cheat
        elif self.difficulty == 2:
            dealerPoints = 21 - abs(self.dealerObj.getPoints())
            dealerScore = self.dealerObj.getPoints() 
            playerPoints = 21 - abs(closestPlayer.getPoints())       

            if dealerPoints > 7 and dealerPoints > playerPoints:
                if self.dealerObj.holding == False:
                    self.play_sound('card.wav')
                    self.deck.deal(self.dealerObj, 1)
            elif dealerPoints > playerPoints:
                #create a stacked deck for the dealer
                self.stacked_deck = []
                #if the dealer's points are negative, get closer to -21
                if self.dealerObj.getPoints() < 0:
                    print(len(self.deck.deck))
                    while len(self.deck.deck) != 0:
                        #if the card is not red, it won't help us get closer to -21
                       # print("val of first card: %s" % (self.deck.deck[0].value))
                        print ("dealer score + card: %s" % (abs(self.deck.deck[0].value + dealerScore)))
                        if self.deck.deck[0].color != 'red':
                            #discard it
                            self.deck.deck.remove(self.deck.deck[0])
                        #if the card in the front of the list will result in a greater score than the player
                        #as well as remain under 21, add it to the dealer's stacked deck
                        elif (abs(self.deck.deck[0].value + dealerScore) >= playerPoints) and (abs(self.deck.deck[0].value + dealerScore) <= 21):
                            print("val of card: %s" % (self.deck.deck[0].value))
                            print ("new dealer score: %s" % (self.deck.deck[0].value + dealerScore))
                            self.stacked_deck.append(self.deck.deck[0])
                            self.deck.deck.remove(self.deck.deck[0])   
                        #if the card won't increase the score, discard it
                        else:
                            self.deck.deck.remove(self.deck.deck[0])   
                    #if the stacked deck is not empty, draw a card from it
                    if len(self.stacked_deck) != 0:
                        random.shuffle(self.stacked_deck)
                        self.dealerObj.hand.append(self.stacked_deck.pop())
                    #if the stacked deck is empty, just hold for now
                    else:
                        print("stacked deck is empty negative")
                        self.dealerObj.holding = True
                                       
                #if the dealer's points are positive, get closer to +21
                elif self.dealerObj.getPoints() > 0:
                    print(len(self.deck.deck))
                    while len(self.deck.deck) != 0:
                        #if the card is red, it won't help us get closer to +21
                        if self.deck.deck[0].color == 'red':
                            #discard it
                            self.deck.deck.remove(self.deck.deck[0])   
                        #if the card in the front of the list will result in a greater score than the player
                        #as well as remain under 21, add it to the dealer's stacked deck
                        elif (abs(self.deck.deck[0].value + dealerScore) >= playerPoints) and (abs(self.deck.deck[0].value + dealerScore) <= 21):
                            print("val of card: %s" % (self.deck.deck[0].value))
                            print ("new dealer score: %s" % (self.deck.deck[0].value + dealerScore))
                            self.stacked_deck.append(self.deck.deck[0])
                            self.deck.deck.remove(self.deck.deck[0])   
                        #if the card won't increase the score, discard it
                        else:
                            self.deck.deck.remove(self.deck.deck[0])   
                    
                    #if the stacked deck is not empty, draw a card from it
                    if len(self.stacked_deck) != 0:
                        random.shuffle(self.stacked_deck)
                        self.dealerObj.hand.append(self.stacked_deck.pop())
                    #if the stacked deck is empty, just hold for now
                    else:
                        print("stacked deck is empty positive")
                        self.dealerObj.holding = True
            #if the dealer's score is already better than the player's, just hold
            else:
                self.dealerObj.holding = True

        #provide a small delay
        self.dealer.update()
        self.draw()
        time.sleep(1)
    
    def onWin(self, player):
        self.draw_text_shadow("WON!", 'monospace', 40, GREEN, SCORE_PLACEMENT[player.num][0], SCORE_PLACEMENT[player.num][1] + 150, True)
        self.draw_text_shadow("Press ENTER to Continue", 'monospace', 40, WHITE, int(WIDTH / 2), int(HEIGHT / 2.3), True)
        playerPoints = 21 - (abs(player.getPoints()))
        if playerPoints == 21:
            player.PlayerHit21()
        else:
            player.PlayerWon()
        pg.display.flip() # display text
    
    def onLoss(self, player):
        self.draw_text_shadow("LOST!", 'monospace', 40, RED, SCORE_PLACEMENT[player.num][0], SCORE_PLACEMENT[player.num][1] + 150, True)
        self.draw_text_shadow("Press ENTER to Continue", 'monospace', 40, WHITE, int(WIDTH / 2), int(HEIGHT / 2.3), True)
        player.PlayerLost()
        pg.display.flip() # display text
    
    def update(self):
        self.players.update()
        self.dealer.update()
                
        # check win/loss status o all players
        for p in self.players.sprites():
            # handle win/loss and dealer hits

            if abs(self.dealerObj.getPoints()) > 21:
                #if self.GameOver == False:
                 #   self.GameOver = True
                
                if p.busted == False:
                    self.onWin(p)
                else:
                    self.onLoss(p)
                # closestPlayer = self.playerObj
                # closestPlayerPts = 21 - abs(closestPlayer.getPoints())
                # points = 21 - (abs(p.getPoints()))
                # if (points < closestPlayerPts and p.busted == False) or closestPlayer.busted == True:
                #     closestPlayer = p
                
                # self.onWin(closestPlayer)

                # if p != closestPlayer:
                #     self.onLoss(p)
            # dealer is not holding and everyone else is, do AI
            elif self.dealerObj.holding == False:
                allHolding = True
                for p in self.players.sprites():
                    if not p.holding:
                        allHolding = False
                if allHolding:
                    self.dealerAI()
            # both are holding, closest to -21 or +21 is the winner
            elif (self.dealerObj.holding == True) and (p.holding == True):
                dealerPoints = 21 - abs(self.dealerObj.getPoints())

                for p in self.players.sprites():
                    playerPoints = 21 - abs(p.getPoints())

                    if (p.getPoints() == 21 or p.getPoints == -21) and dealerPoints != 0:
                        self.onWin(p, True) #player hit 21

                    elif playerPoints < dealerPoints and p.busted == False:
                        self.onWin(p)
                    
                    else:
                        self.onLoss(p)

                # closestPlayer = self.playerObj
                # closestPlayerPts = 21 - abs(closestPlayer.getPoints())
                # for p in self.players.sprites():
                #     points = 21 - (abs(p.getPoints()))
                #     if (points < closestPlayerPts and p.busted == False) or closestPlayer.busted == True:
                #         closestPlayer = p
                
                #     if (points < closestPlayerPts and p.busted == False) or closestPlayer.busted == True:
                #         closestPlayer = p

                #     if (points > dealerPoints) or (points == dealerPoints) or (p.busted == True) or (points != closestPlayerPts):
                #         self.onLoss(p)
                        
                #     elif (points < dealerPoints) or (points == 0) or (points == closestPlayerPts):
                #         self.onWin(p)
                        

    def events(self):
        for event in pg.event.get():
            # handle quit
            if event.type == pg.QUIT:
                self.cont = False
                self.showWinScreen = False
            # handle keypress
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.cont = False
                    self.showWinScreen = False
                if event.key == pg.K_g:
                    self.end_screen()
                
            # handle button clicks
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos # get mouse position
                # loop over stored buttons
                for text, rect in self.buttons.items():
                    if rect.collidepoint(mouse_pos):
                        self.play_sound('ui_click.wav')
                        # chip click
                        if text.startswith('chip_'):
                            self.play_sound('chip.wav')
                            amt = int(text.split('_')[1][1:]) # ex: chip_$50
                            
                            # increase bet (left click)
                            if event.button == 1:
                                if self.playerObj.cash - amt >= 0 and self.playerObj.pressedhit != True:
                                   self.playerObj.cash -= amt
                                   self.playerObj.PotAmount += amt
                            # deincrease bet (right click)
                            if event.button == 3:
                                if self.playerObj.PotAmount - amt >= 0 and self.playerObj.pressedhit != True:
                                    self.playerObj.cash += amt
                                    self.playerObj.PotAmount -= amt
                        # check for button text and do actions
                        elif text == 'Hit':
                            self.play_sound('card.wav')
                            time.sleep(0.15) # sync card audio to animation
                            self.playerObj.pressedhit = True
                            if self.playerObj.holding == False:
                                self.deck.deal(self.playerObj, 1)
                            if abs(self.playerObj.getPoints()) > 21:
                                self.playerObj.busted = True
                                self.playerObj.holding = True
                                self.playerObj = self.players.sprites()[self.playerObj.num % self.playersAmt]

                            if abs(self.playerObj.getPoints()) == 21:
                                self.playerObj.holding = True
                                self.playerObj = self.players.sprites()[self.playerObj.num % self.playersAmt]
                                
                        elif text == 'Hold':
                            self.playerObj.pressedhit = True
                            if self.playerObj.holding != True:
                                self.playerObj.holding = True
                            # next player's turn
                            self.playerObj = self.players.sprites()[self.playerObj.num % self.playersAmt]
                        elif text == 'Back':
                            self.buttons = {} # clear buttons for new screen
                            self.menu_screen()
                        elif text == 'Mute':
                            self.mute_music()    

    def draw(self):
        self.screen.blit(self.background_clear, [0,0])
        self.players.draw(self.screen)
        self.dealer.draw(self.screen)
        
        self.draw_text("Pot: " + str(self.playerObj.PotAmount), 'monospace', 26, WHITE, 185, 60)
        self.make_chip_button(self.screen, 'red', YELLOW, 60*1 + 30, 80, 60, '$25')
        self.make_chip_button(self.screen, 'blue', YELLOW, 60*2 + 35, 80, 60, '$100')
        self.make_chip_button(self.screen, 'black', YELLOW, 60*3 + 40, 80, 60, '$500')
        self.draw_text("Left +, Right -", 'monospace', 20, WHITE, 185, 165)

        self.make_button(self.screen, GRAY, BLACK, WIDTH - 265,40,150,50, 'Hit')
        self.make_button(self.screen, GRAY, BLACK, WIDTH - 265,100,150,50, 'Hold')
        self.make_button(self.screen, GRAY, BLACK, 20, HEIGHT - 60, 70, 40, 'Back')
        self.make_button(self.screen, GRAY, BLACK, 100, HEIGHT - 60, 70, 40, "Mute")

        self.draw_text("Dealer Hand: " + str(self.dealerObj.getPoints()), 'monospace', 22, WHITE, SCORE_PLACEMENT[0][0], SCORE_PLACEMENT[0][1], True)
        
        if self.dealerObj.holding == True:
            self.draw_text("(HOLDING)", 'monospace', 26, WHITE, SCORE_PLACEMENT[0][0], SCORE_PLACEMENT[0][1] - 25)
        
        for p in self.players.sprites():
            self.draw_text(p.name, 'monospace', 22, WHITE, SCORE_PLACEMENT[p.num][0], SCORE_PLACEMENT[p.num][1], p == self.playerObj) # Bold if current turn
            self.draw_text("Hand: " + str(p.getPoints()), 'monospace', 22, WHITE, SCORE_PLACEMENT[p.num][0], SCORE_PLACEMENT[p.num][1] + 25)
            self.draw_text("$" + str(p.cash), 'monospace', 22, WHITE, SCORE_PLACEMENT[p.num][0], SCORE_PLACEMENT[p.num][1] + 50)

            if p.holding == True:
                if abs(p.getPoints()) > 21:
                    self.draw_text("(BUSTED)", 'monospace', 26, WHITE, SCORE_PLACEMENT[p.num][0], SCORE_PLACEMENT[p.num][1] - 25)
                else:
                    self.draw_text("(HOLDING)", 'monospace', 26, WHITE, SCORE_PLACEMENT[p.num][0], SCORE_PLACEMENT[p.num][1] - 25)

        pg.display.flip()

    def draw_text(self, text, font, size, color, xCoord, yCoord, bold=False):
        sys_font = pg.font.SysFont(font, size, bold)
        surface = sys_font.render(text, True, color)
        surface_rect = surface.get_rect(**{'center': (xCoord, yCoord)})
        self.screen.blit(surface, surface_rect)

    def draw_text_shadow(self, text, font, size, color, xCoord, yCoord, bold=False):
        offset = 6
        if size <= 40:
            offset = 3
        self.draw_text(text, font, size, BLACK, xCoord + offset, yCoord + offset, bold)
        self.draw_text(text, font, size, color, xCoord, yCoord, bold)

    def options_screen(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.background, [0,0])

        self.make_button(self.screen, GRAY, BLACK, 375,int(HEIGHT * 0.8),200,50, 'Back')

        self.draw_text("Difficulty", 'Arial Black', 20, WHITE, 480, 170)
        self.make_button(self.screen, (GREEN if self.difficulty == 0 else GRAY), BLACK, 375,190,200,40, 'Easy')
        self.make_button(self.screen, (GREEN if self.difficulty == 1 else GRAY), BLACK, 375,240,200,40, 'Medium')
        self.make_button(self.screen, (GREEN if self.difficulty == 2 else GRAY), BLACK, 375,290,200,40, 'Hard')
        
        self.draw_text("Players", 'Arial Black', 20, WHITE, 480, 350)
        self.make_button(self.screen, (GREEN if self.playersAmt == 1 else GRAY), BLACK, 375,370,60,40, '1')
        self.make_button(self.screen, (GREEN if self.playersAmt == 2 else GRAY), BLACK, 445,370,60,40, '2')
        self.make_button(self.screen, (GREEN if self.playersAmt == 3 else GRAY), BLACK, 515,370,60,40, '3')

        pg.display.flip()
        # wait for clicks
        clicked = False
        while not clicked:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos # get mouse position
                    # loop over stored buttons
                    for text, rect in self.buttons.items():
                        if rect.collidepoint(mouse_pos):
                            self.play_sound('ui_click.wav')
                            clicked = True
                            self.buttons = {} # clear buttons for new screen
                            if text == 'Easy':
                                self.difficulty = 0
                                self.options_screen()
                            elif text == 'Medium':
                                self.difficulty = 1
                                self.options_screen()
                            elif text == 'Hard':
                                self.difficulty = 2
                                self.options_screen()
                            elif text == '1':
                                self.playersAmt = 1
                                self.options_screen()
                            elif text == '2':
                                self.playersAmt = 2
                                self.options_screen()
                            elif text == '3':
                                self.playersAmt = 3
                                self.options_screen()
                            elif text == 'Back':
                                self.menu_screen()

    def objective_screen(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.background, [0,0])

        self.make_button(self.screen, GRAY, BLACK, 375,int(HEIGHT * 0.8),200,50, 'Back')

        self.draw_text("Objective:", 'monospace', 50, WHITE, WIDTH / 2, int(HEIGHT * 0.4))
        self.draw_text("Red Cards are NEGATIVE Points.", 'monospace', 20, RED, WIDTH / 2, HEIGHT / 2, True)
        self.draw_text("Black cards are POSITIVE Points.", 'monospace', 20, BLACK, WIDTH / 2, int(HEIGHT * 0.55), True)
        self.draw_text("The player must decide whether to hit or hold.", 'monospace', 20, WHITE, WIDTH / 2,int(HEIGHT * 0.60))
        self.draw_text("The closest to -21 or 21 without busting wins!", 'monospace', 20, WHITE, WIDTH / 2,int(HEIGHT * 0.65))

        pg.display.flip()
        # wait for clicks
        clicked = False
        while not clicked:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos # get mouse position
                    # loop over stored buttons
                    for text, rect in self.buttons.items():
                        if rect.collidepoint(mouse_pos):
                            self.play_sound('ui_click.wav')
                            clicked = True
                            self.buttons = {} # clear buttons for new screen
                            if text == 'Back':
                                self.menu_screen()

    def menu_screen(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.background, [0,0])
        
        self.make_button(self.screen, GRAY, BLACK, 375,200,200,50, 'Play')
        self.make_button(self.screen, GRAY, BLACK, 375,260,200,50, 'Objective')
        self.make_button(self.screen, GRAY, BLACK, 375,320,200,50, 'Options')
        self.make_button(self.screen, GRAY, BLACK, 375,int(HEIGHT * 0.8),200,50, 'Quit')

        pg.display.flip()
        # wait for clicks
        clicked = False
        while not clicked:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos # get mouse position
                    # loop over stored buttons
                    for text, rect in self.buttons.items():
                        if rect.collidepoint(mouse_pos):
                            self.play_sound('ui_click.wav')
                            clicked = True
                            self.buttons = {} # clear buttons for new screen
                            if text == 'Play':
                                self.new()
                            if text == 'Continue':
                                self.progress()
                            elif text == 'Objective':
                                self.objective_screen()
                            elif text == 'Options':
                                self.options_screen()
                            elif text == 'Quit':
                                self.quit()

    def make_chip_button(self, surface, image, text_color, x, y, size, amount):
        chip = pg.image.load('img/chips/' + image + '.png')
        chip = pg.transform.smoothscale(chip, (size, size))
        chip_rect = chip.get_rect()
        chip_rect = chip_rect.move(x, y)
        self.screen.blit(chip, chip_rect)
        myfont = pg.font.SysFont('Arial Black', 18) #creates the font
        text = myfont.render(amount, 1, text_color) #creates the label
        text_rect = text.get_rect(center = chip_rect.center)
        self.screen.blit(text, text_rect) #places label over button
        self.buttons['chip_' + amount] = chip_rect #store button in global variable for event checks
    
    def make_button(self, surface, color, text_color, x, y, w, h, text):
        button = pg.Rect(x, y, w, h)
        pg.draw.rect(surface, BLACK, button, 1) #creates black outline
        pg.draw.rect(surface, color, button) #creates button rectangle
        myfont = pg.font.SysFont('Arial Black', 20) #creates the font
        label = myfont.render(text, 1, text_color) #creates the label
        text_rect = label.get_rect(center = button.center)
        self.screen.blit(label,text_rect) #places label over button
        self.buttons[text] = button #store button in global variable for event checks

    def play_sound(self, file, volume=0.75):
        sound = pg.mixer.Sound('Music/' + file)
        sound.set_volume(volume)
        sound.play()

    def mute_music(self):
        if self.music_playing == False:
            pg.mixer.music.unpause()
            self.music_playing = True
        elif self.music_playing == True:
            pg.mixer.music.pause()
            self.music_playing = False    

    def end_screen(self):
        surf = pg.image.load('img/cards/gosnell_joker.png')
        surf = pg.transform.smoothscale(surf, [CARD_WIDTH, CARD_HEIGHT])
        surfRect = surf.get_rect()
        surfRect.topleft = [10,200]
        gravity = -15
        xVel = 10
        yVel = 20
        TIME_DELTA = 1
        while self.end_match_event():
            TIME_DELTA += (self.clock.tick(FPS) / 1000)
            surfRect.left += (xVel * TIME_DELTA * cos(30))
            surfRect.top += (yVel * TIME_DELTA * sin(30) - (0.5 * gravity * (TIME_DELTA * TIME_DELTA)))
            if (not (self.rect.contains(surfRect))):
                if (surfRect.bottom > HEIGHT or surfRect.top < 0):
                    yVel*=-.98
                elif (surfRect.right > WIDTH or surfRect.left < 0):
                    xVel *= -random.uniform(0.95, 1.2)
                surfRect = surfRect.clamp(self.rect)
                TIME_DELTA = sqrt(TIME_DELTA)
            self.screen.blit(surf, surfRect)
            pg.display.flip()

    # returns false if they hit a key to restart or progress
    def end_match_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.GameOver = False

                    for p in self.players.sprites():
                        p.busted = False
                    
                    self.progress()
                else:
                    self.GameOver = False

                    for p in self.players.sprites():
                        p.busted = False

                    self.restart()
                return False
        return True

    def hold_on_input(self):
        pg.event.wait()
        while self.end_match_event():
            pass

    def quit(self):
        pg.quit()
        exit()
