# IMPORTS
import pyxel, random

# VARS

def circular(n, min, max):
    """
    Loop a given n number until it's in the inclusive interval. Return calibrated number.
    """
    d = max - min + 1
    while n < min:
        n += d
    while n > max:
        n -= d

    return n

def border(n, min=None, max=None):
    """
    Restrict a given number n in a "border" inclusive interval. Returns calibrated number.
    """
    if min is not None and n < min:
        n = min
    elif max is not None and n > max:
        n = max

    return n
"""
# TESTS - Restrict to
n = 5; min = 0; max = 10 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
n = -1; min = 0; max = 10 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
n = 11; min = 0; max = 10 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
n = 4; min = 1; max = 3 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
"""

class Game:
    def __init__(self, title, x=256, y=256, fps=30, name='', v=2, size=8, vx=4, spf=2):
        # Init game board
        self.xx = x     ### X maX
        self.yx = y     ### Y maX
        self.xn = 0     ### X miN
        self.yn = 0     ### Y miN
        self.fps = fps
        self.title = title
        self.timer = 0          ### DEPREC - Better use pyxel.frame_count
        self.shots_tot = 0

        pyxel.init(self.xx, self.yx, title=self.title, fps=self.fps)

        # Init player
        self.xmov = 0
        self.ymov = 0
        self.vais = Player(self.xx/2 - size/2, self.yx/2 - size/2, name=name, v=v, size=size, vx=vx, spf=spf)

        # Init shot list
        self.shots_l = []

        # Launch the game, each frames per second
        print(f"GAME - Initialized {self.title} with x length = {self.xx}, y length = {self.yx} at {self.fps}fps")
        pyxel.run(self.update, self.draw)

    def __str__(self):
        return f"GAME - Running {self.title} with x length = {self.xx}, y length = {self.yx} at {self.fps}fps"

    def txt_main(self):
        self.tx = 10
        self.ty = 10
        self.tcol = 1
        self.txts_main = ["# Pyxel Game",
                          "title: " + self.title + "; fps: " + str(self.fps),
                          "size: x=" + str(self.xx) + ", y=" + str(self.yx),
                          "time: frames=" + str(pyxel.frame_count) + ", secs=" + str(round(pyxel.frame_count / self.fps, 1)),
                          "player: " + self.vais.name,
                          "pos: x=" + str(int(self.vais.x)) + ", y=" + str(int(self.vais.y)),
                          "stats: size=" + str(self.vais.size) + ", spf=" + str(self.vais.spf),
                          "velocity: actual=" + str(round(self.vais.v, 2)) + ", max=" + str(self.vais.vx),
                          "shots: active=" + str(len(self.shots_l)) + ", total=" + str(self.shots_tot), # "per-sec=" + str(round(len(self.shots_l) / (self.timer / self.fps), 1))
                          "---"]

        for txt in self.txts_main:
            pyxel.text(self.tx, self.ty, txt, self.tcol)
            self.ty += 6

    def input_player(self):
        """
        User basic input
        """
        # Menus
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        # Move. TODO correct wall collision system
        if pyxel.btn(pyxel.KEY_RIGHT) and self.vais.x < self.xx - self.vais.size:
            self.xmov = 1
        if pyxel.btn(pyxel.KEY_DOWN) and self.vais.y < self.yx - self.vais.size:
            self.ymov = 1
        if pyxel.btn(pyxel.KEY_LEFT) and self.vais.x > 0:
            self.xmov = -1
        if pyxel.btn(pyxel.KEY_UP) and self.vais.y > 0:
            self.ymov = -1
        # Shoot
        if pyxel.btn(pyxel.KEY_SPACE) and pyxel.frame_count % self.vais.spf == 0: ### Limit to 1 shot per 2 frame
            #print("DEBUG - Player shot")
            self.shots_tot += 1
            self.shots_l.append(Shot(self, self.vais.x + int(self.vais.size/2), self.vais.y - 6, w=2))

    def input_debug(self):
        """
        Debug user inputs
        """
        # Reset pos
        if pyxel.btn(pyxel.KEY_O):
            self.vais.x = self.xx/2 - self.vais.size/2
            self.vais.y = self.yx/2 - self.vais.size/2

        # Change velocity
        if pyxel.btn(pyxel.KEY_Z) and self.vais.v > 0:
            self.vais.v -= 1
        elif pyxel.btn(pyxel.KEY_X):
            self.vais.v += 1
        # Change size
        if pyxel.btn(pyxel.KEY_C) and self.vais.size > 0:
            self.vais.size -= 1
        elif pyxel.btn(pyxel.KEY_V) and self.vais.size < 256:
            self.vais.size += 1



    """
    UPDATER
    """
    def update(self):
        # Timer. DEPREC - use pyxel.frame_count
        self.timer += 1

        # Input controls
        self.input_player()
        # Debug controls
        self.input_debug()
        # Movement calc
        self.vais.move(self.xmov, self.ymov)
        self.xmov = 0
        self.ymov = 0
        # Shots
        for shot in self.shots_l:
            shot.move()

    """
    DRAWER
    """
    def draw(self):
        # Start fresh each time
        pyxel.cls(0)

        # Text
        self.txt_main()
        # Shots
        for shot in self.shots_l:
            shot.draw()
        # Ship, draw a rectangle
        self.vais.draw()


class Player:
    def __init__(self, x, y, name='', size=8, v=2, vx=4, spf=2):
        self.x = x
        self.y = y
        self.name = name
        self.size = size
        self.v = v              ### Actual velocity
        self.vx = vx            ### MaX accelerated Velocity
        self.xshift = 0
        self.yshift = 0
        # self.acct = 0           ### Timer in frames since last x movement
        # self.accty = 0          ### Timer in frames since last y movement
        self.spf = spf          ### Shot per frame
        self.cardMean = [0, 0, 0, 0]

    def move(self, x, y):
        """
        Shift the vessel in the direction of x and y normalized vector {-1, 0, 1} time the velocity
        """
        """
        # Inertia (basic: omnidirectional fn); increase linear
        self.m = 0.05
        if (x != 0 or y != 0) and self.v <= self.vx:
            self.v += self.m
        elif self.v > 0:
            self.v -= self.m
        else:
            self.v = 0
        """


        self.v = border(self.v, 0, self.vx)

        # Calc movement vector
        self.xshift = x * self.v
        self.yshift = y * self.v
        # Move
        self.x += self.xshift
        self.y += self.yshift


    def draw(self):
        pyxel.rect(self.x, self.y, self.size, self.size, 4)

class Shot:

    def __init__(self, game, x, y, w=2, h=8, v=2, team='WIP'):
        self.x = x
        self.y = y
        self.w = w          ### Width
        self.h = h          ### Height
        self.v = v          ### Velocity
        self.GAME = game    ### Actual gameboard
        # print("SHOT - Shot created; game recorded", self.GAME)

    def __str__(self):
        return f"SHOT - x={self.x}, y={self.y}, w={self.w}, h={self.h}, v={self.v}"

    def move(self):
        ## Here only one dir, up
        self.y -= self.v
        if self.y < self.GAME.yn - self.h + 1:
            self.GAME.shots_l.remove(self)
            # print("SHOTS - Shot deleted (out of bounds). List now:", self.GAME.shots_l)

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 10)

# EXEC

print("GAME - Started")
GAME = Game('Game1', 256, 256, name='Detroix23')
print("GAME - Finished")