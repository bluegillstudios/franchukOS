import turtle
import random
import time

class SpaceInvaders:
    # Constants
    FRAME_RATE = 30  # Frames per second
    TIME_FOR_ONE_FRAME = 1 / FRAME_RATE  # Seconds

    CANNON_STEP = 10
    LASER_LENGTH = 20
    LASER_SPEED = 20
    ALIEN_SPAWN_INTERVAL = 1.2  # Seconds
    ALIEN_SPEED = 3.5

    def __init__(self):
        # Score
        self.score = 0
        self.score_display = turtle.Turtle()
        self.score_display.penup()
        self.score_display.hideturtle()
        self.score_display.color("white")
        self.score_display.goto(-200, 200)
        self.score_display.write("Score: 0", align="left", font=("Arial", 16, "normal"))

        self.window = turtle.Screen()
        self.window.tracer(0)
        self.window.setup(0.5, 0.75)
        self.window.bgcolor(0.2, 0.2, 0.2)
        self.window.title("Space Invaders v2.55")

        self.LEFT = -self.window.window_width() / 2
        self.RIGHT = self.window.window_width() / 2
        self.TOP = self.window.window_height() / 2
        self.BOTTOM = -self.window.window_height() / 2
        self.FLOOR_LEVEL = 0.9 * self.BOTTOM
        self.GUTTER = 0.025 * self.window.window_width()

        # Create laser cannon
        self.cannon = turtle.Turtle()
        self.cannon.penup()
        self.cannon.color(1, 1, 1)
        self.cannon.shape("square")
        self.cannon.setposition(0, self.FLOOR_LEVEL)
        self.cannon.cannon_movement = 0  # -1, 0 or 1 for left, stationary, right

        self.lasers = []
        self.aliens = []

        # Bind key events
        self.window.listen()
        self.window.onkeypress(self.move_left, "Left")
        self.window.onkeypress(self.move_right, "Right")
        self.window.onkey(self.stop_cannon_movement, "Up")
        self.window.onkeypress(self.create_laser, "space")

        self.run_game()

    def draw_cannon(self):
        self.cannon.clear()
        self.cannon.turtlesize(1, 4)  # Base
        self.cannon.stamp()
        self.cannon.sety(self.FLOOR_LEVEL + 10)
        self.cannon.turtlesize(1, 1.5)  # Next tier
        self.cannon.stamp()
        self.cannon.sety(self.FLOOR_LEVEL + 20)
        self.cannon.turtlesize(0.8, 0.3)  # Tip of cannon
        self.cannon.stamp()
        self.cannon.sety(self.FLOOR_LEVEL)

    def move_left(self):
        self.cannon.cannon_movement = -1

    def move_right(self):
        self.cannon.cannon_movement = 1

    def stop_cannon_movement(self):
        self.cannon.cannon_movement = 0

    def create_laser(self):
        laser = turtle.Turtle()
        laser.penup()
        laser.color(1, 0, 0)
        laser.hideturtle()
        laser.setposition(self.cannon.xcor(), self.cannon.ycor())
        laser.setheading(90)
        # Move laser to just above cannon tip
        laser.forward(20)
        # Prepare to draw the laser
        laser.pendown()
        laser.pensize(5)
        self.lasers.append(laser)

    def move_laser(self, laser):
        laser.clear()
        laser.forward(self.LASER_SPEED)
        # Draw the laser
        laser.forward(self.LASER_LENGTH)
        laser.forward(-self.LASER_LENGTH)

    def create_alien(self):
        alien = turtle.Turtle()
        alien.penup()
        alien.turtlesize(1.5)
        alien.setposition(
            random.randint(
                int(self.LEFT + self.GUTTER),
                int(self.RIGHT - self.GUTTER),
            ),
            self.TOP,
        )
        alien.shape("turtle")
        alien.setheading(-90)
        alien.color(random.random(), random.random(), random.random())
        self.aliens.append(alien)

    def remove_sprite(self, sprite, sprite_list):
        sprite.clear()
        sprite.hideturtle()
        self.window.update()
        sprite_list.remove(sprite)
        turtle.turtles().remove(sprite)

    def run_game(self):
        alien_timer = 0
        game_timer = time.time()
        game_running = True
        while game_running:
            timer_this_frame = time.time()

            time_elapsed = time.time() - game_timer
            # Move cannon
            new_x = self.cannon.xcor() + self.CANNON_STEP * self.cannon.cannon_movement
            if self.LEFT + self.GUTTER <= new_x <= self.RIGHT - self.GUTTER:
                self.cannon.setx(new_x)
                self.draw_cannon()
            # Move all lasers
            for laser in self.lasers.copy():
                self.move_laser(laser)
                # Remove laser if it goes off screen
                if laser.ycor() > self.TOP:
                    self.remove_sprite(laser, self.lasers)
                    break
                # Check for collision with aliens
                for alien in self.aliens.copy():
                    if laser.distance(alien) < 20:
                        self.remove_sprite(laser, self.lasers)
                        self.remove_sprite(alien, self.aliens)
                        self.score += 1
                        self.score_display.clear()
                        self.score_display.write("Score: " + str(self.score), align="left", font=("Arial", 16, "normal"))
                        break
            # Spawn new aliens when time interval elapsed
            if time.time() - alien_timer > self.ALIEN_SPAWN_INTERVAL:
                self.create_alien()
                alien_timer = time.time()

            # Move all aliens
            for alien in self.aliens:
                alien.forward(self.ALIEN_SPEED)
                # Check for game over
                if alien.ycor() < self.FLOOR_LEVEL:
                    game_running = False
                    break

            time_for_this_frame = time.time() - timer_this_frame
            if time_for_this_frame < self.TIME_FOR_ONE_FRAME:
                time.sleep(self.TIME_FOR_ONE_FRAME - time_for_this_frame)
            self.window.update()

        splash_text = turtle.Turtle()
        splash_text.hideturtle()
        splash_text.color(1, 1, 1)
        turtle.write("GAME OVER", font=("Courier", 40, "bold"), align="center")

        turtle.done()