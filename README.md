# 🍳 ChefRAG: Akıllı Mutfak Asistanı

> **"Bugün ne pişirsem diye düşünme, sen malzemeni söyle ben şefin olarak hazırlayayım!"**

ChefRAG, modern bir **RAG (Retrieval-Augmented Generation)** mimarisine sahip, yerel bir tarif veritabanını kullanarak kullanıcıya özel yemek önerileri sunan akıllı bir mutfak asistanıdır. 

ChefRAG, klasik “tarif öneren chatbot”lardan farklı olarak, tarifleri LLM’in uydurması yerine **yerel ve denetlenebilir bir tarif veritabanından** çeker.
Bu sayede daha tutarlı, tekrarlanabilir ve güvenilir cevaplar üretir.

## ✨ Temel Özellikler
- **Kalıcı Oturum Yönetimi:** JSON tabanlı sistem sayesinde sohbet geçmişiniz tarayıcı kapansa bile silinmez.
- **Hafızalı Sohbet (Memory):** Önceki mesajlarınızı hatırlar, "Peki yanına ne gider?" gibi devam sorularına anlamlı yanıtlar verir.
- **Multi-Session Desteği:** Yan menüde eski sohbetlerinizi başlıklar halinde görebilir ve aralarında geçiş yapabilirsiniz.
- **Hızlı Çıkarım (Streaming):** Groq LPU altyapısı ve Llama 3.3 modeli sayesinde cevapları gerçek zamanlı sunar.
- **Modüler Mimari:** Mantık (Engine) ve arayüz (UI) katmanları tamamen birbirinden ayrı (Separation of Concerns) tasarlanmıştır.

## 🧠 RAG Akışı Nasıl Çalışır?

1. Kullanıcı malzemelerini veya sorusunu girer
2. Soru embedding’e dönüştürülür
3. ChromaDB üzerinde en alakalı tarifler aranır
4. Bulunan tarifler LLM’e bağlam (context) olarak verilir
5. LLM yalnızca bu bağlama dayanarak cevap üretir


## 🛠️ Teknoloji Yığını
- **LLM:** Groq (Llama-3.3-70b-versatile)
- **Orchestration:** LangChain (LCEL)
- **Vektör Veritabanı:** ChromaDB
- **Embeddings:** HuggingFace (all-MiniLM-L6-v2)
- **Arayüz:** Streamlit (Custom CSS ile özelleştirilmiş)
- **Veri Saklama:** JSON tabanlı yerel depolama

## 🚀 Kurulum ve Çalıştırma

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/beyzanurulukus1/chefRAG.git
   cd chefRAG
2. Gerekli kütüphaneleri kurun:
   ```bash
   pip install -r requirements.txt
3. Veritabanı oluşturun:
   ```bash
   python ingest.py
4. .env dosyanıza API ekleyin:
   ```bash
   GROQ_API_KEY=your_api_key_here
5. Uygulamayı başlatın:
   ```bash
   streamlit run app.py

## ⚙️ Gereksinimler
- Python 3.9+
- pip

## 📂 Proje Yapısı

```text
chefRAG/
├── app.py              # Streamlit arayüzü ve session yönetimi
├── engine.py           # RAG mantığı ve LangChain zinciri
├── ingest.py           # Veri işleme ve vektör veritabanı oluşturma
├── tarifler.json       # Bilgi kaynağı (Tarif veritabanı)
├── requirements.txt    # Gerekli Python kütüphaneleri
├── .env                # API anahtarları (Yerelde tutulur)
└── chat_sessions.json  # Kalıcı sohbet geçmişi (Otomatik oluşturulur)
