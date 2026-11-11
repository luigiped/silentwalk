# Istruzioni operative · Silent Walk

URL pubblico (quello contenuto nel QR): **https://luigiped.github.io/silentwalk/**

Tutti i comandi si lanciano dal Terminale nella cartella del progetto:

```bash
cd ~/Sviluppo/Free\ Space
```

---

## 1. Perché il QR stampato non cambia mai

Il QR contiene **solo l'indirizzo** `https://luigiped.github.io/silentwalk/`, non la pagina, né l'audio, né il codice.
Puoi quindi modificare testi, grafica, codice e traccia fino all'ultimo minuto: chi scansiona trova sempre
la versione più recente pubblicata.

Il QR smette di funzionare **solo** se cambia l'indirizzo. Quindi **non** fare mai:

- rinominare il repo `silentwalk` o l'account GitHub `luigiped`;
- spostare il repo in un'organizzazione o in un altro account;
- impostare un dominio personalizzato in *Settings → Pages*;
- spostare `index.html` dalla radice del repo o cambiare il branch pubblicato (`main`, cartella `/`).

Disattivare e riattivare Pages (vedi punto 5) **non** cambia l'indirizzo.

> Non rigenerare il QR dopo averlo stampato: non serve. Se lo rigeneri con lo stesso URL ottieni comunque un QR equivalente.

---

## 2. Pubblicare una modifica qualsiasi (testi, grafica, codice)

1. Modifica i file (`index.html`, `css/style.css`, `js/app.js`).
2. Prova in locale:
   ```bash
   python3 scripts/serve.py 8000
   ```
   Apri `http://localhost:8000/` sul Mac oppure `http://IP-DEL-MAC:8000/` dal telefono, sulla stessa Wi-Fi.
   L'IP del Mac si trova con `ipconfig getifaddr en0`. Per fermare il server premi `Ctrl+C`.
3. Pubblica:
   ```bash
   git add -A
   git commit -m "Descrizione della modifica"
   git push
   ```
4. Attendi 1-2 minuti e controlla lo stato (deve dire `built`):
   ```bash
   gh api repos/luigiped/silentwalk/pages -q .status
   ```
5. Ricarica la pagina sul telefono. GitHub Pages può servire la versione precedente per **fino a 10 minuti**
   (cache): per l'ultima modifica il giorno dell'evento tieniti almeno 15 minuti di margine.

---

## 3. Cambiare la traccia audio (senza rompere il link)

La pagina carica sempre `assets/traccia.mp3`. Basta sostituire quel file **mantenendo lo stesso nome**.

### 3a. Preparare il nuovo MP3

Serve il nuovo file sorgente (MP3, WAV, M4A…). Senza ffmpeg, con gli strumenti di macOS:

```bash
# 1) decodifica in WAV 44,1 kHz stereo (macOS, nessuna installazione)
afconvert -f WAVE -d LEI16@44100 -c 2 "/percorso/NUOVA traccia.mp3" /tmp/src.wav

# 2) codifica MP3 CBR 96 kbps (una tantum: python3 -m pip install --user lameenc)
python3 scripts/encode_lame.py /tmp/src.wav assets/traccia.mp3 96

# 3) controlla durata e bitrate
afinfo assets/traccia.mp3 | grep -E "duration|bit rate"
ls -lh assets/traccia.mp3
```

Se hai ffmpeg installato, puoi fare tutto in un passo: `scripts/encode_audio.sh "/percorso/NUOVA traccia.wav"`.

Regole:
- **Dimensione sotto i 50 MB** (GitHub rifiuta oltre 100 MB). 35 minuti a 96 kbps ≈ 25 MB.
  Se è troppo grande usa 64 kbps: `python3 scripts/encode_lame.py /tmp/src.wav assets/traccia.mp3 64`.
- Niente Git LFS: l'MP3 va committato come file normale.
- Ascolta il file prima di pubblicarlo.

### 3b. Forzare i telefoni a scaricare la nuova traccia

In `index.html` cerca questa riga:

```html
<audio id="a" preload="metadata" playsinline data-src="assets/traccia.mp3?v=1"></audio>
```

e **aumenta il numero** dopo `?v=` (es. `?v=2`, poi `?v=3`…). In questo modo i telefoni che avevano già aperto
la pagina non usano la vecchia traccia dalla cache. L'URL della pagina (e quindi il QR) non cambia.

### 3c. Pubblicare e verificare

```bash
git add -A
git commit -m "Nuova traccia audio"
git push
```

Dopo 1-2 minuti:

```bash
# deve rispondere "HTTP/2 206" e la nuova dimensione dopo lo "/"
curl -s -o /dev/null -D - -H "Range: bytes=0-1" https://luigiped.github.io/silentwalk/assets/traccia.mp3 | grep -iE "^HTTP|content-range"
```

Poi apri la pagina dal telefono e controlla che la durata mostrata sotto il player sia quella nuova.

> Il repo conserva anche le vecchie versioni dell'MP3 nella cronologia: dopo molte sostituzioni può crescere.
> Non è un problema per la pagina, ma se il push diventa lento conviene ricreare il repo dopo l'evento.

---

## 4. Rigenerare i QR (solo se servisse una nuova copia del file)

```bash
python3 -m pip install --user segno pillow    # una tantum
python3 scripts/make_qr.py https://luigiped.github.io/silentwalk/
```

Output in `qr/`:
- `qr-silentwalk-freespace.svg` / `.png`: personalizzato con i colori FreeSpace e il logo al centro;
- `qr-silentwalk.svg` / `.png`: classico nero su bianco, da tenere come riserva.

Il QR personalizzato usa la correzione d'errore H (30%). Il logo copre circa il 5% del codice e i colori sono
scuri a sufficienza per i lettori. Prima di mandare in stampa fai comunque una prova di scansione con 2-3 telefoni
diversi (iPhone e Android) dalla stampa reale. Stampa sempre su **fondo bianco**, lato minimo 4×4 cm
(almeno 10×10 cm se va letto a 2-3 metri), senza tagliare il margine bianco attorno.

---

## 5. Prima e dopo l'evento

Spegnere la pagina (per esempio subito dopo il collaudo) e riaccenderla la mattina del 20. L'URL resta lo stesso:

```bash
# spegni
gh api -X DELETE repos/luigiped/silentwalk/pages

# riaccendi (poi attendi 1-2 minuti)
gh api -X POST repos/luigiped/silentwalk/pages -f "source[branch]=main" -f "source[path]=/"
```

Smontaggio definitivo dopo l'evento:

```bash
gh auth refresh -h github.com -s delete_repo     # una tantum, serve il permesso di eliminare
gh repo delete luigiped/silentwalk --yes
```

La pagina mostra comunque "L'evento è concluso. Grazie." e non carica più l'audio dopo il 21/11/2026 alle 00:00.
Per spostare questa data modifica `EVENT_END` in `js/app.js`.
