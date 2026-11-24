class Knowledge:
    def __init__(self):
        self.facts = [
            "Yağmur ihtimali 0.7 ve üstündeyse yağmur yağacak kabul et.",
        ]

    def as_text(self):
        return "\n".join(self.facts)
