import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level2(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: CLI CONFIGURATION")
        
        self.hostname = "Router"
        self.current_mode = 0  # 0: User (>), 1: Privileged (#), 2: Config ((config)#)
        
        self.cli_engine = CLIEngine(available_commands=[
            "enable", "en", "configure terminal", "conf t", "disable", "hostname", "exit", "end"
        ])
        
        self.feedback = "System initialized. Waiting for admin input..."
        self.history = [
            "Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.1",
            "Technical Support: http://www.cisco.com/techsupport",
            "Copyright (c) 1986-2024 by Cisco Systems, Inc.",
            "",
            "Press RETURN to get started!",
            ""
        ]

        self.steps = [
            {
                "title": "1. Enter Privileged Mode",
                "desc": "Access higher permission level.",
                "cmds": "enable",
                "done": False
            },
            {
                "title": "2. Enter Global Config",
                "desc": "Enter configuration mode to modify settings.",
                "cmds": "configure terminal",
                "done": False
            },
            {
                "title": "3. Change Hostname",
                "desc": "Set the device name to 'ARDOS'.",
                "cmds": "hostname ARDOS",
                "done": False
            }
        ]

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
        if self.current_mode == 0:
            return f"{self.hostname}>"
        elif self.current_mode == 1:
            return f"{self.hostname}#"
        elif self.current_mode == 2:
            return f"{self.hostname}(config)#"

    def process_command(self, cmd):
        # Normalize command abbreviations (e.g. en -> enable)
        cmd = self.cli_engine.normalize(cmd)
        
        self.history.append(self.get_prompt_string() + cmd)
        
        # --- MOD 0: USER EXEC ---
        if self.current_mode == 0:
            if cmd == "enable":
                self.current_mode = 1
                self.feedback = "SUCCESS: Privileged Access Granted."
                self.complete_step(0)
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

        # --- MOD 1: PRIVILEGED EXEC ---
        elif self.current_mode == 1:
            if cmd == "configure terminal":
                self.current_mode = 2
                self.feedback = "SUCCESS: Entered Configuration Mode."
                self.complete_step(1)
            elif cmd == "disable":
                self.current_mode = 0
                self.feedback = "Logged out of Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

        # --- MOD 2: GLOBAL CONFIG ---
        elif self.current_mode == 2:
            if cmd.startswith("hostname "):
                parts = cmd.split(" ")
                if len(parts) > 1:
                    new_name = parts[1]
                    self.hostname = new_name
                    self.feedback = f"SUCCESS: Hostname changed to '{new_name}'."

                    if new_name == "ARDOS":
                        self.complete_step(2)
                        self.completed = True
                        self.history.append("--- MISSION ACCOMPLISHED ---")
                else:
                    self.feedback = "% Incomplete command."
            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Exited config mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

    def draw(self):
        super().draw()
