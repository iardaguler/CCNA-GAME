import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level7(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: STATIC ROUTING")

        self.hostname = "RouterA"
        self.current_mode = 1

        self.cli_engine = CLIEngine(available_commands=[
            "configure terminal", "conf t", "ip route", "exit", "end"
        ])

        self.feedback = "System Ready. Connect 192.168.2.0/24 via next-hop 10.0.0.2."
        self.history = [
            "RouterA> enable",
            "RouterA# show ip route",
            "Codes: C - connected, S - static",
            "C    192.168.1.0/24 is directly connected, Gig0/0",
            "C    10.0.0.0/30 is directly connected, Ser0/0/0",
            "RouterA#",
            "--- ROUTING REQUIRED ---"
        ]

        self.steps = [
            {
                "title": "1. Enter Global Config",
                "desc": "Access configuration mode.",
                "cmds": "conf t",
                "done": False
            },
            {
                "title": "2. Configure Static Route",
                "desc": "Route to 192.168.2.0 mask 255.255.255.0 via 10.0.0.2",
                "cmds": "ip route 192.168.2.0 255.255.255.0 10.0.0.2",
                "done": False
            }
        ]

        self.route_added = False

    def events(self, event):
        if self.completed: return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.process_command(self.user_input)
                self.cli_engine.add_to_history(self.user_input)
                self.user_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            elif event.key == pygame.K_UP:
                self.user_input = self.cli_engine.get_previous_command()
            elif event.key == pygame.K_DOWN:
                self.user_input = self.cli_engine.get_next_command(self.user_input)
            elif event.key == pygame.K_TAB:
                self.user_input = self.cli_engine.tab_complete(self.user_input)
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable():
                    self.user_input += event.unicode

    def get_prompt_string(self):
        if self.current_mode == 1:
            return f"{self.hostname}#"
        elif self.current_mode == 2:
            return f"{self.hostname}(config)#"
        return ">"

    def process_command(self, cmd):
        cmd = self.cli_engine.normalize(cmd)
        self.history.append(self.get_prompt_string() + cmd)

        if self.current_mode == 1:
            if cmd == "configure terminal":
                self.current_mode = 2
                self.feedback = "Global Config Mode."
                self.complete_step(0)
            elif cmd == "":
                pass
            else:
                self.feedback = "Error: Type 'conf t'."

        elif self.current_mode == 2:
            if cmd.startswith("ip route "):
                parts = cmd.split()
                if len(parts) == 5:
                    dest = parts[2]
                    mask = parts[3]
                    nexthop = parts[4]
                    
                    if dest == "192.168.2.0" and mask == "255.255.255.0" and nexthop == "10.0.0.2":
                        self.route_added = True
                        self.feedback = "SUCCESS: Static route configured."
                        self.complete_step(1)
                    else:
                        self.feedback = "ERROR: Incorrect parameters for ip route."
                else:
                    self.feedback = "Usage: ip route <network> <mask> <next-hop>"
            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected."

        if self.route_added:
            self.completed = True
            self.history.append("--- ROUTING ESTABLISHED ---")

    def draw(self):
        super().draw()
