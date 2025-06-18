import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random
import os
import sys

# Lig logolarının yolu
LOGO_PATHS = {
    "Premier Lig": "logos/premier lig.png",
    "La Liga": "logos/la liga.png",
    "Bundesliga": "logos/bundesliga.png",
    "Ligue 1": "logos/ligue 1.png",
    "Serie A": "logos/serie A.png"
}

# Oyuncuları dosyadan yükleme
def load_players(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

# İsimleri temizleme (Türkçe karakterleri düzeltme)
def clean_name(name):
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    name = name.translate(table)
    name = name.lower()
    yeni = ""
    for harf in name:
        if harf.isalpha():
            yeni += harf
    return yeni

# Renkler
RENK_ARKA = "#1a2238"
RENK_KART = "#232b47"
RENK_YAZI = "#ffffff"
RENK_YUMUSAK = "#b2bacf"
RENK_VURGU = "#3559e0"
RENK_BUTON = "#4e65a3"
RENK_BASARILI = "#38b593"
RENK_KISMI = "#ffe082"
RENK_HATA = "#734b5e"

class PlayerGuessGame(tk.Tk):
    def __init__(self, datafile):
        super().__init__()
        self.title("Futbolcu Tahmin Oyunu")
        self.state("zoomed")
        self.config(bg=RENK_ARKA)
        self.players = load_players(datafile)
        self.logo_imgs = {}
        self.menu_frame = None
        self.game_frame = None
        self.menu_ekran()

    # Menü ekranı oluşturur
    def menu_ekran(self):
        if self.menu_frame:
            self.menu_frame.destroy()
        if self.game_frame:
            self.game_frame.destroy()

        self.menu_frame = tk.Frame(self, bg=RENK_ARKA)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        lbl = tk.Label(self.menu_frame, text="Bir Lig Seçin", font=("Arial", 30, "bold"), fg=RENK_VURGU, bg=RENK_ARKA)
        lbl.pack(pady=30)

        ligler = [lig for lig in LOGO_PATHS if any(p["lig"] == lig for p in self.players)]

        row = tk.Frame(self.menu_frame, bg=RENK_ARKA)
        row.pack(pady=20)

        for lig in ligler:
            img = Image.open(LOGO_PATHS[lig])
            img = img.resize((100, 100))
            tkimg = ImageTk.PhotoImage(img)
            self.logo_imgs[lig] = tkimg
            btn = tk.Button(row, image=tkimg, bg=RENK_KART, bd=0, command=lambda l=lig: self.oyun_baslat(l))
            btn.pack(side="left", padx=25)

    # Oyunu başlatır
    def oyun_baslat(self, lig):
        self.menu_frame.destroy()
        secili_oyuncular = [p for p in self.players if p["lig"] == lig]
        self.game_frame = GameFrame(self, secili_oyuncular, lig, self.menu_ekran)
        self.game_frame.place(relx=0.5, rely=0.5, anchor="center")

class GameFrame(tk.Frame):
    def __init__(self, master, havuz, lig, geri_don):
        super().__init__(master, bg=RENK_ARKA, width=1100, height=650)
        self.pack_propagate(0)
        self.havuz = havuz
        self.lig = lig
        self.geri_don = geri_don
        self.master = master

        self.ust = tk.Frame(self, bg=RENK_ARKA)
        self.ust.pack(pady=8, fill="x")

        self.lbl_hak = tk.Label(self.ust, text="", font=("Arial", 16, "bold"), bg=RENK_ARKA, fg=RENK_YUMUSAK)
        self.lbl_hak.pack(side="left", padx=20)

        self.lbl_lig = tk.Label(self.ust, text="Lig: " + lig, font=("Arial", 16, "bold"), bg=RENK_ARKA, fg=RENK_VURGU)
        self.lbl_lig.pack(side="right", padx=20)

        self.frm_kelime = tk.Frame(self, bg=RENK_ARKA)
        self.frm_kelime.pack(pady=20)

        self.frm_ipucu = tk.Frame(self, bg=RENK_KART)
        self.frm_ipucu.pack(pady=10)

        self.frm_tahmin = tk.Frame(self, bg=RENK_ARKA)
        self.frm_tahmin.pack(pady=10)

        self.btn_menu = tk.Button(self, text="Ana Menü", font=("Arial", 14), bg=RENK_BUTON, fg="white", command=self.geri_don)
        self.btn_menu.config(cursor="hand2")

        self.master.bind("<Key>", self.tus_basildi)
        self.yeni_tur()

    def yeni_tur(self):
        self.oyuncu = random.choice(self.havuz)
        self.cevap = clean_name(self.oyuncu["isim"])
        print("Cevap (debug):", self.cevap)  # Öğrenci debug çıktısı
        self.hak = 5
        self.harflar = [""] * len(self.cevap)
        self.kilitler = [None] * len(self.cevap)
        self.sira = 0
        self.ipucu_adim = 0
        self.frm_tahmin.destroy()
        self.frm_tahmin = tk.Frame(self, bg=RENK_ARKA)
        self.frm_tahmin.pack(pady=10)
        self.kelime_goster()
        self.ipucu_goster()
        self.lbl_hak.config(text="Kalan Hak: " + str(self.hak))
        self.btn_menu.place_forget()

    def kelime_goster(self):
        for w in self.frm_kelime.winfo_children():
            w.destroy()
        for i in range(len(self.harflar)):
            if self.kilitler[i]:
                harf = self.kilitler[i].upper()
                bg = RENK_BASARILI
            elif self.harflar[i]:
                harf = self.harflar[i].upper()
                bg = RENK_KART
            else:
                harf = "_"
                bg = RENK_KART
            lbl = tk.Label(self.frm_kelime, text=harf, width=2, font=("Consolas", 26, "bold"), bg=bg, fg=RENK_YAZI)
            lbl.pack(side="left", padx=5, ipadx=5, ipady=5)

    def ipucu_goster(self):
        for w in self.frm_ipucu.winfo_children():
            w.destroy()
        baslik = tk.Label(self.frm_ipucu, text="İpuçları", font=("Arial", 14, "bold"), bg=RENK_KART, fg=RENK_VURGU)
        baslik.pack(anchor="w", padx=8)

        ipuclar = [("Mevki", self.oyuncu["mevki"]),
                   ("Yaş", self.oyuncu["yaş"]),
                   ("Takım", self.oyuncu["takım"]),
                   ("Uyruk", self.oyuncu["uyruk"])]
        for i in range(min(self.ipucu_adim, 4)):
            satir = tk.Label(self.frm_ipucu, text=f"{ipuclar[i][0]}: {ipuclar[i][1]}", font=("Arial", 12), bg=RENK_KART, fg=RENK_YUMUSAK)
            satir.pack(anchor="w", padx=16)

        if self.hak == 0:
            dogru = tk.Label(self.frm_ipucu, text="Doğru: " + self.oyuncu["isim"], font=("Arial", 13, "bold"), bg=RENK_KART, fg=RENK_KISMI)
            dogru.pack(anchor="w", padx=8, pady=6)

    def tus_basildi(self, e):
        if self.hak == 0:
            return
        if e.keysym == "BackSpace":
            while self.sira > 0 and self.kilitler[self.sira - 1]:
                self.sira -= 1
            if self.sira > 0:
                self.sira -= 1
            self.harflar[self.sira] = ""
            self.kelime_goster()
        elif e.keysym == "Return":
            if "" not in self.harflar:
                self.kontrol_et()
        elif e.char.isalpha():
            while self.sira < len(self.harflar) and self.kilitler[self.sira]:
                self.sira += 1
            if self.sira < len(self.harflar):
                self.harflar[self.sira] = clean_name(e.char)[0]
                self.sira += 1
                self.kelime_goster()
            if "" not in self.harflar:
                self.kontrol_et()

    def kontrol_et(self):
        tahmin = ''.join([self.kilitler[i] if self.kilitler[i] else self.harflar[i] for i in range(len(self.cevap))])
        print("Tahmin:", tahmin)
        renkler = [RENK_HATA] * len(self.cevap)
        kalan = {}
        for harf in self.cevap:
            kalan[harf] = kalan.get(harf, 0) + 1

        for i in range(len(tahmin)):
            if tahmin[i] == self.cevap[i]:
                renkler[i] = RENK_BASARILI
                kalan[tahmin[i]] -= 1

        for i in range(len(tahmin)):
            if renkler[i] == RENK_HATA and tahmin[i] in kalan and kalan[tahmin[i]] > 0:
                renkler[i] = RENK_KISMI
                kalan[tahmin[i]] -= 1

        satir = tk.Frame(self.frm_tahmin, bg=RENK_ARKA)
        for i in range(len(tahmin)):
            lbl = tk.Label(satir, text=tahmin[i].upper(), width=2, font=("Consolas", 17, "bold"),
                           bg=renkler[i], fg="black")
            lbl.pack(side="left", padx=3, ipadx=3, ipady=4)
        satir.pack(pady=2)

        for i in range(len(tahmin)):
            if renkler[i] == RENK_BASARILI:
                self.kilitler[i] = tahmin[i]

        self.harflar = [self.kilitler[i] if self.kilitler[i] else "" for i in range(len(self.cevap))]
        self.sira = 0
        self.kelime_goster()

        if tahmin == self.cevap:
            messagebox.showinfo("Tebrikler", "Cevap doğru: " + self.oyuncu["isim"])
            self.yeni_tur()
            return

        self.hak -= 1
        self.lbl_hak.config(text="Kalan Hak: " + str(self.hak))
        self.ipucu_adim = 5 - self.hak
        self.ipucu_goster()

        if self.hak == 0:
            self.btn_menu.place(relx=0.5, rely=0.93, anchor="center")

# Programı başlat
if __name__ == "__main__":
    dosya = "secili_takim_oyuncular.json"
    if not os.path.isfile(dosya):
        tk.Tk().withdraw()
        messagebox.showerror("Hata", f"{dosya} bulunamadı.")
        sys.exit()
    app = PlayerGuessGame(dosya)
    app.mainloop()
