# IMPORTS
import pyxel, random, math

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

def strr(r):
    """
    Stringify from int and round
    """
    return lambda i : str(round(i, int(r)))

str2 = strr(2)
str1 = strr(1)

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
    def __init__(self, title, x=256, y=256, fps=30,                             ### Default world
                 name='', size=8, vx=4.0, spf=2, pvn=0.0, pvx=0.5, pvs=0.1, psdec=0.0, psv=2.0,      ### Player
                 pdrag=0.0, borders='hard', bounce=0.0                          ### Phys
                 ):

        # Init logs
        self.Logs = [{'t': 0, 'msg': 'Logs initialized'}] ## List of {Timer in frames, Log}

        # Init game board
        self.xx = x     ### X maX
        self.yx = y     ### Y maX
        self.xn = 0     ### X miN
        self.yn = 0     ### Y miN
        self.fps = fps
        self.title = title
        self.shots_tot = 0
        self.param = {'borders': borders,
                      'pdrag': pdrag,
                      'bounce': bounce,
                      'pVn': pvn,       ### Player Velocity miN
                      'pVx': pvx,       ### Player Velocity maX
                      'pSdec': psdec,   ### Player Shoot DECeleration
                      'pSv': psv
                      }
        self.ins = {'m': pvs           ### player power slider force
                    }
        self.locks = {
                    'shoot': False
                    }

        pyxel.init(self.xx, self.yx, title=self.title, fps=self.fps)
        self.Logs.append({'t': 0, 'msg': 'Game initialized'})

        # Init player
        self.xmov = 0
        self.ymov = 0
        self.vais = Player(self, name=name, size=size, vx=vx, spf=spf, drag=pdrag, bounce=bounce, pvn=pvn, pvx=pvx, pvs=pvs, psdec=psdec)

        # Init shot list
        self.shots_p = []

        # Init enemies
        self.enemies = []
        ## DEBUG - Test
        self.enemies.append(Enemy(self, 100, 100, direction=(0, -1), v=1, size=10, behaviour={'type': 'claws'}))

        # Init Timers
        self.timer = 0          ### DEPREC - Better use pyxel.frame_count
        self.delays = {}
        self.delay_new('inp_lockAttack', 6)

        # Init text
        ## Fixed
        self.tx = 10
        self.ty = 10
        self.tcol = 1
        self.txts_main = ()
        ## Temp
        self.txts_temp = []

        # Launch the game, each frames per second
        print(f"GAME - Initialized {self.title} with x length = {self.xx}, y length = {self.yx} at {self.fps}fps")
        pyxel.run(self.update, self.draw)
        self.Logs.append({'t': 0, 'msg': 'Game launched'})

    def __str__(self):
        return f"GAME - Running {self.title} with x length = {self.xx}, y length = {self.yx} at {self.fps}fps"

    def txt_main(self):
        self.txts_main = (
            "# Pyxel Game - title: " + self.title + "; borders=" + self.param['borders'] + ", fps=" + str(self.fps),
            "size: x=" + str(self.xx) + ", y=" + str(self.yx),
            "time: frames=" + str(pyxel.frame_count) + ", secs=" + str(round(pyxel.frame_count / self.fps, 1)),
            "player: " + self.vais.name,
            "pos: x=" + str(int(self.vais.x)) + ", y=" + str(int(self.vais.y)),
            "stats: size=" + str(self.vais.size) + ", spf=" + str(self.vais.spf),
            "velocity: max=" + str(self.vais.v['max']) + ", min=" + str(self.vais.v['min']) + ", absolute=" + str2(self.vais.absV),
            "accel: power=" + str2(self.vais.m) + ", air-drag=" + str2(self.vais.drag['air']) + ", bounce=" + str(self.vais.bounce * 100) + "%",
            "cardinal-v: y=" + str1(self.vais.shift['y']) + ", x=" + str1(self.vais.shift['x']),
            "shots: active=" + str(len(self.shots_p)) + ", total=" + str(self.shots_tot),
            # "per-sec=" + str(round(len(self.shots_p) / (self.timer / self.fps), 1))
            "---")
        for txt in self.txts_main:
            pyxel.text(self.tx, self.ty, txt, self.tcol)
            self.ty += 6
        self.ty = 10

    def txt_temp_new(self, x, y, id, txt='No text', time=10.0, col=16, dn=None, dx=None):
        self.delay_new("in-brake", dn, dx)  ### Create if delays doesnt already exists
        if self.delay_check(id):
            self.delay_use(id)
            self.txts_temp.append({'txt': txt, 'time': time, 'x': x, 'y': y, 'color': col})

    def txt_temp_update(self):
        for txt in self.txts_temp:
            txt['time'] -= 1
            if txt['time'] <= 0:
                self.txts_temp.remove(txt)

    def txt_temp_draw(self):
        for txt in self.txts_temp:
            pyxel.text(txt['x'], txt['y'], txt['txt'], txt['color'])

    # DELAYS
    def delay_new(self, delay_id, delay_min, delay_max=None, cx=None, autoUse=False):
        """
        Create a new delay in ticks
        """
        state = False
        if delay_id not in self.delays and delay_min is not None:
            self.delays[delay_id] = {'t': 0, 'dn': delay_min, 'dx': delay_max, 'cx': cx, 'c': 0, 'autoUse': autoUse}
            state = True
        return state

    def delay_check(self, delay_id, debug=False):
        """
        Check delay time. Return False if in cooldown, True if not, and None if non existant
        """
        if delay_id in self.delays:
            if debug:
                print("DELAYS - Time:", self.delays[delay_id]['t'])
            if self.delays[delay_id]['t'] > self.delays[delay_id]['dn']:
                auth = True
            else:
                auth = False
        else:
            auth = None

        return auth

    def delay_use(self, delay_id):
        """
        Reset delay to zero, even if cooldown not ready
        """
        self.delays[delay_id]['t'] = 0

    def delay_update(self):
        """
        Update delays' timer
        """
        """
        ## Iterate with a manual copy
        delaysUpdate = self.delays
        for id in self.delays:
            delaysUpdate[id]['t'] += 1
            if delaysUpdate[id]['dx'] is not None:
                if delaysUpdate[id]['t'] <= delaysUpdate[id]['dx']:
                    del delaysUpdate[id]
        ## Update new delays from delays that existed (old)
        self.delays = delaysUpdate
        """
        for delay_id in self.delays:
            self.delays[delay_id]['t'] += 1
            if self.delays[delay_id]['dx'] is not None:
                if self.delays[delay_id]['t'] <= self.delays[delay_id]['dx']:
                    del self.delays[delay_id]
            if self.delays[delay_id]['autoUse'] and self.delays[delay_id]['t'] >= self.delays[delay_id]['dn']:
                self.delay_use(delay_id)

    ## Fixed delays
    ### cf Constructor



    def input_player(self):
        """
        User basic input
        """
        # Menus
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        # Move
        ## Brake
        if pyxel.btn(pyxel.KEY_P) or pyxel.btn(pyxel.KEY_CTRL):
            ### Smooth drag
            self.txt_temp_new(self.vais.cx - 6, self.vais.y - 8, id='in-brake', txt='BRAKE!', time=2, col=7, dn=0)
            self.vais.move_drag(self.vais.m)
        ## Directions
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.xmov = 1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.ymov = 1
        if pyxel.btn(pyxel.KEY_LEFT):
            self.xmov = -1
        if pyxel.btn(pyxel.KEY_UP):
            self.ymov = -1

        # Change power
        if pyxel.btn(pyxel.KEY_Z) and self.vais.m > self.vais.v['min']:
            ## Decrease
            self.vais.m -= self.ins['m']
        if pyxel.btn(pyxel.KEY_X) and self.vais.m < self.vais.v['max']:
            ## Increase
            self.vais.m += self.ins['m']

        # Shoot
        if pyxel.btn(pyxel.KEY_SPACE) and pyxel.frame_count % self.vais.spf == 0: ### Limit to 1 shot per spf frame
            #print("DEBUG - Player shot")
            self.vais.attack()
        ## Lock shoot
        if pyxel.btn(pyxel.KEY_C):
            if self.delay_check('inp_lockAttack'):
                self.delay_use('inp_lockAttack')
                self.locks['shoot'] = not self.locks['shoot']
            ### Then, check lock functions

    def input_debug(self):
        """
        Debug user inputs
        """
        # Reset pos
        if pyxel.btn(pyxel.KEY_O):
            self.vais.x = self.xx/2 - self.vais.size/2
            self.vais.y = self.yx/2 - self.vais.size/2
        # Cancel velocity
        if pyxel.btn(pyxel.KEY_P) and pyxel.btn(pyxel.KEY_SHIFT):
            ## Instant reset
            self.vais.shift['x'] = 0
            self.vais.shift['y'] = 0


        # Change size
        if pyxel.btn(pyxel.KEY_PAGEUP) and self.vais.size > 0:
            self.vais.size -= 1
        elif pyxel.btn(pyxel.KEY_PAGEDOWN) and self.vais.size < 256:
            self.vais.size += 1



    """
    UPDATER
    """
    def update(self):
        # Timer. DEPREC - use pyxel.frame_count
        self.timer += 1

        # Player
        ## Input controls
        self.input_player()
        # Debug controls
        self.input_debug()
        ## Movement calc
        self.vais.move(self.xmov, self.ymov)
        self.xmov = 0
        self.ymov = 0
        # Shots
        for shot in self.shots_p:
            shot.move()
        # Enemies
        for enemy in self.enemies:
            enemy.move_ai()

        # Text
        self.txt_temp_update()

        # Delays
        self.delay_update()

    """
    DRAWER
    """
    def draw(self):
        # Start fresh each time
        pyxel.cls(0)

        # Text fixed
        self.txt_main()
        # Text temp
        self.txt_temp_draw()
        # Ship, draw a rectangle
        self.vais.draw()
        self.vais.draw_vect(m=5)
        self.vais.draw_stats()
        # Shots
        for shot in self.shots_p:
            shot.draw()
        # Enemies
        for enemy in self.enemies:
            enemy.draw()



class Player:
    def __init__(self, game, name='', size=8, v=2, vx=4.0, spf=2, drag=0.0, v_limit=0, bounce=0.0, vvx=float('inf'),
                 pvn=0.0, pvx=0.5, pvs=0.05, psdec=0.005, startingMun=5000, startingLife=5):
        self.GAME = game
        self.x = (self.GAME.xx + size) / 2
        self.y = (self.GAME.yx + size) / 2
        self.name = name
        self.size = size
        self.cx = self.x + (self.size / 2)
        self.cy = self.y + (self.size / 2)
        self.v = {'min': pvn, 'max': pvx, 'slide-m': pvs}
        self.vvx = vvx              ### MaX Vector Velocity
        self.shift = {'x': 0.0, 'y': 0.0}   ### Speed vector for x, y
        self.dirs = {'x': 0.0, 'y': 0.0}    ### Normal vector to indicate direction
        # self.acct = 0             ### Timer in frames since last x movement
        # self.accty = 0            ### Timer in frames since last y movement
        self.spf = spf              ### Shot per frame
        self.cardV = [0, 0, 0, 0]   ### DEPREC - Mean of the 4 accel vector i, j, -i, -j clockwise
        self.m = 0.05               ### Linear factor, aka thruster power
        self.drag = {'air': drag, 'v-limit': v_limit}
        self.absV = 0               ### Absolute velocity
        self.bounce = bounce
        ### Combat
        self.shotDirs = (0, -1)
        self.munitions = startingMun
        self.life = startingLife
        ### Repr
        self.stats = {'x': self.GAME.xx - 10, 'y': self.GAME.yx + 10, 'h': (self.GAME.xx + 30) / 3, 'w': (self.GAME.yx + 20) / 10}

    def center_update(self):
        ## Update center
        self.cx = self.x + (self.size / 2)
        self.cy = self.y + (self.size / 2)
        return self.cx, self.cy

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
        # Locks
        self.locks_actions()
        # Inertia (cardinal); linear prop
        self.dirs['x'] = x
        self.dirs['y'] = y
        ## Increase (thruster on)
        self.shift['y'] += self.dirs['y'] * self.m
        self.shift['x'] += self.dirs['x'] * self.m
        ## Limit in void (dust I guess ?)
        ### WIP
        # print("PLAYER - Thrusters ON: x= " + str(self.dirs['x']) + ", y= " + str(self.dirs['y']))

        ## Air drag
        self.move_drag(self.drag['air'])

        ## Limit
        self.shift['y'] = border(self.shift['y'], -self.vvx, self.vvx)
        self.shift['x'] = border(self.shift['x'], -self.vvx, self.vvx)

        # Move
        self.absV = math.sqrt(self.shift['x'] ** 2 + self.shift['y'] ** 2)
        self.x += self.shift['x']
        self.y += self.shift['y']
        ## Update center
        self.center_update()
        ## Check borders
        if self.GAME.param['borders'] == 'tor':
            self.y = circular(self.y, 0 - self.size, self.GAME.yx)
            self.x = circular(self.x, 0 - self.size, self.GAME.xx)
        else:
            ### Collision with wall + bounce
            if self.y > self.GAME.yx - self.size:
                self.y = self.GAME.yx - self.size
                self.shift['y'] = self.shift['y'] * -self.bounce
            elif self.y < 0:
                self.y = 0
                self.shift['y'] = self.shift['y'] * -self.bounce
            if self.x > self.GAME.xx - self.size:
                self.x = self.GAME.xx - self.size
                self.shift['x'] = self.shift['x'] * -self.bounce
            elif self.x < 0:
                self.x = 0
                self.shift['x'] = self.shift['x'] * -self.bounce

        ## Simply movement
        if 0.01 > self.shift['x'] > -0.01:
            self.shift['x'] = 0
        if 0.01 > self.shift['y'] > -0.01:
            self.shift['y'] = 0

    def move_drag(self, drag):
        drag = drag * (self.size / 8)
        if drag != 0 and (self.shift['y'] != 0 or self.shift['x'] != 0):
            if self.shift['y'] > 0:
                self.shift['y'] -= self.absV * drag
            elif self.shift['y'] < 0:
                self.shift['y'] += self.absV * drag
            if self.shift['x'] > 0:
                self.shift['x'] -= self.absV * drag
            elif self.shift['x'] < 0:
                self.shift['x'] += self.absV * drag

    def draw(self):
        pyxel.rect(self.x, self.y, self.size, self.size, 4)

    def draw_vect(self, m=4):
        """
        Draw forces on the player
        """
        # Inertia (y, x)
        pyxel.line(self.cx, self.cy, self.cx, self.cy + (self.shift['y'] * m), col=9)
        pyxel.line(self.cx, self.cy, self.cx + (self.shift['x'] * m), self.cy, col=9)
        #print("PLAYER - vect shift x: ", self.cx, self.cy, self.cx + (self.shift['x'] * m), self.cy)
        # Thrusters (y, x)
        pyxel.line(self.cx, self.cy, self.cx, self.cy + (self.dirs['y'] * self.m * m * 10), col=10)
        pyxel.line(self.cx, self.cy, self.cx + (self.dirs['x'] * self.m * m * 10), self.cy, col=10)

    def draw_stats(self):
        # Stats
        ## Life
        pyxel.rectb(self.stats['x'], self.stats['y'] + self.stats['h'], self.stats['w'], self.stats['h'], col=8)

    def attack(self):
        self.GAME.shots_tot += 1
        ## Fix the not moving point shots
        if tuple(self.dirs.values()) != (0, 0):
            self.shotDirs = tuple(self.dirs.values())
        self.GAME.shots_p.append(Shot(self.GAME, self.GAME.shots_p, self.cx, self.cy, direction=self.shotDirs, w=2,
                                      v=self.GAME.param['pSv'], decel=self.GAME.param['pSdec']))

    def locks_actions(self):
        """
        Effect of all toggled action
        """
        if self.GAME.locks['shoot']:
            self.attack()

class Enemy:
    types = [
        '',
        'claws'
    ]
    def __init__(self, game, x, y, direction, v=1, size=10, behaviour=None, col=7, startingLife=5):
        self.GAME = game
        self.x = x
        self.y = y
        self.col = col
        self.size = size
        self.behave = behaviour or {'type': 'claws'}
        self.type = behaviour['type']
        self.direction = [direction[0], direction[1]]
        self.v = v
        self.delay_retreat = 0
        self.life = startingLife

        if self.type == 'claws':
            self.claw = {'lim': random.randint(20, 80), 'dw': 0, 'stage': 'attacking'}

    def perish(self):
        self.GAME.enemies.remove(self)

    def move(self):
        self.x += self.direction[0] * self.v
        self.y += self.direction[1] * self.v
    def move_ai(self):
        if self.type == 'claws':
            ## Advance til a limit, then wait and go back
            if self.claw['stage'] == 'attacking':
                if self.claw['dw'] >= self.claw['lim']:
                    self.claw['stage'] = 'waiting'
                self.move()
                self.claw['dw'] += 1

            elif self.claw['stage'] == 'waiting':
                self.delay_retreat = self.GAME.delay_check(self)
                #print("ENEMY - Delay check: " + str(self.delay_retreat))
                if self.delay_retreat is None:
                    ### Start a timer
                    self.GAME.delay_new(self, 180, None, 1)
                    print("ENEMY - New timer; waiting fleeing")
                elif self.delay_retreat is False:
                    pass
                elif self.delay_retreat is True:
                    ### Turn when timer's off
                    self.GAME.delay_use(self)
                    self.direction[0] = -self.direction[0]
                    self.direction[1] = -self.direction[1]
                    self.claw['stage'] = 'fleeing'

            else:   ## self.claw['stage'] == 'fleeing'
                self.move()
                self.claw['dw'] -= 1
                if self.claw['dw'] < 0:
                    ### Loop to original pos
                    self.perish()

        else:
            ## Incorrect type
            self.perish()

    def draw(self):
        pyxel.rect(self.x, self.y, self.size, self.size, 4)



class Shot:

    def __init__(self, game, team, x, y, w=2, h=8, v=2, direction=(0, -1), decel=0.0):
        self.x = x
        self.y = y
        self.yOld = y
        self.xOld = x
        self.w = w          ### Width
        self.h = h          ### Height
        self.v = v          ### Velocity
        self.decel = decel  ### Deceleration
        self.GAME = game    ### Actual gameboard
        self.team = team
        self.direction = direction          ### Normalized vector
        self.lifet = self.GAME.fps * 8      ### Life span in ticks
        # print("SHOT - Shot created; game recorded", self.GAME)

    def __str__(self):
        return f"SHOT - x={self.x}, y={self.y}, w={self.w}, h={self.h}, v={self.v}"

    def move(self):
        # Move and collisions
        ## Vector movement
        ### Save old position
        self.xOld = self.x
        self.yOld = self.y
        ### Update them
        self.x += self.direction[0] * self.v
        self.y += self.direction[1] * self.v

        ## Check collisions
        if self.GAME.param['borders'] == 'tor':
            self.y = circular(self.y, 0 - self.h, self.GAME.yx)
            self.x = circular(self.x, 0 - self.w, self.GAME.xx)
        ### Hard border and other
        else:
            if self.x < self.GAME.xn or self.x > self.GAME.xx or self.y < self.GAME.yn or self.y > self.GAME.yx:
                self.perish()
            # print("SHOTS - Shot deleted (out of bounds). List now:", self.GAME.shots_p)
        ## Update lifespan
        self.lifet -= 1
        if self.lifet < 0:
            self.perish()

        ## Deceleration
        self.v = self.v - self.v * self.decel

        ## Simplify
        ### Simply velocity
        if 0.02 > self.v:
            self.v = 0

    def draw(self):
        """
        Draws the shot, multiple method tested
        """
        # Line with width
        """
        for l in range(self.w):
            shift = l + (self.w / 2)
            pyxel.line(self.x - shift, self.y, self.x - shift, self.y + self.h, col=10)
        """
        # Vector speed
        """
        pyxel.line(self.xOld, self.yOld, self.x, self.y, col=10)
        """
        # True shot (with height)
        pyxel.line(self.x, self.y, self.x + self.h * self.direction[0], self.y + self.h * self.direction[1], col=10)

    def perish(self):
        self.GAME.shots_p.remove(self)


# EXEC
if __name__ == "__main__":
    launch_mode = 'Classic'
    #launch_mode = 'Function testing'

    if launch_mode == 'Classic':
        print("GAME - Started")
        GAME = Game('Game1', 256, 256, fps=60, borders='hard',                    ### World
                    name='Detroix23', pvn=0.05, pvx=0.15, pvs=0.005, psdec=0.010, psv=3.5,          ### Player
                    vx=float('inf'), pdrag=0.01, bounce=0.95                                ### Physics
                    )
        print("GAME - Finished")

    elif launch_mode == 'Function testing':
        print("FT - Started")