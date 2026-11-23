import imaplib
import email
from email.header import decode_header
import re
import time


class ImapKodOkuyucu:
    """
    Özel alan adı (Catch-All) veya standart IMAP destekli e-posta kutularından
    gelen doğrulama kodlarını (4-8 haneli OTP) otomatik yakalayan modül.
    """

    def __init__(self, imap_sunucu: str, kullanici_mail: str, sifre: str, port: int = 993):
        self.imap_sunucu = imap_sunucu
        self.kullanici_mail = kullanici_mail
        self.sifre = sifre
        self.port = port

    def baglan(self):
        mail = imaplib.IMAP4_SSL(self.imap_sunucu, self.port)
        mail.login(self.kullanici_mail, self.sifre)
        return mail

    def _metni_coz(self, metin):
        if not metin:
            return ""
        parcalar = decode_header(metin)
        sonuc = ""
        for icerik, kodlama in parcalar:
            if isinstance(icerik, bytes):
                sonuc += icerik.decode(kodlama or "utf-8", errors="ignore")
            else:
                sonuc += icerik
        return sonuc

    def _govdeyi_al(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                icerik_turu = part.get_content_type()
                if icerik_turu in ["text/plain", "text/html"]:
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode("utf-8", errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8", errors="ignore")
        return ""

    def dogrulama_kodu_bekle(
        self,
        hedef_alici: str = None,
        gonderen_filtre: str = None,
        bekleme_suresi: int = 60,
        kontrol_araligi: int = 4,
    ):
        """
        Belirtilen süre boyunca gelen kutusunu tarar.
        Catch-All sistemlerde 'hedef_alici' parametresiyle hangi alt adrese gelen mailin
        okunacağını ayırt eder ve 4-8 haneli doğrulama kodunu döndürür.
        """
        baslangic = time.time()

        while time.time() - baslangic < bekleme_suresi:
            try:
                mail = self.baglan()
                mail.select("INBOX")

                # Okunmamış (UNSEEN) mailleri ara
                durum, mesajlar = mail.search(None, "UNSEEN")
                if durum == "OK" and mesajlar[0]:
                    mail_id_listesi = mesajlar[0].split()

                    # En yeni gelen mailden geriye doğru tara
                    for mail_id in reversed(mail_id_listesi):
                        _, veri = mail.fetch(mail_id, "(RFC822)")
                        ham_mail = veri[0][1]
                        msg = email.message_from_bytes(ham_mail)

                        alici = self._metni_coz(msg.get("To", "")).lower()
                        gonderen = self._metni_coz(msg.get("From", "")).lower()
                        konu = self._metni_coz(msg.get("Subject", ""))

                        # Catch-All alıcı kontrolü
                        if hedef_alici and hedef_alici.lower() not in alici:
                            continue

                        # Gönderen filtre kontrolü
                        if gonderen_filtre and gonderen_filtre.lower() not in gonderen:
                            continue

                        govde = self._govdeyi_al(msg)
                        tam_metin = f"{konu} {govde}"

                        # HTML etiketlerini temizle ve 4-8 haneli sayısal kodu yakala
                        temiz_metin = re.sub(r"<[^>]+>", " ", tam_metin)
                        eslesme = re.search(r"\b(\d{4,8})\b", temiz_metin)

                        if eslesme:
                            bulunan_kod = eslesme.group(1)
                            mail.logout()
                            return {
                                "basarili": True,
                                "kod": bulunan_kod,
                                "alici": alici,
                                "gonderen": gonderen,
                            }

                mail.logout()
            except Exception as hata:
                return {"basarili": False, "hata": str(hata)}

            time.sleep(kontrol_araligi)

        return {"basarili": False, "hata": "Belirtilen sürede doğrulama kodu bulunamadı."}


# --- HIZLI TEST VE KULLANIM ÖRNEĞİ ---
if __name__ == "__main__":
    print("✅ IMAP & Catch-All Kod Okuyucu Modülü yüklendi ve kullanıma hazır!")
    # Örnek kullanım:
    # okuyucu = ImapKodOkuyucu("://alanadiniz.com", "catchall@alanadiniz.com", "SIFRENIZ")
    # sonuc = okuyucu.dogrulama_kodu_bekle(hedef_alici="uye123@alanadiniz.com", bekleme_suresi=45)
    # print(sonuc)
