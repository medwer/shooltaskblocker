import tkinter as tk
from tkinter import messagebox
from .questions import QuestionManager
from .security import SystemSecurity

class SchoolTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Школьная программа")
        self.security = SystemSecurity(self.root)
        self.security.disable_window_controls()
        self.question_manager = QuestionManager()
        self.setup_ui()
        self.refresh_questions()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        tk.Label(
            self.main_frame,
            text="Ответьте правильно на все вопросы, чтобы закрыть программу",
            font=("Arial", 14, "bold"),
            wraplength=600
        ).pack(pady=(0, 20))
        self.questions_frame = tk.Frame(self.main_frame)
        self.questions_frame.pack(fill=tk.BOTH, expand=True)
        self.check_btn = tk.Button(
            self.main_frame,
            text="Проверить ответы",
            command=self.check_answers,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white"
        )
        self.check_btn.pack(pady=20)

    def refresh_questions(self):
        for widget in self.questions_frame.winfo_children():
            widget.destroy()
        questions = self.question_manager.generate_questions()
        self.answer_entries = []
        for i, q in enumerate(questions):
            frame = tk.Frame(self.questions_frame, bd=1, relief=tk.GROOVE, padx=10, pady=10)
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=f"Вопрос {i + 1}: {q['question']}",
                     font=("Arial", 12)).pack(anchor="w")
            entry = tk.Entry(frame, font=("Arial", 12))
            entry.pack(fill=tk.X, pady=5)
            entry.insert(0, self.question_manager.user_answers[i])
            entry.bind("<KeyRelease>", lambda e, idx=i: self.save_answer(idx, e.widget.get()))
            self.answer_entries.append(entry)

    def save_answer(self, index, answer):
        self.question_manager.update_answer(index, answer)

    def check_answers(self):
        if self.question_manager.check_answers():
            messagebox.showinfo("Успех", "Все ответы верны! Программа закроется.")
            self.close_program()
        else:
            messagebox.showwarning("Ошибка", "Не все ответы верны! Попробуйте еще раз.")
            self.refresh_questions()

    def close_program(self):
        self.security.release_hooks()
        self.root.quit()
        self.root.destroy()