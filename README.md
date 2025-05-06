# FeynmanChat - AI Destekli Öğrenme Uygulaması

Yapay Zeka ve Teknoloji Akademisi 2025 AI Jam Hackathon kapsamında Grup 24 tarafından geliştirilen **FeynmanChat**, karakter tabanlı etkileşimli bir öğrenme uygulamasıdır. Kullanıcılar; çocuk, üniversiteli ve profesör karakterleriyle konuşarak belirli bir konuda sadece sorular üzerinden derinlemesine düşünmeye teşvik edilir.

## ✨ Özellikler

- 👶 **Karakter Tabanlı Sohbet:** Kullanıcılar "Meraklı Çocuk", "Araştırmacı Öğrenci" veya "Profesör" karakterlerinden birini seçerek o karakterin tarzına uygun sorularla öğrenme deneyimi yaşar.
- 🧠 **Sokratik Yöntemle Öğrenme:** Sistem, bilgi vermek yerine sadece sorular sorar. Bu da kullanıcıyı düşünmeye zorlar.
- 📊 **Oturum Takibi ve Puanlama:** Her konuşma oturumu kayıt altına alınır ve kullanıcı cevapları 1-5 arasında otomatik olarak puanlanır.
- 🔐 **Kayıt ve Giriş Sistemi:** Kullanıcılar kendi hesaplarıyla oturum açabilir ve geçmiş sohbetlerini görebilir.
- 🧠 **Gemini 1.5 Pro API Entegrasyonu:** Google’ın gelişmiş yapay zekâ modeli kullanılarak dinamik içerik üretimi sağlanır.

## 🛠️ Teknolojiler

- **Backend:** FastAPI, SQLite
- **Frontend:** HTML, CSS, Vanilla JS
- **AI Entegrasyonu:** Google Gemini 1.5 Pro API
- **Veritabanı Güvenliği:** bcrypt ile şifrelenmiş kullanıcı yönetimi
- **Veri Yönetimi:** Oturum geçmişi, mesajlar ve puanlar için ayrı tablolar

## 🚀 Kurulum

1. Bu repoyu klonlayın:
   ```bash
   git clone https://github.com/kullanici-adi/FeynmanChat.git
   cd FeynmanChat
   ```

2. Sanal ortam kurun ve gerekli bağımlılıkları yükleyin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. `.env` dosyasını oluşturun ve API anahtarınızı ekleyin:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

4. Sunucuyu başlatın:
   ```bash
   uvicorn main:app --reload
   ```

5. Uygulamayı açın: [http://localhost:8000](http://localhost:8000)

## 📁 Proje Yapısı

```
.
├── main.py                # FastAPI ana uygulama
├── gemini.py              # Gemini API ile konuşma ve puanlama
├── database.py            # SQLite işlemleri
├── schemas.py             # Pydantic veri modelleri
├── prompts.json           # Karakter bazlı prompt şablonları
├── templates/             # HTML şablonlar
├── static/                # CSS, JS, görseller
└── .env                   # API anahtarları (gizli tutulmalı)
```

`.gitignore` şu dosyaları dışlar:
```
.env
__pycache__/
*.db
```

## 👨‍💻 Takım Üyeleri (Grup 24)

- Oğuzhan Sarıgöl  
- Mine Kırmacı  
- Yiğit Alp Aslan  
- Gamze Yaş  
- Zeynep Demirel  

## 📜 Lisans

Bu proje yalnızca **hackathon** kapsamında değerlendirilmek üzere geliştirilmiştir.

---

🧠 “Bir şeyi gerçekten anladınız mı? Bir çocuğa anlatabiliyor musunuz?”

**FeynmanChat**, bu felsefeyle geliştirildi.
