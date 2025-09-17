from .gemini_client import get_model
from .tools import tools
from .router import TOOL_ROUTER
from .prompt_loader import load_system_prompt, render_user_prompt

def run_planner(form_input: dict) -> str:
    system_text = load_system_prompt()
    user_text = render_user_prompt("initial_prompt.txt", form_input)
    model = get_model(tools=tools)

    resp = model.generate_content(contents=[{"role":"user","parts":[user_text]}],
                                    system_instruction=system_text)

    while True:
        parts = resp.candidates[0].content.parts if resp.candidates else []
        calls = [p.function_call for p in parts if getattr(p, "function_call", None)]
        if not calls: break
        tool_outputs = []
        for call in calls:
            name, args = call.name, dict(call.args)
            out = TOOL_ROUTER[name](args)
            tool_outputs.append({"function_call":{"name":name},"output":out})
        resp = model.generate_content(contents=[resp.candidates[0].content, *tool_outputs])
    return resp.text