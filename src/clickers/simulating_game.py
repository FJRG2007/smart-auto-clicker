import time, keyboard
from threading import Timer

class GameSimulator:
    def __init__(self, root, button):
        self.root = root
        self.simulating_game = False
        self.simulate_game_button = button
        self.simulate_game_button.config(command=self.toggle_simulation)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        print("Window is closing.")
        self.root.quit()

    def toggle_simulation(self):
        if not self.simulating_game:
            self.simulating_game = True
            self.simulate_game_button.config(text="Stop Simulating")
            self.start_simulation()
        else:
            self.simulating_game = False
            self.simulate_game_button.config(text="Simulate Playing")

    def start_simulation(self):
        if self.simulating_game:
            self.simulate_keys()
            Timer(10, self.start_simulation).start()

    def simulate_keys(self):
        sequence = ["w", "s", "a", "d"]
        for i in range(len(sequence)):
            key = sequence[i]
            keyboard.press(key)
            time.sleep(1)
            keyboard.release(key)
            if key == "w": sequence[i] = "s"
            elif key == "s": sequence[i] = "w"
            elif key == "a": sequence[i] = "d"
            elif key == "d": sequence[i] = "a"