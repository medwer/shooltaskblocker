import json
import random
from pathlib import Path
import configparser

class QuestionManager:
    def __init__(self):
        self.questions = self._load_questions()
        self.config = self._load_config()
        self.current_questions = []
        self.user_answers = []

    def _load_questions(self):
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'questions.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _load_config(self):
        config = configparser.ConfigParser()
        default_config = {
            'tasks_to_solve': 1,
            'items': 'math',
            'enable_timer': False,
            'timer_minutes': 30
        }

        try:
            config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
            config.read(config_path, encoding='utf-8')

            if 'Settings' not in config:
                return default_config

            def clean_value(value):
                if isinstance(value, str):
                    return value.split('#')[0].strip()
                return value

            items_str = config.get('Settings', 'Items', fallback='math')
            items = [item.strip() for item in items_str.split(',')]
            settings = config['Settings']
            loaded_config = {
                'tasks_to_solve': int(clean_value(settings.get('TasksToSolve'))),
                'items': items,
                'enable_timer': settings.getboolean('EnableTimer'),
                'timer_minutes': int(clean_value(settings.get('TimerMinutes')))
            }

            return loaded_config

        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            return default_config

    def generate_questions(self):
        count = self.config['tasks_to_solve']
        selected_items = self.config['items']
        filtered_questions = [
            q for q in self.questions
            if q.get('item') in selected_items
        ]
        count = min(count, len(filtered_questions))
        self.current_questions = self._sample_questions(filtered_questions, count, selected_items)
        self.user_answers = [""] * len(self.current_questions)
        return self.current_questions

    def _sample_questions(self, questions, count, items):
        questions_by_item = {item: [] for item in items}
        for q in questions:
            questions_by_item[q['item']].append(q)
        per_item = count // len(items)
        remainder = count % len(items)
        result = []
        for i, item in enumerate(items):
            take = per_item + (1 if i < remainder else 0)
            if take > 0:
                result.extend(random.sample(questions_by_item[item], min(take, len(questions_by_item[item]))))

                random.shuffle(result)
        return result

    def update_answer(self, index, answer):
        if 0 <= index < len(self.user_answers):
            self.user_answers[index] = answer

    def check_answers(self):
        return all(
            user_answer.strip().lower() == q["answer"].lower()
            for q, user_answer in zip(self.current_questions, self.user_answers)
        )