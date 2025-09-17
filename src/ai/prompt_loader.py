from pathlib import Path
from typing import Any, Dict
import yaml
from jinja2 import Environment, BaseLoader, StrictUndefined

PROMPTS_DIR = Path(__file__).parents[2] / "prompts"

def load_system_prompt() -> str:
    data = yaml.safe_load((PROMPTS_DIR / "system.yaml").read_text(encoding="utf-8"))
    return data["content"]

def render_user_prompt(template_name: str, context: Dict[str, Any]) -> str:
    text = (PROMPTS_DIR / "user" / template_name).read_text(encoding="utf-8")
    env = Environment(loader=BaseLoader(), undefined=StrictUndefined, autoescape=False,
                        trim_blocks=True, lstrip_blocks=True)
    return env.from_string(text).render(**context)