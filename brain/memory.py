import json


class Memory:
    def __init__(self):
        self.messages = []

    def add_perception(self, percept):
        self.messages.append({"role": "user", "content": percept})

    def add_action(self, tool, args, result):
        call_id = f"call_{len(self.messages)}"

        # "Şu tool'u seçtim" ...
        self.messages.append({
            "role": "assistant",
            "tool_calls": [{
                "id": call_id,
                "type": "function",
                "function": {"name": tool, "arguments": json.dumps(args)},
            }],
        })

        self.messages.append({"role": "tool", "tool_call_id": call_id, "content": str(result)})
