import asyncio
import sys
from typing import Callable, Awaitable


class Colors: # testar com outros terminais sem ser o do vs code dps
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

USERNAME_COLORS = [
    Colors.BRIGHT_CYAN,
    Colors.BRIGHT_GREEN,
    Colors.BRIGHT_YELLOW,
    Colors.BRIGHT_MAGENTA,
    Colors.BRIGHT_BLUE,
    Colors.CYAN,
    Colors.GREEN,
    Colors.YELLOW,
]

class ColoredUI:
    def __init__(self):
        self.username_color_map = {}
        self.color_index = 0
    
    def get_username_color(self, username: str) -> str:
        if username not in self.username_color_map:
            self.username_color_map[username] = USERNAME_COLORS[
                self.color_index % len(USERNAME_COLORS)
            ]
            self.color_index += 1
        return self.username_color_map[username]
    
    def print_message(self, username: str, text: str, reprint_prompt: bool = True, prompt_username: str = None):
        color = self.get_username_color(username)
        print(f"\r{color}{Colors.BOLD}{username}{Colors.RESET}: {text}")
        if reprint_prompt and prompt_username:
            prompt_color = self.get_username_color(prompt_username)
            print(f"{prompt_color}{Colors.BOLD}{prompt_username}{Colors.RESET}: ", end="", flush=True)
        elif reprint_prompt:
            print("> ", end="", flush=True)
    
    def print_system(self, text: str, reprint_prompt: bool = True, prompt_username: str = None):
        print(f"\r{Colors.BRIGHT_BLACK}[system] {text}{Colors.RESET}")
        if reprint_prompt and prompt_username:
            prompt_color = self.get_username_color(prompt_username)
            print(f"{prompt_color}{Colors.BOLD}{prompt_username}{Colors.RESET}: ", end="", flush=True)
        elif reprint_prompt:
            print("> ", end="", flush=True)
    
    def print_prompt(self, username: str):
        color = self.get_username_color(username)
        print(f"{color}{Colors.BOLD}{username}{Colors.RESET}: ", end="", flush=True)
    
    def print_info(self, text: str):
        print(f"{Colors.BRIGHT_BLUE}{text}{Colors.RESET}")
    
    def print_error(self, text: str):
        print(f"{Colors.BRIGHT_RED}Error: {text}{Colors.RESET}", file=sys.stderr)
    
    def print_success(self, text: str):
        print(f"{Colors.BRIGHT_GREEN}{text}{Colors.RESET}")


async def input_loop(
    send: Callable[[str], Awaitable[None]],
    close: Callable[[], Awaitable[None]],
    ui: ColoredUI,
    username: str
):

    ui.print_info("\nCommands: /quit to exit, /help for help\n")
    
    while True:
        try:
            ui.print_prompt(username)
            text = await asyncio.to_thread(input)
            
            if text.strip() == "/quit":
                await send("[left the room]")
                await close()
                break
            
            elif text.strip() == "/help":
                print(f"\n{Colors.BRIGHT_CYAN}Available commands:{Colors.RESET}")
                print(f"  {Colors.YELLOW}/quit{Colors.RESET}  - Leave the chat room")
                print(f"  {Colors.YELLOW}/help{Colors.RESET}  - Show this help message\n")
                continue
            
            elif text.strip() == "":
                continue
            
            await send(text)
            
        except EOFError:
            await send("[left the room]")
            await close()
            break
        except Exception as e:
            ui.print_error(f"Input error: {e}")
            break