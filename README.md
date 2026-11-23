# 📧 IMAP & Catch-All E-posta Doğrulama Kodu (OTP) Okuyucu Modülü

Özel alan adı (**Catch-All**) veya standart **IMAP** destekli e-posta hesaplarına gelen doğrulama kodlarını (4-8 haneli OTP) otomatik olarak yakalayan, harici kütüphane gerektirmeyen modüler Python kütüphanesi.

## ✨ Özellikler
- **Sıfır Harici Bağımlılık:** Yalnızca Python standart kütüphaneleri (`imaplib`, `email`, `re`) ile yüksek hızda çalışır.
- **Catch-All Desteği:** Tek bir ana posta kutusuna düşen farklı alt adreslere (`hedef_alici`) gelen mailleri birbirine karıştırmadan filtreler.
- **Akıllı Kod Yakalama (Regex Parsing):** Hem düz metin (`text/plain`) hem de HTML e-posta gövdelerini temizleyerek doğrulama kodunu otomatik ayıklar.
