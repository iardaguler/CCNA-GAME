import pygame
import random
from settings import *
from levels.base_level import BaseLevel

class Level11(BaseLevel):
    def __init__(self, screen):
        super().__init__(screen, task_title="MINI-GAME: SUBNETTING SPEED RUN")
        
        self.is_windows_cmd = True
        self.term_title = " Subnet Calculator V1.0"
        self.term_text_color = WHITE
        self.term_bg_color = BLACK

        self.questions = [
            {"ip": "192.168.1.50/26", "q": "What is the Subnet Mask?", "ans": "255.255.255.192"},
            {"ip": "10.0.0.15/28", "q": "What is the Broadcast Address?", "ans": "10.0.0.15"},
            {"ip": "172.16.5.0/24", "q": "How many usable hosts per subnet?", "ans": "254"},
            {"ip": "192.168.100.100/25", "q": "What is the Network Address?", "ans": "192.168.100.0"},
            {"ip": "10.1.1.1/30", "q": "What is the Subnet Mask?", "ans": "255.255.255.252"}
        ]
        
        self.current_q_index = 0
        self.score = 0
        self.max_score = len(self.questions)
        
        self.feedback = "Welcome to Subnetting Speed Run! Answer the questions."
        self.history = [
            "--- SUBNETTING QUIZ INITIALIZED ---",
            "Type your answer and press ENTER.",
            ""
        ]

        self.steps = [
            {
                "title": f"Question {i+1}",
                "desc": q["q"] + f" ({q['ip']})",
                "cmds": "Type answer directly",
                "done": False
            } for i, q in enumerate(self.questions)
        ]

        self.ask_question()

    def ask_question(self):
        if self.current_q_index < self.max_score:
            q = self.questions[self.current_q_index]
            self.history.append(f"Target IP: {q['ip']}")
            self.history.append(f"Question: {q['q']}")
            self.history.append("Answer>_")

    def get_status_text(self):
        return f"STATUS: SCORE {self.score}/{self.max_score}" if not self.completed else "STATUS: MASTER SUBNETTER"

    def events(self, event):
        if self.completed: return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.process_command(self.user_input)
                self.user_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable():
                    self.user_input += event.unicode

    def process_command(self, cmd):
        cmd = cmd.strip()

        if self.history:
            self.history[-1] = self.history[-1].replace("_", "") + cmd

        correct_answer = self.questions[self.current_q_index]["ans"]
        
        if cmd == correct_answer:
            self.feedback = f"SUCCESS: '{cmd}' is CORRECT!"
            self.history.append("Result: Correct!")
            self.complete_step(self.current_q_index)
            self.score += 1
            self.current_q_index += 1
            self.history.append("")
            
            if self.current_q_index < self.max_score:
                self.ask_question()
            else:
                self.completed = True
                self.history.append("--- QUIZ COMPLETED ---")
        else:
            self.feedback = f"ERROR: '{cmd}' is INCORRECT. Try again."
            self.history.append(f"Result: Incorrect. Expected format example: '{correct_answer}'")
            self.history.append("Answer>_")

    def draw(self):
        super().draw()
