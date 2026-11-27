# Softtech x BUEC Agentic AI Atölyesi — Sıfırdan Adım Adım Bir AI Agent

Softtech x BUEC Agentic AI Atölyesi'nde iki günde adım adım birlikte yazdığımız agent'ın kodu.

Hiçbir agent framework'ü kullanmadan, yaklaşık 120 satır Python ile yazılmış küçük bir AI agent. Amaç eğitim: bir agent'ın içinde gerçekte ne döndüğünü, her parçayı ayrı bir dosyada görerek anlamak.

- **1. gün:** algıla → karar ver → uygula döngüsü; hafıza; tool calling.
- **2. gün:** bilgi katmanı (Knowledge). Agent'a bizim ofisin kurallarını bir dokümandan, soruyla ilgili parçasını seçerek vermek: **RAG**.

Agent şu soruya cevap arıyor:

> "İstanbul'da yarın yağmur yağarsa sahil yürüyüşüm ne olacak? Şemsiyeyi nereden bulurum?"

Cevabın yarısı dış dünyada (hava durumu, takvim), yarısı **ofis rehberinde** ("yağışlı günlerde açık hava etkinlikleri kapalı alana alınır", "ofis girişindeki ortak şemsiyeler"). İkinci yarıyı hiçbir LLM kendi bilgisinden bilemez; rehberden okuması gerekir. Hangi tool'u hangi sırayla çağıracağına ve rehbere ne zaman bakacağına agent kendisi karar veriyor.

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
│   ├── knowledge.py      # Ofis rehberini parçalar, vektöre çevirir, soruya en yakın parçaları getirir (RAG)
│   ├── rehber.md         # Ofis rehberi: 10 paragraf, her biri bir konu
│   └── rehber-buyuk.md   # Aynı rehberin 85 paragraflık hali (deneme için)
├── action/
│   └── tools.py          # Tool'lar ve tool kayıt mekanizması (rehber araması da bir tool)
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

`requirements.txt` iki grup içerir: 1. gün için `openai` ve `python-dotenv`; 2. gün için `sentence-transformers`, `torch`, `torchvision` (embedding modeli bunlarla çalışır, kurulum birkaç dakika sürebilir).

LLM olarak [Groq](https://console.groq.com) kullanılıyor. Ücretsiz bir API anahtarı alıp `.env` dosyasına koy:

```bash
cp .env.example .env
```

Sonra `.env` içindeki `GROQ_API_KEY=` satırına kendi anahtarını yaz.

> `.env` dosyası `.gitignore` içindedir. API anahtarını asla repoya gönderme.

Embedding modeli (`google/embeddinggemma-2`) ilk çalıştırmada Hugging Face'ten indirilir, sonra bilgisayarında kalır. Gemma modelleri lisans kabulü ister: indirme hata verirse [modelin sayfasında](https://huggingface.co/google/embeddinggemma-2) lisansı kabul et ve `hf auth login` ile giriş yap.

## Çalıştırma

```bash
python agent.py
```

Örnek çıktı:

```
[PERCEPTION] Kullanıcı dedi ki: İstanbul'da yarın yağmur yağarsa sahil yürüyüşüm ne olacak? Şemsiyeyi nereden bulurum?
Gördüğün: gri bulutlarla kaplı gökyüzü
[BRAIN] karar: weather_forecast {'city': 'İstanbul'}
[ACTION] sonuç: {'sehir': 'İstanbul', 'yagmur_ihtimali': 0.8}
[BRAIN] karar: search_knowledge {'query': 'İstanbul ofis şemsiye nereden alınır'}
[ACTION] sonuç: Hava ve yağış: Yağış ihtimali 0.6 ve üzerindeyse hava yağışlı kabul edilir. Yağışlı günlerde açık hava etkinlikleri kapalı alana alınır. Ofis girişindeki ortak şemsiyelerden alabilirsiniz; ertesi gün geri bırakmanız yeterlidir.
[BRAIN] cevap: İstanbul’da yarın yağmur ihtimali %80 – yağışlı bir gün bekleniyor. Sahil yürüyüşünüzü kapalı bir alana taşımanız ya da ertelemeniz daha güvenli olur. Şemsiyeyi ofisin girişindeki ortak şemsiyelerden alabilirsiniz; kullanıp ertesi gün geri bırakmanız yeterli.
```

Çıktıda dikkat edilecek şeyler:

- Agent'a "önce havaya, sonra rehbere bak" diye bir sıra **verilmedi**. Tool'ları kendisi seçti; rehberde ne arayacağını (`'İstanbul ofis şemsiye nereden alınır'`) da kendisi yazdı.
- Görüntü "gri bulutlarla kaplı gökyüzü" dediği halde agent buna güvenmedi; hava durumunu tool'dan aldı.
- "Kapalı alana alınır" ve "ofis girişindeki ortak şemsiyeler" yalnızca `brain/rehber.md` içinde yazıyor. Cevapta geçiyorsa doğru parça getirilmiş demektir.
- Cevap LLM'den geldiği için her çalıştırmada kelimesi kelimesine aynı olmaz; tool sırası da değişebilir.
- Soruda şehir adı bilerek var: `weather_forecast` şehir ister; soru şehirsiz olunca model tool çağırmak yerine "hangi şehirdesiniz?" diye sorup duruyor.

## 1. gün: agent nasıl inşa edildi

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

### Adım 3 — Knowledge: sabit bilgiler (1. gün hali)

Dosya: `brain/knowledge.py`

1. günün sonunda bu dosya tek bir cümleden ibaretti:

```python
self.facts = [
    "Yağmur ihtimali 0.7 ve üstündeyse yağmur yağacak kabul et.",
]
```

Hafıza *bu konuşmada* olanları tutar; bilgi tabanı ise *her zaman* geçerli kuralları. Bu kural system prompt'a ekleniyordu; tool `0.8` döndürdüğünde agent'ın bunu "yağacak" diye yorumlamasını sağlayan şey bu satırdı. **Knowledge, tool sonucunu yorumlar.**

Bir cümleyi elle yazmak kolay; bir ofis rehberinin tamamını elle yazamayız. 2. gün bu dosya baştan yazıldı (aşağıda).

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

`weather_forecast` ve `get_calendar` sabit değer döndürür; gerçek bir API'ye bağlı değildir. Böylece dikkat tool'un içine değil, agent döngüsüne kalır. Üçüncü tool `search_knowledge` 2. günde eklendi.

### Adım 5 — Decision: beyin karar verir

Dosya: `brain/decision.py`

`decide` fonksiyonu LLM'e üç şey gönderir:

1. **System mesajı** — rol tanımı (`ROLE`).
2. **Hafıza** — şimdiye kadarki tüm mesajlar (Adım 2).
3. **Tool şemaları** — kullanabileceği tool'ların listesi (Adım 4).

LLM iki şeyden birini yapar ve fonksiyon buna göre döner:

| LLM ne yaptı | `decide` ne döndürür |
|--------------|----------------------|
| Bir tool seçti | `(tool_adı, argümanlar, None)` |
| Düz metin yazdı | `(None, None, cevap)` |

Bu "tool calling" (function calling) mekanizmasıdır. LLM tool'u **çalıştırmaz**; yalnızca "şunu şu argümanlarla çağır" der. Çalıştırmak bizim kodumuzun işidir.

Groq, OpenAI ile uyumlu bir API sunduğu için `openai` kütüphanesi `base_url` değiştirilerek kullanılıyor. `temperature=0`: aynı girdiye hep aynı (ya da aynıya çok yakın) cevap; demo sırasında sürpriz olmasın.

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

## 2. gün: Knowledge'dan RAG'e

1. gün tool'lar agent'a **dünyayı** verdi: hava, takvim. Ama kimse ona **bizim** dünyamızı anlatmadı: ofisin kuralları, şemsiyenin nerede durduğu. Rehbersiz agent'a yukarıdaki soruyu sorunca cevap akıcı ve kendinden emin geliyor: şemsiye için market sayıyor. Yanlış olduğu, rehberli cevabın yanında görülüyor.

RAG'in tamamı tek cümle: **bilginin hepsini değil, soruyla ilgili parçalarını LLM'e ver.**

2. gün beş adımda bu cümleye gidildi. Her adımda yalnızca `brain/knowledge.py` (ve ona bağlı olarak `agent.py`) değişti:

| Adım | Ne yapıldı | Çalıştırınca ne görüldü | Bıraktığı soru |
|---|---|---|---|
| 1 | `rehber.md`'nin tamamı okunup prompt'a konur | Cevap doğru oldu (58 → 1323 karakter prompt). `rehber-buyuk.md` ile denenince Groq'un dakikalık token sınırı aşıldı: `413 Request too large` | Her soruda hepsini vermek zorunda mıyız? |
| 2 | Chunking: doküman boş satırlardan 10 parçaya bölünür, ilk ikisi verilir | Çalışma saatleri ve servis geldi; yağış kuralı gelmedi, model yine uydurdu | Hangi parçalar ilgili, nasıl seçeceğiz? |
| 3 | Kelime eşleşmesi: soruyla en çok ortak kelimesi olan parçalar | Servis ("yarın") ve kıyafet ("gri") geldi. Yağış parçasının puanı 0: soruda "yağmur", parçada "yağış" | Kelimeler tutmazsa ne olur? |
| 4 | Embedding: parçalar ve soru vektöre çevrilir, anlamca en yakın olanlar | Yağış parçası ilk sırada, hiçbir kelime tutmadığı halde. Cevap doğru, prompt'a 10 yerine 2 parça girdi | Ne zaman arayacağına kim karar veriyor? |
| 5 | Arama bir tool olur: `search_knowledge(query)` | Model aramayı kendi seçiyor, sorguyu kendi yazıyor | |

Repodaki kod 5. adımın hali. Aşağıda bu halin iki parçası anlatılıyor.

### Knowledge: parçala, vektöre çevir, en yakını getir

Dosya: `brain/knowledge.py`

```python
model = SentenceTransformer("google/embeddinggemma-2")

class Knowledge:
    def __init__(self):
        text = DOCUMENT.read_text(encoding="utf-8")
        self.chunks = [part.strip() for part in text.split("\n\n") if part.strip()]
        self.vectors = model.encode(self.chunks, prompt_name="Document")

    def retrieve(self, question, k=2):
        question_vector = model.encode(question, prompt_name="SearchQuery")
        scores = model.similarity(question_vector, self.vectors)[0].tolist()
        ranked = sorted(zip(scores, self.chunks), reverse=True)
        return "\n".join(chunk for score, chunk in ranked[:k])
```

Üç fikir var:

**Chunking.** `rehber.md` boş satırlardan bölünür; her paragraf bir parça (`chunk`). Rehber öyle yazıldı ki her paragraf tek bir konu: servis, yemek, hava ve yağış… Parçayı küçük tutmak, "ilgili olanı" seçmeyi mümkün kılar.

**Embedding.** Model her metni, anlamını taşıyan bir sayı listesine (vektöre) çevirir. Anlamca yakın metinlerin vektörleri de yakındır. Bu yüzden "yağmur yağarsa… şemsiye" sorusu, içinde "yağmur" kelimesi hiç geçmeyen "Hava ve yağış: … ortak şemsiyelerden alabilirsiniz" parçasını bulur. Kelime eşleşmesi (3. adım) bunu yapamıyordu.

Parçalar **bir kez** vektöre çevrilir (`__init__`), soru her seferinde (`retrieve`). Milyonlarca parça olsa bu vektörleri bir vektör veritabanında tutardık; on parça için bir Python listesi yeter.

`prompt_name` nedir? Model, metni vektöre çevirmeden önce başına kısa bir etiket koyar, çünkü böyle eğitilmiş: `"Document"` → "bu bir kayıt", `"SearchQuery"` → "bu bir soru". Soru ile cevabın metni birbirine benzemez ("şemsiyeyi nereden bulurum" / "ortak şemsiyelerden alabilirsiniz"); model "soru" etiketli metni "kayıt" etiketli metinlerle eşleştirmeyi öğrenmiştir.

**Similarity.** `model.similarity` iki vektör arasındaki açıya bakar (cosine similarity): aynı yön 1, dik 0. Sayının kendisi değil sırası önemli; en yüksek `k` parça döner. `k=2` olduğu için ikinci parça genellikle zayıf bir eşleşmedir, zararı yok.

### Arama da bir tool

Dosya: `action/tools.py`, sondaki blok

```python
knowledge = Knowledge()

def search_knowledge(query):
    return knowledge.retrieve(query)

add_tool(search_knowledge, "ofis rehberinden arama yapar. kurallar, yağış ve şemsiye, servis, toplantı odaları, yemek gibi konular.", {"query": "aranacak konu"})
```

4. adımda `agent.py` her soruda bir kez `retrieve` çağırıp sonucu system prompt'a koyuyordu; "Yarın planım ne?" sorusu için de rehbere bakılıyordu. 5. adımda arama, hava durumu gibi sıradan bir tool oldu: ne zaman arayacağına ve ne arayacağına model karar veriyor. Rehberden gelen parça da tool sonucu olarak hafızaya yazılıyor, system prompt'ta bilgi kalmıyor (`decide` artık yalnızca `ROLE` gönderir).

İki günün özeti:

| | Knowledge nerede | Ne zaman verilir | Kim seçer |
|---|---|---|---|
| 1. gün | Kodda, bir cümle | Her çağrıda | Biz |
| 2. gün, adım 1 | Dokümanda, tamamı | Her çağrıda | Biz |
| 2. gün, adım 4 | Dokümanda, parçalar | Her görevde bir kez | Embedding |
| 2. gün, adım 5 | Dokümanda, parçalar | Model gerek görünce | Model |

## Kendin dene

Kodu anlamanın en iyi yolu değiştirmek:

1. **Rehberi değiştir.** `brain/rehber.md` içindeki şemsiye cümlesini "Şemsiyeler 3. kattaki dolapta" yap. Cevap değişiyor mu? Kod değişmedi, bilgi değişti: RAG'in asıl faydası bu.
2. **Soruyu değiştir.** `agent.py` sonundaki `user_text`'e "Öğle yemeği kaçta, vejetaryen menü var mı?" yaz. Hangi parça geliyor? "Bilgisayarım açılmıyor, kime haber vereyim?" ile dene: ortak kelime olmadan BT destek parçasını bulmalı.
3. **`k`'yı değiştir.** `retrieve` içinde `k=2` yerine `k=1` ve `k=5` dene. Cevap ve prompt uzunluğu nasıl değişiyor?
4. **Büyük rehberi dene.** `knowledge.py` içinde `"rehber.md"` yerine `"rehber-buyuk.md"` yaz. 85 parça; arama hâlâ doğru parçayı buluyor mu? (2. günün 1. adımında bu dosya prompt'a sığmıyordu.)
5. **Puanları yazdır.** `retrieve` içine `print(ranked[:3])` ekle; cosine değerlerini gör. Yakın anlam 0.7-0.8 civarı, alakasız 0.6 civarı çıkar.
6. **Tool'un sonucunu değiştir.** `weather_forecast` içinde ihtimali `0.2` yap. Agent hâlâ şemsiye öneriyor mu? Rehberdeki 0.6 eşiğiyle birleştiriyor mu?
7. **Yeni bir tool ekle.** Şehrin sıcaklığını döndüren `get_temperature(city)` yaz, `add_tool` ile kaydet. `agent.py` ve `decision.py`'ye dokunman gerekmediğine dikkat et.
8. **Bir tool'u gerçek yap.** `weather_forecast` içinden gerçek bir hava durumu API'sini çağır.

## Bilinçli olarak basit bırakılanlar

Bu bir eğitim projesi; üretim kodu değil. Şunlar özellikle dışarıda bırakıldı:

- **Tek tool / adım.** LLM aynı anda birden fazla tool isterse yalnızca ilki çalıştırılır.
- **Hata yönetimi yok.** LLM olmayan bir tool adı ya da yanlış argüman üretirse program hata verir.
- **Tüm parametreler `string`.** `add_tool` her parametreyi metin kabul eder.
- **Hafıza kalıcı değil.** Program kapanınca her şey unutulur.
- **Görüntü gerçek değil.** Resim yerine resmin metin tarifi veriliyor.
- **Vektör veritabanı yok.** Vektörler bir Python listesinde; her çalıştırmada yeniden hesaplanır.
- **Chunk = paragraf, `k` sabit.** Gerçekte parça boyutu, örtüşme ve kaç parça getirileceği ayarlanır.

Her biri iyi bir "sonraki adım" alıştırmasıdır.

## Kullanılanlar

- [openai](https://pypi.org/project/openai/) — OpenAI uyumlu API istemcisi (Groq'a bağlanmak için)
- [python-dotenv](https://pypi.org/project/python-dotenv/) — `.env` dosyasından API anahtarını okumak için
- [sentence-transformers](https://pypi.org/project/sentence-transformers/) — embedding modeli ve cosine similarity (`torch`, `torchvision` ile)
- LLM: `openai/gpt-oss-120b` (Groq üzerinde). Farklı bir model denemek için `brain/decision.py` içindeki `MODEL` satırını değiştir; tool calling destekleyen bir model seçmen gerekir. (1. günde `qwen/qwen3.8-27b` kullanıldı; bazı sorularda tool çağrısını gerçek çağrı yerine düz metin olarak yazdığı için değiştirildi.)
- Embedding modeli: `google/embeddinggemma-2` (`brain/knowledge.py` içindeki `SentenceTransformer(...)` satırı).
- Groq ücretsiz hesapta dakikalık girdi sınırı 7000 token. Art arda çok çalıştırınca `429` gelirse bir dakika bekle.
