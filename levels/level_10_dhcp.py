import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level10(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: DHCP SERVER")

        self.hostname = "CoreRouter"
        self.current_mode = 1

        self.cli_engine = CLIEngine(available_commands=[
            "configure terminal", "conf t", "ip dhcp excluded-address",
            "ip dhcp pool", "network", "default-router", "dns-server", "exit", "end"
        ])

        self.feedback = "System Ready. Setup a DHCP pool named LAN_POOL."
        self.history = [
            "CoreRouter> enable",
            "CoreRouter# show ip dhcp binding",
            "",
            "CoreRouter#",
            "--- DHCP CONFIGURATION REQUIRED ---"
        ]

        self.steps = [
            {
                "title": "1. Exclude Addresses",
                "desc": "Exclude 192.168.1.1 to 192.168.1.10.",
                "cmds": "ip dhcp excluded-address 192.168.1.1 192.168.1.10",
                "done": False
            },
            {
                "title": "2. Create DHCP Pool",
                "desc": "Create pool named LAN_POOL.",
                "cmds": "ip dhcp pool LAN_POOL",
                "done": False
            },
            {
                "title": "3. Define Network",
                "desc": "Set network 192.168.1.0/24.",
                "cmds": "network 192.168.1.0 255.255.255.0",
                "done": False
            },
            {
                "title": "4. Set Default Router",
                "desc": "Set gateway 192.168.1.1.",
                "cmds": "default-router 192.168.1.1",
                "done": False
            }
        ]

        self.excluded = False
        self.pool_created = False
        self.net_defined = False
        self.router_defined = False

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
        elif self.current_mode == 3:
            return f"{self.hostname}(dhcp-config)#"
        return ">"

    def process_command(self, cmd):
        cmd = self.cli_engine.normalize(cmd)
        self.history.append(self.get_prompt_string() + cmd)

        if self.current_mode == 1:
            if cmd == "configure terminal":
                self.current_mode = 2
                self.feedback = "Global Config Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "Error: Type 'conf t'."

        elif self.current_mode == 2:
            if cmd == "ip dhcp excluded-address 192.168.1.1 192.168.1.10":
                self.excluded = True
                self.feedback = "SUCCESS: Addresses excluded."
                self.complete_step(0)
            elif cmd == "ip dhcp pool LAN_POOL":
                self.current_mode = 3
                self.pool_created = True
                self.feedback = "SUCCESS: DHCP Pool created."
                self.complete_step(1)
            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input."

        elif self.current_mode == 3:
            if cmd == "network 192.168.1.0 255.255.255.0":
                self.net_defined = True
                self.feedback = "SUCCESS: Network assigned to pool."
                self.complete_step(2)
            elif cmd == "default-router 192.168.1.1":
                self.router_defined = True
                self.feedback = "SUCCESS: Default gateway assigned."
                self.complete_step(3)
            elif cmd == "dns-server 8.8.8.8":
                self.feedback = "SUCCESS: DNS Server assigned."
            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "Exited DHCP config mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input."

        if self.excluded and self.pool_created and self.net_defined and self.router_defined:
            self.completed = True
            self.history.append("--- DHCP SERVER ACTIVE ---")

    def draw(self):
        super().draw()
