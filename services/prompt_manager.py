import os
import yaml
from typing import Dict, Any
from collections import defaultdict

class PromptManager:
    PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts')
    SYSTEM_PROMPTS_FILE = 'system_prompts.yaml'
    USER_PROMPTS_FILE = 'user_prompts.yaml'

    _system_prompts = {}
    _user_prompts = {}

    @classmethod
    def load_prompts(cls):
        cls._system_prompts = cls._load_yaml(cls.SYSTEM_PROMPTS_FILE)
        cls._user_prompts = cls._load_yaml(cls.USER_PROMPTS_FILE)
        print("Loaded prompts")

    @classmethod
    def _load_yaml(cls, filename):
        file_path = os.path.join(cls.PROMPTS_DIR, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    @classmethod
    def save_prompts(cls):
        cls._save_yaml(cls.SYSTEM_PROMPTS_FILE, cls._system_prompts)
        cls._save_yaml(cls.USER_PROMPTS_FILE, cls._user_prompts)
        print("Prompts saved successfully")

    @classmethod
    def _save_yaml(cls, filename, data):
        file_path = os.path.join(cls.PROMPTS_DIR, filename)
        try:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving prompts to {filename}: {e}")

    @classmethod
    def get_prompt(cls, prompt_type: str, prompt_name: str, **kwargs) -> str:
        if prompt_type == "system":
            return cls._system_prompts.get(prompt_name, "")
        elif prompt_type == "user":
            template = cls._user_prompts.get(prompt_name, "")
            return template.format_map(defaultdict(lambda: "N/A", kwargs))
        else:
            raise ValueError(f"Invalid prompt type: {prompt_type}")

    @classmethod
    def update_prompt(cls, name: str, content: str, prompt_type: str):
        if prompt_type == 'system':
            cls._system_prompts[name] = content
        elif prompt_type == 'user':
            cls._user_prompts[name] = content
        else:
            raise ValueError("Invalid prompt type")
        
        cls.save_prompts()
        cls.load_prompts()
        print("Reloaded prompts after update")

# Load prompts when the module is imported
PromptManager.load_prompts()
