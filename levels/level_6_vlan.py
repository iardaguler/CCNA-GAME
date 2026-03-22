import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level6(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: VLAN SEGMENTATION")

        self.hostname = "Switch"
        self.current_mode = 1
        self.current_interface = ""

        self.cli_engine = CLIEngine(available_commands=[
            "configure terminal", "conf t", "vlan 10", "vlan 20", 
            "interface fa0/1", "interface fa0/2", "int fa0/1", "int fa0/2",
            "switchport access vlan", "name", "exit", "end"
        ])

        self.feedback = "System Ready. Configure VLANs for Department Separation."
        pad = " " * 28
        self.history = [
            "Switch> enable",
            "Switch# show vlan brief",
            "VLAN Name       Status    Ports",
            "---- ---------- --------- ---------------------------",
            f"1    default    active    Fa0/1, Fa0/2, Fa0/3, Fa0/4",
            f"{pad}Fa0/5, Fa0/6, Fa0/7, Fa0/8",
            f"{pad}Fa0/9..Fa0/24, Gi0/1-2",
            "1002 fddi-def   act/unsup ",
            "1003 token-ring act/unsup ",
            "",
            "Switch#",
            "--- SEGMENTATION REQUIRED ---"
        ]

        self.steps = [
            {
                "title": "1. Create VLAN 10 (Sales)",
                "desc": "Create the VLAN ID and name it.",
                "cmds": "vlan 10 > name Sales > exit",
                "done": False
            },
            {
                "title": "2. Create VLAN 20 (HR)",
                "desc": "Create the VLAN ID and name it.",
                "cmds": "vlan 20 > name HR > exit",
                "done": False
            },
            {
                "title": "3. Assign Port fa0/1 to Sales",
                "desc": "Move interface FastEthernet0/1 to VLAN 10.",
                "cmds": "int fa0/1 > switchport access vlan 10",
                "done": False
            },
            {
                "title": "4. Assign Port fa0/2 to HR",
                "desc": "Move interface FastEthernet0/2 to VLAN 20.",
                "cmds": "int fa0/2 > switchport access vlan 20",
                "done": False
            }
        ]

        self.vlan10_exists = False
        self.vlan20_exists = False
        self.port1_assigned = False
        self.port2_assigned = False

    def get_status_text(self):
        return "STATUS: SEGMENTED" if self.completed else "STATUS: DEFAULT VLAN 1"

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
        elif self.current_mode == 4:
            return f"{self.hostname}(config-vlan)#"
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
                self.feedback = "Error: Type 'conf t' to configure VLANs."

        elif self.current_mode == 2:
            if cmd.startswith("vlan "):
                parts = cmd.split()
                if len(parts) > 1:
                    vid = parts[1]
                    if vid == "10":
                        self.current_mode = 4
                        self.vlan10_exists = True
                        self.feedback = "VLAN 10 Created. Name it 'Sales'."
                        self.history.append("VLAN 10 added.")
                    elif vid == "20":
                        self.current_mode = 4
                        self.vlan20_exists = True
                        self.feedback = "VLAN 20 Created. Name it 'HR'."
                        self.history.append("VLAN 20 added.")
                    else:
                        self.feedback = "Error: Task requires VLAN 10 and 20."
                else:
                    self.feedback = "Usage: vlan <id>"

            elif cmd.startswith("interface "):
                if "fastethernet" in cmd and "0/1" in cmd:
                    self.current_mode = 3
                    self.current_interface = "fa0/1"
                    self.feedback = "Configuring Interface fa0/1."
                elif "fastethernet" in cmd and "0/2" in cmd:
                    self.current_mode = 3
                    self.current_interface = "fa0/2"
                    self.feedback = "Configuring Interface fa0/2."
                else:
                    self.feedback = "Error: Use 'int fa0/1' or 'int fa0/2'."

            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

        elif self.current_mode == 3:
            # Normalizasyon ile "switchport access vlan" tam kalır
            if cmd.startswith("switchport access vlan "):
                parts = cmd.split()
                if len(parts) > 3:
                    vid = parts[3]
                    if self.current_interface == "fa0/1" and vid == "10":
                        if self.vlan10_exists:
                            self.port1_assigned = True
                            self.feedback = "SUCCESS: fa0/1 moved to VLAN 10."
                            self.complete_step(2)
                        else:
                            self.feedback = "Error: Create VLAN 10 first!"
                    elif self.current_interface == "fa0/2" and vid == "20":
                        if self.vlan20_exists:
                            self.port2_assigned = True
                            self.feedback = "SUCCESS: fa0/2 moved to VLAN 20."
                            self.complete_step(3)
                        else:
                            self.feedback = "Error: Create VLAN 20 first!"
                    else:
                        self.feedback = "Error: Wrong VLAN for this port."
                else:
                    self.feedback = "Usage: switchport access vlan <id>"

            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "Exited interface mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

        elif self.current_mode == 4:
            if cmd.startswith("name "):
                parts = cmd.split()
                if len(parts) > 1:
                    name = parts[1]
                    self.feedback = f"VLAN name set to {name}."
                    if self.vlan10_exists and not self.steps[0]["done"] and name == "Sales":
                        self.complete_step(0)
                    elif self.vlan20_exists and not self.steps[1]["done"] and name == "HR":
                        self.complete_step(1)
                else:
                    self.feedback = "Usage: name <word>"
            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "VLAN configuration saved."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

        if self.port1_assigned and self.port2_assigned:
            self.completed = True
            self.history.append("--- SEGMENTATION COMPLETE ---")

    def draw(self):
        super().draw()
