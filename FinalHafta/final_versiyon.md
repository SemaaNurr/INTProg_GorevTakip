# 📌  Proje Başlığı

Görev Dağılım ve Takip Uygulaması

---

## 🧾 Proje Tanıtımı

Bu proje, takım üyeleri arasında görev dağılımını düzenli ve verimli bir şekilde yönetmeyi amaçlayan bir görev takip uygulamasıdır.
Kullanıcılar, projeler kapsamında görevler oluşturabilir ve her bir görevin durumunu "Yapılacak", "Devam Ediyor" ve "Tamamlandı" gibi kategorilerle takip edebilir. 
Böylece takım içindeki iş akışı şeffaf bir şekilde izlenebilir ve iş planlaması kolaylaşır.

---

## 🚀 Proje Özellikleri

- 🔐 Kullanıcı kayıt ve giriş işlemleri
- 📚 Yeni veri (Görev ekleme, görev listeleme, görev detaylarını görüntüleme)
- 📝 Verileri düzenleyebilme ve silebilme


---

## ⚙ Kurulum ve Çalıştırma

### ✅ Gereksinimler 

Bu projeyi çalıştırmak için bilgisayarınızda aşağıdaki yazılımlar kurulu olmalıdır:

-Python 3.7 veya daha üstü
-SQLite
-Visual Studio Code

Ayrıca aşağıdaki kütüphaneler kullanılmaktadır:
-Flask
-Flask-SQLAlchemy
-Pandas
-ReportLab
-Openpyxl
-Python’ın standart kütüphaneleri: os, json, hashlib, functools, io

### 🚀 Uygulamayı Başlatma

Uygulama tarayıcınızda http://127.0.0.1:5000 adresinde çalışacaktır.
Yayın (Render) Linki: https://gorevtakip.onrender.com/ 


## 📂 Proje Dosya Yapısı

Final_Hafta/
│
├── requirements.txt              # Gerekli Python kütüphaneleri listesi
│
└── Görev Takip/
    │
    ├── app.py                    # Ana Flask uygulama dosyası
    ├── kullanicilar.db           # SQLite veritabanı dosyası (otomatik oluşur)
    │
    ├── static/                   # Statik dosyalar (CSS, JS, font, resim)
    │   ├── style.css             # Projenin ana stil dosyası
    └── templates/                # HTML şablon dosyaları
        ├── base.html                 # Ortak şablon (navbar, footer, layout)
        ├── anasayfa.html             # Ana sayfa (proje tanıtımı/giriş)
        ├── giris.html                # Kullanıcı giriş formu
        ├── kayit.html                # Kullanıcı kayıt formu
        ├── dashboard.html            # Kullanıcıya özel panel ve görev listesi
        ├── panel.html                # Alternatif panel sayfası
        ├── gorev_ekle.html           # Yeni görev ekleme formu
        ├── gorev_duzenle.html        # Görev düzenleme formu
        ├── gorev_detay.html          # Görev detaylarını gösteren sayfa
        ├── gorev_liste.html          # Görevleri listeleme sayfası
        ├── kullanicilar.html         # Kullanıcıları listeleme sayfası
        ├── rapor.html                # Raporlama ana sayfası
        ├── hakkımızda.html           # Hakkımızda sayfası
        ├── iletisim.html             # İletişim sayfası
