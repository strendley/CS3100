# game options/settings
TITLE = "Blackjack +/- Grading Edition"
FULLSCREEN = True
SCALE = 0.5
CARD_SCALE = 0.4
WIDTH = int(1920 * SCALE)
HEIGHT = int(1080 * SCALE)
CARD_WIDTH = int(216 * CARD_SCALE)
CARD_HEIGHT = int(314 * CARD_SCALE)
FPS = 30

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (192, 192, 192)

GRAVITY = 9.8

HAND_PLACEMENT = {
    0:(int(0.42 * WIDTH), int(0.14 * HEIGHT)),
    1:(int(0.42 * WIDTH), int(0.64 * HEIGHT)),
    2:(int(0.17 * WIDTH), int(0.64 * HEIGHT)),
    3:(int(0.67 * WIDTH), int(0.64 * HEIGHT))
}

SCORE_PLACEMENT = {
    0:(int(0.5 * WIDTH), int(0.1 * HEIGHT)),
    1:(int(0.5 * WIDTH), int(0.51 * HEIGHT)),
    2:(int(0.25 * WIDTH), int(0.51 * HEIGHT)),
    3:(int(0.75 * WIDTH), int(0.51 * HEIGHT))
}
