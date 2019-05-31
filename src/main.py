import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.core.audio import SoundLoader

import time


# Class that represents a paddle
class Paddle(Widget):
    score = NumericProperty(0)
    pong_sound = SoundLoader.load("sounds/pong_sound.wav")

    # Method that checks if a collision between the ball and this paddle happened
    # and changes the ball's velocity based on where the ball hit the paddle
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            offset = (ball.center_y - self.center_y) / (self.height/2)
            ball.x_velocity *= -1.15
            ball.y_velocity = (ball.y_velocity * 1.15) + offset
            self.pong_sound.play()

    # Method that sets this paddle's score to zero
    def reset_score(self):
        self.score = 0


# Class that represents a ball
class Ball(Widget):
    x_velocity = NumericProperty(0)
    y_velocity = NumericProperty(0)

    # Method that moves the x- and y-coordinates of the ball based on the velocities
    def move(self):
        self.pos[0] += self.x_velocity
        self.pos[1] += self.y_velocity


# Class that represents the area where the game happens
class PongArena(Widget):
    pass


# Class that represents the popup that comes up when the game ends
class EndOfGamePopup(Popup):
    # The winner at the end of the game
    winner = StringProperty("")


# Class that represents the popup that comes up when a player presses the pause button
class PausePopup(Popup):
    pass


# Class that represents the main menu
class MainMenuScreen(Screen):
    pass


# Class that represents the game screen
class GameScreen(Screen):
    player_left = ObjectProperty(None)
    player_right = ObjectProperty(None)
    ball = ObjectProperty(None)
    arena = ObjectProperty(None)
    winning_score = NumericProperty(10)

    # Method called when the game screen starts
    def on_enter(self, *args):
        self.start_game()

    # Method called when the game leaves
    def on_leave(self, *args):
        Clock.unschedule(self.update)

    # Method that puts the ball in the middle of the screen and sets the new speed
    def serve_ball(self, velocity=(4, 0)):
        self.ball.center = self.center
        self.ball.x_velocity = velocity[0]
        self.ball.y_velocity = velocity[1]

    # Method that redraws the screen and checks the position of the ball
    def update(self, dt):
        self.ball.move()

        self.player_left.bounce_ball(self.ball)
        self.player_right.bounce_ball(self.ball)

        if self.ball.y < self.y or self.ball.top > self.top:
            self.ball.y_velocity *= -1

        if self.ball.x < 0:
            self.player_right.score += 1
            self.serve_ball((-3, 0))
            time.sleep(1)
        elif self.ball.x + self.ball.width > self.width:
            self.player_left.score += 1
            self.serve_ball((3, 0))
            time.sleep(1)

        if self.player_left.score == self.winning_score:
            time.sleep(0.5)
            self.open_end_popup("LEFT PLAYER")
        elif self.player_right.score == self.winning_score:
            time.sleep(0.5)
            self.open_end_popup("RIGHT PLAYER")

    # Method that sets the paddle at their start positions, their score's to zero, serves the ball,
    # and schedule's the update method
    def start_game(self):
        self.player_left.x = self.arena.x
        self.player_left.center_y = self.arena.center_y
        self.player_right.x = self.arena.width - self.player_right.width
        self.player_right.center_y = self.arena.center_y

        self.player_left.reset_score()
        self.player_right.reset_score()

        self.serve_ball()
        Clock.schedule_interval(self.update, 1/60)

    # Method that opens the end of game popup and sets the winner
    def open_end_popup(self, winner):
        Clock.unschedule(self.update)
        popup = EndOfGamePopup()
        popup.winner = winner
        popup.open()

    # Method that opens the pause popup
    def open_pause_popup(self):
        Clock.unschedule(self.update)
        popup = PausePopup()
        popup.open()

    # Method that resumes the game from where it was paused
    def continue_game(self):
        Clock.schedule_interval(self.update, 1/60)

    # Method that reacts when the player's click and drag the paddles
    def on_touch_move(self, touch):
        if touch.x < self.width / 3 and \
                self.player_left.height / 2 + touch.y < self.top and touch.y - self.player_left.height / 2 > self.y:
            self.player_left.center_y = touch.y
        elif touch.x > self.width * (2 / 3) and \
                self.player_right.height / 2 + touch.y < self.top and touch.y - self.player_right.height / 2 > self.y:
            self.player_right.center_y = touch.y


# Class that represents the game
class PongApp(App):
    screen_manager = None

    # Method that builds the app
    def build(self):
        self.icon = "images/pong_icon.png"

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(MainMenuScreen(name="main_menu"))
        self.screen_manager.add_widget(GameScreen(name="game_screen"))

        return self.screen_manager


if __name__ == "__main__":
    pa = PongApp()
    pa.run()
