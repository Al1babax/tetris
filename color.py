class Colors:
    def __init__(self):
        self.color_dict = {
            "orange": ("\033[1;30;48;5;208m", "\033[0m"),  # Bright orange background (custom), black foreground
            "red": ("\033[1;30;41m", "\033[0m"),           # Red background, black foreground
            "green": ("\033[1;30;48;5;46m", "\033[0m"),         # Green background, black foreground
            "yellow": ("\033[1;30;48;5;226m", "\033[0m"),       # Bright yellow background, black foreground
            "blue": ("\033[1;30;48;5;39m", "\033[0m"),          # Blue background, black foreground
            "white": ("\033[1;30;107m", "\033[0m")         # Bright white background, black foreground
        }

        self.square_to_color = {
            "O": "orange",
            "R": "red",
            "G": "green",
            "Y": "yellow",
            "B": "blue",
            "W": "white"
        }

    def color_text(self, text, color):
        return f"{self.color_dict[color][0]}{text}{self.color_dict[color][1]}"