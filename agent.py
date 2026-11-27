from action.tools import TOOL_SCHEMAS, act
from brain.decision import decide
from brain.knowledge import Knowledge
from brain.memory import Memory
from perception.perceive import perceive

MAX_STEPS = 6


class Agent:
    def __init__(self):
        self.memory = Memory()
        self.knowledge = Knowledge()

    def run(self, text, image):
        percept = perceive(text, image)
        self.memory.add_perception(percept)
        print("[PERCEPTION]", percept)

        for step in range(MAX_STEPS):
            tool, args, answer = decide(self.memory, TOOL_SCHEMAS)
            if answer:
                print("[BRAIN] cevap:", answer)
                break
            print("[BRAIN] karar:", tool, args)

            result = act(tool, args)
            print("[ACTION] sonuç:", result)

            self.memory.add_action(tool, args, result)


if __name__ == "__main__":
    user_text = "İstanbul'da yarın yağmur yağarsa sahil yürüyüşüm ne olacak? Şemsiyeyi nereden bulurum?"
    sky_image = "gri bulutlarla kaplı gökyüzü"
    Agent().run(user_text, sky_image)
