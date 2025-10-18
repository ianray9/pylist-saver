class Colors:
    def __init__(self):
        self.green = "\033[32m"
        self.bold_green = "\033[1;32m"
        self.red = "\033[31m"
        self.reset = "\033[0m"
        self.yellow = "\033[33m"

    def set_color(self, text: str, color: str) -> str:
        color_code = getattr(self, color.lower(), "")
        print(f"{color_code}")
        print(f"{self.reset}")
        return f"{color_code}{text}{self.reset}"
