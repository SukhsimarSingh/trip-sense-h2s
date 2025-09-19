import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Any

PROMPTS_DIR = "prompts"
SYSTEM_PROMPT_PATH = PROMPTS_DIR + "/system.yaml"
USER_PROMPT_PATH = PROMPTS_DIR + "/user"
TEMPLATE_FILE = "initial_prompt.jinja"

def load_system_prompt() -> str:
    with open(SYSTEM_PROMPT_PATH) as f:
        data = yaml.safe_load(f)
    return data["content"]

def render_user_prompt(context: dict[str, Any]) -> str:
    jinja_env = Environment(loader=FileSystemLoader(USER_PROMPT_PATH), autoescape=select_autoescape())
    template = jinja_env.get_template(TEMPLATE_FILE)
    return template.render(**context)