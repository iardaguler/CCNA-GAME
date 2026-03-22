import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level9(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: NAT CONFIGURATION")

        self.hostname = "EdgeRouter"
        self.current_mode = 1
        self.current_interface = ""

        self.cli_engine = CLIEngine(available_commands=[
            "configure terminal", "conf t", "interface gig0/0", "interface gig0/1",
            "ip nat inside", "ip nat outside", "access-list 1 permit",
            "ip nat inside source list 1 interface gig0/1 overload", "exit", "end"
        ])

        self.feedback = "System Ready. Configure PAT (NAT Overload) for internal network."
        self.history = [
            "EdgeRouter> enable",
            "EdgeRouter# show ip nat translations",
            "",
            "EdgeRouter#",
            "--- NAT REQUIRED FOR INTERNET ACCESS ---"
        ]

        self.steps = [
            {
                "title": "1. Define Inside Interface",
                "desc": "Set Gig0/0 as NAT inside.",
                "cmds": "int gig0/0 > ip nat inside",
                "done": False
            },
            {
                "title": "2. Define Outside Interface",
                "desc": "Set Gig0/1 as NAT outside.",
                "cmds": "int gig0/1 > ip nat outside",
                "done": False
            },
            {
                "title": "3. Create ACL",
                "desc": "Permit 192.168.1.0/24 network.",
                "cmds": "access-list 1 permit 192.168.1.0 0.0.0.255",
                "done": False
            },
            {
                "title": "4. Configure Overload",
                "desc": "Map ACL 1 to interface Gig0/1 with overload.",
                "cmds": "ip nat inside source list 1 interface gig0/1 overload",
                "done": False
            }
        ]

        self.nat_inside = False
        self.nat_outside = False
        self.acl_created = False
        self.nat_overload = False

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
            return f"{self.hostname}(config-if)#"
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
            if cmd.startswith("interface "):
                if "gigabitethernet" in cmd and "0/0" in cmd:
                    self.current_mode = 3
                    self.current_interface = "GigabitEthernet0/0"
                    self.feedback = "SUCCESS: Interface g0/0 selected."
                elif "gigabitethernet" in cmd and "0/1" in cmd:
                    self.current_mode = 3
                    self.current_interface = "GigabitEthernet0/1"
                    self.feedback = "SUCCESS: Interface g0/1 selected."
                else:
                    self.feedback = "ERROR: Use gig0/0 or gig0/1."
            elif cmd == "access-list 1 permit 192.168.1.0 0.0.0.255":
                self.acl_created = True
                self.feedback = "SUCCESS: Access list 1 configured."
                self.complete_step(2)
            elif cmd == "ip nat inside source list 1 interface gigabitethernet 0/1 overload":
                self.nat_overload = True
                self.feedback = "SUCCESS: PAT (Overload) configured."
                self.complete_step(3)
            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input."

        elif self.current_mode == 3:
            if cmd == "ip nat inside":
                if self.current_interface == "GigabitEthernet0/0":
                    self.nat_inside = True
                    self.feedback = "SUCCESS: Interface marked as NAT inside."
                    self.complete_step(0)
                else:
                    self.feedback = "ERROR: Gig0/0 should be inside."
            elif cmd == "ip nat outside":
                if self.current_interface == "GigabitEthernet0/1":
                    self.nat_outside = True
                    self.feedback = "SUCCESS: Interface marked as NAT outside."
                    self.complete_step(1)
                else:
                    self.feedback = "ERROR: Gig0/1 should be outside."
            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "Exited interface mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input."

        if self.nat_inside and self.nat_outside and self.acl_created and self.nat_overload:
            self.completed = True
            self.history.append("--- NAT CONFIGURED SUCCESSFULLY ---")

    def draw(self):
        super().draw()
