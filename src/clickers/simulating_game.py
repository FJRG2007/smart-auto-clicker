import time, keyboard
from threading import Thread

class GameSimulator:
    def __init__(self, root, button):
        self.root = root
        self.simulating_game = False
        self.simulate_game_button = button
        self.simulate_game_button.config(command=self.toggle_simulation)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        print("Window is closing.")
        self.simulating_game = False
        self.root.quit()

    def toggle_simulation(self):
        if not self.simulating_game:
            self.simulating_game = True
            self.simulate_game_button.config(text="Stop Simulating")
            self.simulation_thread = Thread(target=self.start_simulation)
            self.simulation_thread.start()
        else:
            self.simulating_game = False
            self.simulate_game_button.config(text="Simulate Playing")

    def start_simulation(self):
        while self.simulating_game:
            self.simulate_keys()
            time.sleep(10)

    def simulate_keys(self):
        sequence = ["w", "s", "a", "d"]
        for i in range(len(sequence)):
            if not self.simulating_game: break
            key = sequence[i]
            keyboard.press(key)
            time.sleep(1)
            keyboard.release(key)
            if key == "w": sequence[i] = "s"
            elif key == "s": sequence[i] = "w"
            elif key == "a": sequence[i] = "d"
            elif key == "d": sequence[i] = "a"