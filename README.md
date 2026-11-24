# Softtech x BUEC Agentic AI Atölyesi — Sıfırdan Adım Adım Bir AI Agent

Softtech x BUEC Agentic AI Atölyesi'nde adım adım birlikte yazdığımız agent'ın kodu.

Hiçbir agent framework'ü kullanmadan, yaklaşık 100 satır Python ile yazılmış küçük bir AI agent. Amaç eğitim: bir agent'ın içinde gerçekte ne döndüğünü, her parçayı ayrı bir dosyada görerek anlamak.

Agent şu soruya cevap arıyor:

> "İstanbul'da yarın yağmur yağar mı? Planlarıma bak, ona göre şemsiye almalı mıyım?"

Bunu cevaplamak için hava durumuna ve takvime bakması, sonra ikisini birleştirip karar vermesi gerekiyor. Hangi tool'u hangi sırayla çağıracağına agent kendisi karar veriyor.

## Agent nedir?

Bir agent üç şeyi döngü halinde yapar:

1. **Algılar** (perception) — dış dünyadan gelen girdiyi alır.
2. **Karar verir** (brain) — elindeki bilgiye bakıp bir sonraki adımı seçer.
3. **Uygular** (action) — seçtiği adımı gerçekten çalıştırır, sonucu hafızasına yazar.

Sonra tekrar karar adımına döner. Yapacak iş kalmayınca kullanıcıya cevap verir ve döngü biter.

```
            ┌──────────────┐
  girdi ──▶ │  PERCEPTION  │
            └──────┬───────┘
                   ▼
            ┌──────────────┐   tool seçti    ┌──────────┐
       ┌──▶ │    BRAIN     │ ──────────────▶ │  ACTION  │
       │    │ karar + hafıza│                └────┬─────┘
       │    └──────┬───────┘                      │
       │           │ cevap yazdı                  │ sonuç hafızaya
       │           ▼                              │
       │        ÇIKTI                             │
       └──────────────────────────────────────────┘
```

## Klasör yapısı

```
softtech-buec-agentic-ai-atolyesi/
├── agent.py              # Ana döngü: algıla → karar ver → uygula
├── perception/
│   └── perceive.py       # Girdiyi (metin + görüntü) tek bir algıya çevirir
├── brain/
│   ├── decision.py       # LLM'e sorar: tool mu çağırayım, cevap mı vereyim?
│   ├── memory.py         # Konuşma geçmişi (şimdiye kadar ne oldu)
│   └── knowledge.py      # Sabit bilgiler / kurallar
├── action/
│   └── tools.py          # Tool'lar ve tool kayıt mekanizması
├── requirements.txt
└── .env.example          # API anahtarı şablonu
```

## Kurulum

Python 3.10 veya üstü gerekir (3.12 ile denendi).

```bash
git clone https://github.com/seymasa/softtech-buec-agentic-ai-atolyesi.git
cd softtech-buec-agentic-ai-atolyesi
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

LLM olarak [Groq](https://console.groq.com) kullanılıyor. Ücretsiz bir API anahtarı alıp `.env` dosyasına koy:

```bash
cp .env.example .env
```

Sonra `.env` içindeki `GROQ_API_KEY=` satırına kendi anahtarını yaz.

> `.env` dosyası `.gitignore` içindedir. API anahtarını asla repoya gönderme.

## Çalıştırma

```bash
python agent.py
```

Örnek çıktı:

```
[PERCEPTION] Kullanıcı dedi ki: İstanbul'da yarın yağmur yağar mı? planlarıma bak ona göre Şemsiye almalı mıyım?
Gördüğün: günlük güneşlik gökyüzü
[BRAIN] karar: weather_forecast {'city': 'İstanbul'}
[ACTION] sonuç: {'sehir': 'İstanbul', 'yagmur_ihtimali': 0.8}
[BRAIN] karar: get_calendar {}
[ACTION] sonuç: [{'saat': '09:00', 'etkinlik': 'Ofiste toplantı', 'yer': 'kapalı alan'}, {'saat': '18:00', 'etkinlik': 'Sahilde yürüyüş', 'yer': 'açık hava'}]
[BRAIN] cevap: İstanbul'da yarın yağmur ihtimali %80; yani yağmur yağması bekleniyor. Planlarına baktığımda akşam 18:00'de sahilde açık havada yürüyüşün var. Şemsiye almanı kesinlikle öneririm.
```

Çıktıda dikkat edilecek üç şey:

- Agent'a "önce hava durumuna, sonra takvime bak" diye bir sıra **verilmedi**. İki tool'u da kendisi seçti.
- Görüntü "günlük güneşlik gökyüzü" dediği halde agent buna kanmadı; tool'dan gelen 0.8 ihtimalini ve bilgi tabanındaki kuralı esas aldı.
- Cevap LLM'den geldiği için her çalıştırmada kelimesi kelimesine aynı olmaz.

## Adım adım: agent nasıl inşa edildi

Her adım bir öncekinin üstüne tek bir parça ekler. Kodu bu sırayla okumak en kolayı.

### Adım 1 — Perception: girdiyi algıya çevir

Dosya: `perception/perceive.py`

```python
def perceive(text, image):
    return f"Kullanıcı dedi ki: {text}\nGördüğün: {image}"
```

Agent'ın dünyayla ilk teması. Burada iki "duyu" var: kullanıcının yazdığı metin ve bir görüntü. İşi basit tutmak için görüntü gerçek bir resim değil, resmin metin olarak tarifi. Fonksiyon ikisini LLM'in okuyabileceği tek bir metne çeviriyor.

Gerçek bir sistemde bu katman ses tanıma, görüntü işleme, sensör okuma gibi işleri yapar. Fikir aynıdır: ham girdiyi beynin anlayacağı biçime getirmek.

### Adım 2 — Memory: olanları hatırla

Dosya: `brain/memory.py`

LLM'in kendi hafızası yoktur; her çağrıda ona geçmişi baştan vermek gerekir. `Memory` sınıfı bu geçmişi bir `messages` listesinde tutar:

- `add_perception(percept)` → algıyı `user` mesajı olarak ekler.
- `add_action(tool, args, result)` → iki mesaj ekler: "şu tool'u çağırdım" (`assistant`) ve "sonucu buydu" (`tool`).

İkisi `call_id` ile birbirine bağlanır; LLM hangi sonucun hangi çağrıya ait olduğunu buradan anlar.

Yani buradaki "hafıza" ayrı bir veritabanı değil, LLM'e her seferinde gönderilen konuşma geçmişinin ta kendisi.

### Adım 3 — Knowledge: sabit bilgiler

Dosya: `brain/knowledge.py`

```python
self.facts = [
    "Yağmur ihtimali 0.7 ve üstündeyse yağmur yağacak kabul et.",
]
```

Hafıza *bu konuşmada* olanları tutar; bilgi tabanı ise *her zaman* geçerli kuralları. Bu kurallar system prompt'a eklenir. Tool `0.8` döndürdüğünde agent'ın bunu "yağacak" diye yorumlamasını sağlayan şey bu satırdır.

### Adım 4 — Tools: agent'ın elleri

Dosya: `action/tools.py`

LLM yalnızca metin üretir; hava durumuna bakamaz, takvimi okuyamaz. Tool'lar ona bu yetenekleri veren sıradan Python fonksiyonlarıdır.

Her tool iki yere kaydedilir:

| Liste | Kim kullanır | İçinde ne var |
|-------|--------------|---------------|
| `TOOLS` | Python (`act`) | Fonksiyon adı → fonksiyonun kendisi |
| `TOOL_SCHEMAS` | LLM | Tool'un adı, açıklaması ve parametreleri (JSON şema) |

`add_tool` ikisini birden doldurur:

```python
add_tool(weather_forecast, "Bir şehir için yarının yağmur ihtimalini (0-1 arası) getirir.", {"city": "Şehir adı"})
```

LLM tool'un kodunu görmez, yalnızca açıklamasını görür. Bu yüzden **açıklama ne kadar net olursa, doğru tool'u seçme ihtimali o kadar artar.**

Bu projedeki iki tool (`weather_forecast`, `get_calendar`) sabit değer döndürür; gerçek bir API'ye bağlı değildir. Böylece dikkat tool'un içine değil, agent döngüsüne kalır.

### Adım 5 — Decision: beyin karar verir

Dosya: `brain/decision.py`

`decide` fonksiyonu LLM'e üç şey gönderir:

1. **System mesajı** — rol tanımı + bilgi tabanı (Adım 3).
2. **Hafıza** — şimdiye kadarki tüm mesajlar (Adım 2).
3. **Tool şemaları** — kullanabileceği tool'ların listesi (Adım 4).

LLM iki şeyden birini yapar ve fonksiyon buna göre döner:

| LLM ne yaptı | `decide` ne döndürür |
|--------------|----------------------|
| Bir tool seçti | `(tool_adı, argümanlar, None)` |
| Düz metin yazdı | `(None, None, cevap)` |

Bu "tool calling" (function calling) mekanizmasıdır. LLM tool'u **çalıştırmaz**; yalnızca "şunu şu argümanlarla çağır" der. Çalıştırmak bizim kodumuzun işidir.

Groq, OpenAI ile uyumlu bir API sunduğu için `openai` kütüphanesi `base_url` değiştirilerek kullanılıyor.

### Adım 6 — Agent döngüsü: hepsini birleştir

Dosya: `agent.py`

```python
def run(self, text, image):
    percept = perceive(text, image)            # 1. algıla
    self.memory.add_perception(percept)

    for step in range(MAX_STEPS):
        tool, args, answer = decide(...)       # 2. karar ver
        if answer:
            break                              #    cevap geldiyse bitir
        result = act(tool, args)               # 3. uygula
        self.memory.add_action(tool, args, result)   # sonucu hatırla
```

Bütün agent bu döngüden ibaret. Her turda hafıza biraz daha büyür, LLM bir sonraki kararını daha fazla bilgiyle verir.

`MAX_STEPS = 6` bir emniyet sınırıdır: LLM sürekli tool çağırıp hiç cevap vermezse döngü sonsuza kadar sürmesin diye.

## Kendin dene

Kodu anlamanın en iyi yolu değiştirmek:

1. **Kuralı değiştir.** `knowledge.py` içindeki eşiği `0.9` yap. Cevap nasıl değişiyor?
2. **Tool'un sonucunu değiştir.** `weather_forecast` içinde ihtimali `0.2` yap.
3. **Takvimi değiştir.** Açık havadaki etkinliği sil. Agent hâlâ şemsiye öneriyor mu?
4. **Yeni bir tool ekle.** Örneğin şehrin sıcaklığını döndüren `get_temperature(city)` yaz, `add_tool` ile kaydet ve soruyu "mont giymeli miyim?" diye değiştir. `agent.py` ve `decision.py` dosyalarına hiç dokunman gerekmediğine dikkat et.
5. **Soruyu değiştir.** `agent.py` sonundaki `user_text` içine tool gerektirmeyen bir soru yaz ("Merhaba, nasılsın?"). Agent hiç tool çağırmadan cevap vermeli.
6. **Bir tool'u gerçek yap.** `weather_forecast` içinden gerçek bir hava durumu API'sini çağır.

## Bilinçli olarak basit bırakılanlar

Bu bir eğitim projesi; üretim kodu değil. Şunlar özellikle dışarıda bırakıldı:

- **Tek tool / adım.** LLM aynı anda birden fazla tool isterse yalnızca ilki çalıştırılır.
- **Hata yönetimi yok.** LLM olmayan bir tool adı ya da yanlış argüman üretirse program hata verir.
- **Tüm parametreler `string`.** `add_tool` her parametreyi metin kabul eder.
- **Hafıza kalıcı değil.** Program kapanınca her şey unutulur.
- **Görüntü gerçek değil.** Resim yerine resmin metin tarifi veriliyor.

Her biri iyi bir "sonraki adım" alıştırmasıdır.

## Kullanılanlar

- [openai](https://pypi.org/project/openai/) — OpenAI uyumlu API istemcisi (Groq'a bağlanmak için)
- [python-dotenv](https://pypi.org/project/python-dotenv/) — `.env` dosyasından API anahtarını okumak için
- Model: `qwen/qwen3.8-27b` (Groq üzerinde). Farklı bir model denemek için `brain/decision.py` içindeki `MODEL` satırını değiştir; tool calling destekleyen bir model seçmen gerekir.
