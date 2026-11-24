TOOLS = {}
TOOL_SCHEMAS = []


def act(tool, args):
    return TOOLS[tool](**args)


def add_tool(function, description, params):
    """Bir tool'u kaydeder ve LLM'in beklediği formatta tanıtır."""
    TOOLS[function.__name__] = function
    TOOL_SCHEMAS.append({
        "type": "function",
        "function": {
            "name": function.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {p: {"type": "string", "description": d} for p, d in params.items()},
                "required": list(params),
            },
        },
    })


def weather_forecast(city):
    return {"sehir": city, "yagmur_ihtimali": 0.8}


add_tool(weather_forecast, "Bir şehir için yarının yağmur ihtimalini (0-1 arası) getirir.", {"city": "Şehir adı"})


def get_calendar():
    return [
        {"saat": "09:00", "etkinlik": "Ofiste toplantı", "yer": "kapalı alan"},
        {"saat": "18:00", "etkinlik": "Sahilde yürüyüş", "yer": "açık hava"},
    ]

add_tool(get_calendar, "Kullanıcının yarınki planlarını getirir.", {})
