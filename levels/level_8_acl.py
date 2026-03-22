import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level8(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: ACCESS CONTROL LIST")

        self.hostname = "Firewall"
        self.current_mode = 1
        self.current_interface = ""

        self.cli_engine = CLIEngine(available_commands=[
            "configure terminal", "conf t", "access-list 10 deny host", 
            "access-list 10 permit any", "interface gig0/0", "int g0/0",
            "ip access-group 10 in", "exit", "end"
        ])

        self.feedback = "System Ready. Block PC (192.168.1.50) from entering Gig0/0."
        self.history = [
            "Firewall# show access-lists",
            "No access lists configured.",
            "Firewall#",
            "--- ACL CONFIGURATION REQUIRED ---"
        ]

        self.steps = [
            {
                "title": "1. Deny Specific Host",
                "desc": "Block IP 192.168.1.50.",
                "cmds": "access-list 10 deny host 192.168.1.50",
                "done": False
            },
            {
                "title": "2. Permit All Others",
                "desc": "Allow the rest of the traffic.",
                "cmds": "access-list 10 permit any",
                "done": False
            },
            {
                "title": "3. Apply to Interface",
                "desc": "Apply ACL 10 inbound on gig0/0.",
                "cmds": "int g0/0 > ip access-group 10 in",
                "done": False
            }
        ]

        self.acl_deny = False
        self.acl_permit = False
        self.acl_applied = False

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
            if cmd.startswith("access-list 10 "):
                if cmd == "access-list 10 deny host 192.168.1.50":
                    self.acl_deny = True
                    self.feedback = "SUCCESS: Host denied."
                    self.complete_step(0)
                elif cmd == "access-list 10 permit any":
                    self.acl_permit = True
                    self.feedback = "SUCCESS: Remaining traffic permitted."
                    self.complete_step(1)
                else:
                    self.feedback = "ERROR: Incorrect ACL rule."
                    
            elif cmd.startswith("interface "):
                if "gigabitethernet" in cmd and "0/0" in cmd:
                    self.current_mode = 3
                    self.current_interface = "GigabitEthernet0/0"
                    self.feedback = "SUCCESS: Interface g0/0 selected."
                else:
                    self.feedback = "ERROR: Wrong interface. Use 'g0/0'."
            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input."

        elif self.current_mode == 3:
            if cmd == "ip access-group 10 in":
                if self.acl_deny and self.acl_permit:
                    self.acl_applied = True
                    self.feedback = "SUCCESS: ACL applied to interface."
                    self.complete_step(2)
                else:
                    self.feedback = "ERROR: Configure ACL rules completely before applying."
            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "Exited interface mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input."

        if self.acl_applied:
            self.completed = True
            self.history.append("--- NETWORK SECURED ---")

    def draw(self):
        super().draw()
