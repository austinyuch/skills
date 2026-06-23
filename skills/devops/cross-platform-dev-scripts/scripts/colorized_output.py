import sys
import ctypes


class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"


def enable_windows_colors():
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def print_colored(text, color):
    print(f"{color}{text}{Colors.RESET}")


if __name__ == "__main__":
    enable_windows_colors()

    print_colored("✅ 成功訊息", Colors.GREEN)
    print_colored("❌ 錯誤訊息", Colors.RED)
    print_colored("⚠️  警告訊息", Colors.YELLOW)
    print_colored("ℹ️  資訊訊息", Colors.BLUE)
