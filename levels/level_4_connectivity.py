import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level4(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: ENDPOINT CONNECTIVITY")

        self.is_windows_cmd = True
        self.term_title = " Command Prompt - C:\\Windows\\System32\\cmd.exe"
        self.term_text_color = WHITE
        self.term_bg_color = BLACK

        self.pc_ip = "0.0.0.0"
        self.pc_mask = "0.0.0.0"
        self.pc_gateway = "0.0.0.0"

        self.cli_engine = CLIEngine(available_commands=[
            "ipconfig", "set ip", "ping", "cls"
        ])

        self.feedback = "Terminal Ready. Use 'ipconfig' to check status."
        self.history = [
            "Microsoft Windows [Version 10.0.19045]",
            "(c) Microsoft Corporation. All rights reserved.",
            "",
            "C:\\Users\\Admin>_"
        ]

        self.steps = [
            {
                "title": "1. Check Configuration",
                "desc": "Verify current network adapter settings.",
                "cmds": "ipconfig",
                "done": False
            },
            {
                "title": "2. Assign Static IP",
                "desc": "Set any IP (Must be different from Gateway).",
                "cmds": "set ip <ip> <mask> <gateway>",
                "done": False
            },
            {
                "title": "3. Verify Connectivity",
                "desc": "Test connection to the Router (Gateway).",
                "cmds": "ping 192.168.1.1",
                "done": False
            }
        ]

        self.ip_set = False
        self.ping_success = False

    def get_status_text(self):
        return "STATUS: CONNECTED" if self.completed else "STATUS: DISCONNECTED"

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

    def process_command(self, cmd):
        cmd = cmd.strip()

        # Update prompt line
        if self.history:
            self.history[-1] = self.history[-1].replace("_", "") + cmd

        if cmd == "ipconfig":
            self.history.append("")
            self.history.append("Ethernet adapter Ethernet0:")
            self.history.append(f"   IPv4 Address. . . . . . : {self.pc_ip}")
            self.history.append(f"   Subnet Mask . . . . . . : {self.pc_mask}")
            self.history.append(f"   Default Gateway . . . . : {self.pc_gateway}")
            self.history.append("")
            self.feedback = "SUCCESS: Configuration displayed."
            self.complete_step(0)

        elif cmd.startswith("set ip"):
            parts = cmd.split()
            if len(parts) == 5:
                ip = parts[2]
                mask = parts[3]
                gw = parts[4]

                if ip == gw:
                    self.feedback = "ERROR: IP Conflict! Client IP cannot be same as Gateway."
                    self.history.append("Error: Duplicate IP address detected.")
                elif gw != "192.168.1.1":
                    self.feedback = "ERROR: Gateway unreachable. Target Router is 192.168.1.1"
                    self.history.append("Error: Invalid Default Gateway.")
                else:
                    self.pc_ip = ip
                    self.pc_mask = mask
                    self.pc_gateway = gw
                    self.ip_set = True
                    self.feedback = f"SUCCESS: Static IP {ip} assigned."
                    self.history.append("Command completed successfully.")
                    self.complete_step(1)
            else:
                self.history.append("Usage: set ip <ip> <mask> <gateway>")
                self.feedback = "ERROR: Invalid syntax."

        elif cmd.startswith("ping"):
            target = cmd.split()[-1]
            self.history.append(f"Pinging {target} with 32 bytes of data:")

            if target == "192.168.1.1":
                correct_subnet = self.pc_ip.startswith("192.168.1.")

                if self.ip_set and correct_subnet:
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.ping_success = True
                    self.feedback = "SUCCESS: Connectivity Verified!"
                    self.complete_step(2)
                elif self.ip_set and not correct_subnet:
                    self.history.append("Request timed out.")
                    self.history.append("Request timed out.")
                    self.history.append("Request timed out.")
                    self.history.append("Request timed out.")
                    self.feedback = "FAIL: Destination host unreachable (Subnet Mismatch)."
                else:
                    self.history.append("General failure.")
                    self.feedback = "FAIL: PC needs a valid IP first!"
            else:
                self.history.append("Request timed out.")
                self.feedback = "ERROR: Target unreachable."

        elif cmd == "cls":
            self.history = []

        else:
            if cmd != "":
                self.history.append(f"'{cmd}' is not recognized as an internal command.")
                self.feedback = "ERROR: Unknown command."

        self.history.append("C:\\Users\\Admin>_")

        if self.ip_set and self.ping_success:
            self.completed = True

    def draw(self):
        super().draw()
