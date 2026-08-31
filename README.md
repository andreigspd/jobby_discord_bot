# Jobby - LinkedIn IT Job Notifier Discord Bot

**Jobby** este un bot de Discord simplu și eficient specializat pe domeniul **IT / Software Engineering** care caută automat oferte de muncă pe **LinkedIn**, trimite notificări în timp real când apar joburi noi de IT și permite utilizatorilor să interacționeze cu joburile direct din Discord prin **butoane interactive** (📌 Selectat & ✅ Aplicat).

---

## ✨ Caracteristici principale

- 💻 **Filtrare exclusivă pentru IT**: Botul aplică automat filtre speciale de funcție de job și cuvinte-cheie din tehnologie (`f_F=it` + filtru titlu IT) pentru a elimina joburile din alte domenii (resurse umane, vânzări, șoferi etc.) și a afișa doar joburi de IT/Software!
- 🔍 **Căutare simplă**: Execută o singură comandă `!search <cuvinte_cheie> <locație>` (sau `/search`) pentru a găsi rapid oferte de IT pe LinkedIn.
- 🔄 **Notificări automate (Auto-Update)**: Botul salvează căutarea ta și verifică periodic (la fiecare 15 minute) în fundal dacă au apărut joburi noi de IT. Când găsește o ofertă nouă, trimite automat un card (embed) în canal!
- 📌 **Butoane interactive în Discord**:
  - 📌 **Selectează**: Marchează un job ca selectat/salvat. Numele tău va apărea în subsolul cardului din Discord!
  - ✅ **Aplicat**: Marchează jobul ca fiind aplicat, astfel încât colegii/prietenii din server să știe la ce joburi s-a aplicat deja.
- 💾 **Bază de date SQLite integrată**: Reține joburile deja notificate (pentru a evita duplicatele) și salvează starea selecțiilor și a căutărilor active chiar și după repornirea botului.
- 🛡️ **Fără autentificare LinkedIn**: Scrapează endpoint-ul public guest, eliminând riscul blocării contului personal de LinkedIn.

---

## 🛠️ Cerințe și Instalare

### 1. Clonarea proiectului & Instalarea dependențelor
Asigură-te că ai **Python 3.8+** instalat. Rulează în terminal:

```bash
git clone https://github.com/username/jobby.git
cd jobby
python -m pip install -r requirements.txt
```

### 2. Configurare mediu (`.env`)
Creează un fișier numit `.env` în rădăcina proiectului și adaugă Token-ul botului tău de Discord:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

> 💡 *Note*: Asigură-te că botul are activate permisiunile `Message Content Intent` și `Server Members Intent` din Discord Developer Portal.

### 3. Pornirea botului
Rulează comanda:

```bash
python main.py
```

---

## 🚀 Utilizare în Discord

### Căutare joburi IT și activare notificări:
Rulează în orice canal din serverul tău de Discord:

```text
!search "Python Developer" "Romania"
```
sau
```text
!search "Junior" "Remote"
```

1. Botul va afișa imediat ultimele joburi IT găsite pe LinkedIn sub formă de carduri elegante.
2. Botul va înregistra automat canalul pentru verificări automate de joburi IT în fundal la fiecare 15 minute.
3. Apasă pe butoanele **📌 Selectează** sau **✅ Aplicat** de sub orice job pentru a marca starea acestuia în conversație!

---

## 📁 Structura proiectului

```text
jobby/
├── main.py           # Logica botului de Discord, handler comenzi, UI View & task de fundal
├── scraper.py        # Web scraping & filtrare exclusivă IT pentru endpoint-ul public LinkedIn
├── database.py       # Interfață SQLite (jobs.db) pentru deduplicare și selecții utilizatori
├── requirements.txt   # Dependențele Python (discord.py, beautifulsoup4, requests, python-dotenv)
└── README.md         # Documentația proiectului
```

---

## 📄 Licență
Proiect creat cu scop educațional. Utilizați în conformitate cu termenii și condițiile de utilizare ale platformelor.
