import pygame
from settings import *
from levels.base_level import BaseLevel
from utils.cli import CLIEngine

class Level5(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MISSION: DEVICE HARDENING")

        self.hostname = "ARDOS"
        self.current_mode = 1
        self.current_line = ""

        self.secret_pass = None
        self.console_pass = None
        self.vty_pass = None

        self.cli_engine = CLIEngine(available_commands=[
            "configure terminal", "conf t", "enable secret", 
            "service password-encryption", "line console 0", "line vty 0 4",
            "password", "login", "exit", "end"
        ])

        self.feedback = "SECURITY AUDIT: System is VULNERABLE. Set STRONG passwords."
        self.history = [
            "ARDOS# show running-config",
            "Building configuration...",
            "Current configuration : 1024 bytes",
            "! No passwords set!",
            "! No service password-encryption",
            "ARDOS#",
            "--- SECURITY HARDENING REQUIRED ---"
        ]

        self.steps = [
            {
                "title": "1. Set Enable Secret",
                "desc": "Protect privileged mode with ANY strong password.",
                "cmds": "enable secret <password>",
                "done": False
            },
            {
                "title": "2. Encrypt All Passwords",
                "desc": "Hide plain-text passwords in config file.",
                "cmds": "service password-encryption",
                "done": False
            },
            {
                "title": "3. Secure Console Port",
                "desc": "Set physical port password & enable login.",
                "cmds": "line console 0 > password <pass> > login > exit",
                "done": False
            },
            {
                "title": "4. Secure VTY (Remote)",
                "desc": "Set remote access password & enable login.",
                "cmds": "line vty 0 4 > password <pass> > login > exit",
                "done": False
            }
        ]

        self.service_encryption = False
        self.temp_line_login = False

    def get_status_text(self):
        return "STATUS: SECURE" if self.completed else "STATUS: VULNERABLE"

    def get_status_color(self):
        return NEON_GREEN if self.completed else (255, 80, 80)

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
            return f"{self.hostname}(config-line)#"
        return ">"

    def process_command(self, cmd):
        cmd = self.cli_engine.normalize(cmd)
        self.history.append(self.get_prompt_string() + cmd)

        if self.current_mode == 1:
            if cmd == "configure terminal":
                self.current_mode = 2
                self.feedback = "SUCCESS: Global Config Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "HINT: Type 'conf t' to start configuration."

        elif self.current_mode == 2:
            if cmd.startswith("enable secret"):
                parts = cmd.split()
                if len(parts) >= 3:
                    user_pass = parts[2]
                    self.secret_pass = user_pass
                    self.feedback = f"SUCCESS: Secret set to '{user_pass}' (Hashed)."
                    self.history.append(f"[Syslog] Secret password set.")
                    self.complete_step(0)
                else:
                    self.feedback = "ERROR: Incomplete command. Usage: enable secret <password>"

            elif cmd == "service password-encryption":
                self.service_encryption = True
                self.feedback = "SUCCESS: Encryption service active."
                self.history.append("[Syslog] Encryption service enabled")
                self.complete_step(1)

            elif cmd == "line console 0":
                self.current_mode = 3
                self.current_line = "console"
                self.temp_line_login = False
                self.feedback = "MODE: Console Config. Set 'password <...>' and 'login'."

            elif cmd == "line vty 0 4":
                self.current_mode = 3
                self.current_line = "vty"
                self.temp_line_login = False
                self.feedback = "MODE: VTY Config. Set 'password <...>' and 'login'."

            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "% Invalid input detected at '^' marker."

        elif self.current_mode == 3:
            if cmd.startswith("password"):
                parts = cmd.split()
                if len(parts) >= 2:
                    user_pass = parts[1]
                    if self.current_line == "console":
                        self.console_pass = user_pass
                    elif self.current_line == "vty":
                        self.vty_pass = user_pass
                    self.feedback = f"OK: Password set to '{user_pass}'."
                    self.history.append("Password stored.")
                else:
                    self.feedback = "ERROR: Missing password. Usage: password <word>"

            elif cmd == "login":
                self.temp_line_login = True
                self.feedback = "OK: Login check enabled."
                self.history.append("Login enabled")

            elif cmd == "exit":
                is_secure = False
                if self.current_line == "console":
                    if self.console_pass and self.temp_line_login:
                        is_secure = True
                        self.feedback = "SUCCESS: Console port secured."
                        self.complete_step(2)
                elif self.current_line == "vty":
                    if self.vty_pass and self.temp_line_login:
                        is_secure = True
                        self.feedback = "SUCCESS: Remote access secured."
                        self.complete_step(3)

                if not is_secure:
                    self.feedback = "FAIL: Line NOT secure! Did you set password AND 'login'?"
                    self.history.append("%Warning: Security incomplete")

                self.current_mode = 2
                self.current_line = ""

            elif cmd == "":
                pass
            else:
                self.feedback = "HINT: Use 'password <your_pass>' and 'login'."

        if self.secret_pass and self.console_pass and self.vty_pass and self.service_encryption:
            if all(step["done"] for step in self.steps):
                self.completed = True
                self.history.append("--- SYSTEM FULLY HARDENED ---")

    def draw(self):
        super().draw()
