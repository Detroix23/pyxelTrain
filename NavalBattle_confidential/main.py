
# Nuit du c0de 2025

import pyxel

class Game:

    def __init__(self):
        # Base
        self.size = 256
        self.max_force = 2
        print("# Game init")
        pyxel.init(self.size, self.size, title="Bataille Navale", fps=30, quit_key=pyxel.KEY_ESCAPE)
        pyxel.load("3.pyxres")

        # Players
        self.players = {
            "Police": Player(self, "Police", 50, "zqsd"),
            "Pirate": Player(self, "Pirate", 240, "arrows")
        }

        # Shots
        self.shots = []

        # Run
        print("# Game to run")
        pyxel.run(self.update, self.draw)


    def player_inputs(self):
        if pyxel.btn(pyxel.KEY_Q) and not self.players["Police"].x_force < -self.max_force:
            self.players["Police"].x_force -= 0.1
        elif pyxel.btn(pyxel.KEY_D) and not self.players["Police"].x_force > self.max_force:
            self.players["Police"].x_force += 0.1
        if pyxel.btn(pyxel.KEY_S):
            self.players["Police"].angle += 1
        elif pyxel.btn(pyxel.KEY_Z):
            self.players["Police"].angle -= 1
        if pyxel.btnr(pyxel.KEY_SPACE):
            self.players["Police"].shoot()

        if pyxel.btn(pyxel.KEY_LEFT) and not self.players["Pirate"].x_force < -self.max_force:
            self.players["Pirate"].x_force -= 0.1
        elif pyxel.btn(pyxel.KEY_RIGHT) and not self.players["Pirate"].x_force > self.max_force:
            self.players["Pirate"].x_force += 0.1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.players["Pirate"].angle += 1
        elif pyxel.btn(pyxel.KEY_UP):
            self.players["Pirate"].angle -= 1
        if pyxel.btnr(pyxel.KEY_KP_0):
            self.players["Pirate"].shoot()


    def update(self):
        self.player_inputs()
        for player in self.players.values():
            #print(player)
            player.move()

        for shot in self.shots:
            #print(shot)
            shot.move()

    def draw(self):
        pyxel.cls(6)
        pyxel.rect(0 , 2 * self.size / 3, self.size, 2 * self.size / 2, col=5)

        for player in self.players.values():
            player.draw()

        for shot in self.shots:
            shot.draw()

class Player:
    def __init__(self, Game, name, position_x, keys):
        self.Game = Game
        self.name = name
        self.position_x = position_x
        self.position_y = 2 * self.Game.size / 3
        self.keys = keys
        self.life = 5
        self.x_force = 0
        if self.name == "Police":
            self.angle = 135
        else:
            self.angle = 310

        print(self.angle)

        self.size = 10
        self.bounce_factor = 3
        if self.keys == "zqsd":
            self.direction = 1
        else:
            self.direction = -1

    def __str__(self):
        return f"Player {self.name}- Pos: x={self.position_x}; Force: x={self.x_force}; Direction: {self.direction}"

    def draw(self):
        if self.name=="Police":
            pyxel.blt(self.position_x + 10, 2 * self.Game.size / 3 - self.size, 0, 16, 48, -16, -16, 2, self.angle)
            pyxel.blt(self.position_x, 2 * self.Game.size / 3 - self.size,0,0,16,16,16,2)
        else:
            pyxel.blt(self.position_x - 10, 2 * self.Game.size / 3 - self.size, 0, 0, 48, -16, 16, 2, self.angle)
            pyxel.blt(self.position_x, 2 * self.Game.size / 3 - self.size,0,0,32,16,16,2)


    def move(self):
        # Bouge
        self.position_x += self.x_force
        # Ralentissement
        self.x_force = self.x_force / 1.05
        # Rebondissment
        if self.position_x + self.size > self.Game.size:
            self.position_x = (self.Game.size - self.size) + self.bounce_factor * ((self.Game.size - self.size) - self.position_x)
            self.x_force = -self.x_force
        elif self.position_x < 0:
            self.position_x = -self.bounce_factor * self.position_x
            self.x_force = -self.x_force
        # Simplifer le mouvement
        if abs(self.x_force) < 0.001: self.x_force = 0

    def shoot(self):
        Shot(self.Game, self.angle, self.direction, self.name, (self.position_x, self.position_y))


class Shot:
    def __init__(self, Game, angle, direction, player, position=(0,0)):
        """
        @direction = -1 left, 1 right
        """
        self.Game = Game
        self.speed = 2.5
        self.player = player
        self.lifetime = 1
        self.position_initial = position
        self.position = position
        self.direction = direction
        self.angle = angle
        self.hitbox = 5
        self.Game.shots.append(self)

        #print(self.direction)

        self.acceleration_y = 1
        self.force = (
            pyxel.cos(self.angle),
            pyxel.sin(self.angle)
        )

    def __str__(self):
        return f"Shot - Lifetime={self.lifetime}; Position={self.position}"

    def draw(self):
        if self.player == "Police":
            pyxel.blt(self.position[0], self.position[1],0,0,64,16,16,2)
        else:
            pyxel.blt(self.position[0], self.position[1],0,0,80,16,16,2)

    def move(self):
        # Calc vecteur force
        self.force = (
            pyxel.cos(self.angle * self.direction),
            pyxel.sin(self.angle * self.direction)
        )
        # Movement réel

        self.position = (
            self.position[0] - self.force[0] * self.speed,
            self.position[1] - self.force[1] * self.speed
        )
        """
        self.position = (
            self.position_initial[0] + self.direction * self.lifetime,
            self.position_initial[1] - 1 * self.position[1] ** 1.01 + self.position[1]
        )
        """
        #self.position_initial[1] -1 * self.position[1] ** 2

        # Hors-bordures

        if self.position[0] < 0 or self.position[1] > self.Game.size or self.position[1] < 0 or self.position[1] > self.Game.size:
            self.perish()


        # Tourner
        self.angle = self.angle + 20 / self.lifetime ** 1
        # Vie
        self.lifetime += 1
        if self.lifetime > 512:
            self.perish()

        # Check hitbox
        for x in range(0, self.hitbox):
            for y in range(0, self.hitbox):
                if self.player == "Police" and self.Game.players["Pirate"].position_x == x and self.Game.players["Pirate"].position_y == y:
                    print("Police win")
                    #self.Game.players["Pirate"].perish()
                elif self.player == "Pirate" and self.Game.players["Police"].position_x == x and self.Game.players["Police"].position_y == y:
                    print("Pirate win")
                    #self.Game.players["Police"].perish()


    def perish(self):
        if self in self.Game.shots:
            self.Game.shots.remove(self)


# Start

Game = Game()


