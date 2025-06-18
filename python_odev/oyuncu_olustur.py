import requests
import json
import time
import os
from datetime import datetime

API_KEY = "43ae159a1a184dddb1dcc2221c71d9f8"
headers = {"X-Auth-Token": API_KEY}

takimlar = {
    # Premier Lig
    "Arsenal": 57,
    "Manchester City": 65,
    "Manchester United": 66,
    "Liverpool": 64,
    "Tottenham": 73,
    # La Liga
    "Real Madrid": 86,
    "Barcelona": 81,
    "Atletico Madrid": 78,
    # Bundesliga
    "Bayern Münih": 5,
    "Borussia Dortmund": 4,
    "Bayer Leverkusen": 3,
    # Serie A
    "Juventus": 109,
    "Napoli": 113,
    "Inter": 108,
    "Milan": 98,
    # Ligue 1
    "PSG": 524,
    "Marsilya": 516
}

takim_ligleri = {
    "Arsenal": "Premier Lig",
    "Manchester City": "Premier Lig",
    "Manchester United": "Premier Lig",
    "Liverpool": "Premier Lig",
    "Tottenham": "Premier Lig",
    "Real Madrid": "La Liga",
    "Barcelona": "La Liga",
    "Atletico Madrid": "La Liga",
    "Bayern Münih": "Bundesliga",
    "Borussia Dortmund": "Bundesliga",
    "Bayer Leverkusen": "Bundesliga",
    "Juventus": "Serie A",
    "Napoli": "Serie A",
    "Inter": "Serie A",
    "Milan": "Serie A",
    "PSG": "Ligue 1",
    "Marsilya": "Ligue 1"
}

oyuncular = []
dosya_adi = "secili_takim_oyuncular.json"

# 1. Daha önce çekilmiş oyuncuları yükle
if os.path.exists(dosya_adi):
    with open(dosya_adi, "r", encoding="utf-8") as f:
        oyuncular = json.load(f)
else:
    oyuncular = []

# 2. Hangi takımlar zaten kaydedilmiş kontrol et
kayitli_takimlar = set(oyuncu["takım"] for oyuncu in oyuncular)
eksik_takimlar = [takim for takim in takimlar if takim not in kayitli_takimlar]

print(f"Zaten çekilmiş takımlar: {sorted(kayitli_takimlar)}")
print(f"Çekilecek (eksik) takımlar: {eksik_takimlar}")

def yas_hesapla(dogum_tarihi):
    try:
        yil = int(dogum_tarihi[:4])
        ay = int(dogum_tarihi[5:7])
        gun = int(dogum_tarihi[8:10])
        bugun = datetime.now()
        yas = bugun.year - yil - ((bugun.month, bugun.day) < (ay, gun))
        return yas
    except:
        return None

for takim_adi in eksik_takimlar:
    takim_id = takimlar[takim_adi]
    print(f"\n{takim_adi} için oyuncular çekiliyor...")
    url = f"https://api.football-data.org/v4/teams/{takim_id}"
    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        time.sleep(1)
    except Exception as e:
        print(f"İstek hatası ({takim_adi}): {e}")
        continue

    # API limiti veya başka hata mesajı kontrolü
    if "message" in data:
        print(f"{takim_adi} için hata: {data['message']}")
        break  # Limit dolduysa burada dur ve tekrar devam et
    squad = data.get("squad", [])
    if not squad:
        print(f"UYARI: {takim_adi} ({takim_id}) için hiç oyuncu verisi gelmedi!")
        continue

    print(f"  Çekilen oyuncu sayısı: {len(squad)}")
    for player in squad:
        oyuncu = {
            "isim": player.get("name"),
            "yaş": yas_hesapla(player.get("dateOfBirth", "")),
            "takım": takim_adi,
            "mevki": player.get("position"),
            "uyruk": player.get("nationality"),
            "lig": takim_ligleri.get(takim_adi, "")
        }
        oyuncular.append(oyuncu)

# 3. Dosyaya kaydet (her denemede güncellenir)
with open(dosya_adi, "w", encoding="utf-8") as f:
    json.dump(oyuncular, f, ensure_ascii=False, indent=2)

print(f"\nBitti! Toplam {len(oyuncular)} oyuncu kaydedildi.")
print(f"JSON dosyan güncellendi: {dosya_adi}")
