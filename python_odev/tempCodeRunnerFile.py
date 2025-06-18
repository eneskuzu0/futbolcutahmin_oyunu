import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random
import unicodedata

# Lig logolarının dosya yolları
LOGO_YOLLARI = {
    "Premier Lig": "logos/premier lig.png",
    "La Liga": "logos/la liga.png",
    "Bundesliga": "logos/bundesliga.png",
    "Ligue 1": "logos/ligue 1.png",
    "Serie A": "logos/serie A.png"
}

# JSON dosyasından oyuncu verilerini yüklüyoruz
def oyunculari_yukle(dosya_adi):
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Hata", f"{dosya_adi} bulunamadı!")
        return {}

# Türkçe karakterleri sadeleştirerek harf karşılaştırması için temizlik fonksiyonu
def isim_temizle(isim):
    ceviri = str.maketrans("çğıöşü", "cgiosu")
    isim = isim.translate(ceviri).lower()
    temiz = ""
    for harf in isim:
        if harf.isalpha():
            temiz += harf
    return temiz

# Ana oyun sınıfı (Wordle benzeri futbolcu tahmin oyunu)
class TahminOyunu(tk.Tk):
    def __init__(self, json_dosyasi):
        super().__init__()
        self.title("Futbolcu Tahmin Oyunu")
        self.config(bg="#f4f4f4")
        self.geometry("600x500")
        self.veriler = oyunculari_yukle(json_dosyasi)
        self.secili_lig = None
        self.tahmin_hakki = 5
        self.aktif_oyuncu = None
        self.ipucu_durumu = 0
        self.tahmin_edilenler = []

        self.logo_resimleri = {}
        self.ana_ekrani_olustur()

    # Lig seçme ekranını oluşturur
    def ana_ekrani_olustur(self):
        self.temizle()
        tk.Label(self, text="Lig Seç", font=("Arial", 18), bg="#f4f4f4").pack(pady=10)

        for lig in LOGO_YOLLARI:
            try:
                resim = Image.open(LOGO_YOLLARI[lig]).resize((100, 100))
                self.logo_resimleri[lig] = ImageTk.PhotoImage(resim)
                btn = tk.Button(self, image=self.logo_resimleri[lig], command=lambda l=lig: self.oyunu_baslat(l))
                btn.pack(pady=5)
            except:
                tk.Label(self, text=lig, font=("Arial", 14), bg="#f4f4f4").pack(pady=5)

    # Oyunu başlatır
    def oyunu_baslat(self, lig_adi):
        if not self.veriler.get(lig_adi):
            messagebox.showwarning("Uyarı", f"{lig_adi} için oyuncu verisi yok.")
            return
        self.secili_lig = lig_adi
        self.aktif_oyuncu = random.choice(self.veriler[lig_adi])
        self.tahmin_hakki = 5
        self.ipucu_durumu = 0
        self.tahmin_edilenler = []
        self.oyun_ekrani_olustur()

    # Oyun ekranı tasarımı
    def oyun_ekrani_olustur(self):
        self.temizle()
        tk.Label(self, text=f"Lig: {self.secili_lig}", font=("Arial", 14), bg="#f4f4f4").pack(pady=5)
        self.hak_label = tk.Label(self, text=f"Kalan Hak: {self.tahmin_hakki}", font=("Arial", 12), bg="#f4f4f4")
        self.hak_label.pack()

        self.giris = tk.Entry(self, font=("Arial", 14))
        self.giris.pack(pady=10)

        tk.Button(self, text="Tahmin Et", command=self.tahmini_kontrol_et).pack()

        self.sonuc_label = tk.Label(self, text="", font=("Arial", 12), bg="#f4f4f4")
        self.sonuc_label.pack(pady=10)

        self.ipucu_label = tk.Label(self, text="", font=("Arial", 12), bg="#f4f4f4", fg="darkblue")
        self.ipucu_label.pack()

    # Kullanıcının tahminini kontrol eder
    def tahmini_kontrol_et(self):
        tahmin = self.giris.get()
        temiz_tahmin = isim_temizle(tahmin)
        temiz_gercek = isim_temizle(self.aktif_oyuncu["isim"])

        if temiz_tahmin == temiz_gercek:
            self.oyun_bitti(f"Tebrikler! Doğru tahmin: {self.aktif_oyuncu['isim']}")
        else:
            self.tahmin_hakki -= 1
            self.hak_label.config(text=f"Kalan Hak: {self.tahmin_hakki}")
            self.giris.delete(0, tk.END)

            if self.tahmin_hakki == 0:
                self.oyun_bitti(f"Bilemedin! Cevap: {self.aktif_oyuncu['isim']}")
            else:
                self.ipucu_goster()

    # İpucu gösterme mantığı
    def ipucu_goster(self):
        ipuclar = ["mevki", "yas", "takim", "uyruk"]
        if self.ipucu_durumu < len(ipuclar):
            alan = ipuclar[self.ipucu_durumu]
            deger = self.aktif_oyuncu.get(alan, "Bilinmiyor")
            self.ipucu_label.config(text=f"İpucu: {alan.capitalize()} - {deger}")
            self.ipucu_durumu += 1
        else:
            self.ipucu_label.config(text="Başka ipucu kalmadı.")

    # Oyun bitince ekran
    def oyun_bitti(self, mesaj):
        self.temizle()
        tk.Label(self, text=mesaj, font=("Arial", 14), bg="#f4f4f4").pack(pady=20)
        tk.Button(self, text="Ana Menüye Dön", command=self.ana_ekrani_olustur).pack(pady=10)

    # Ekranı temizler
    def temizle(self):
        for widget in self.winfo_children():
            widget.destroy()

# Oyunu çalıştır
if __name__ == "__main__":
    app = TahminOyunu("oyuncular.json")
    app.mainloop()
