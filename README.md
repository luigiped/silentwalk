# Silent Walk · FreeSpace APS

Landing page statica per la silent walk "Camminiamo insieme: voci contro il silenzio" (Cariati, 20 novembre 2026).
HTML + CSS + JS senza framework né build step, servita da GitHub Pages. Nessun tracker, cookie o richiesta esterna
(c'è anche una Content-Security-Policy che consente solo risorse dello stesso dominio).

## Struttura

- `index.html`, `css/style.css`, `js/app.js`: la pagina (loader → logo → landing con player).
- `assets/traccia.mp3`: traccia MP3 CBR 96 kbps (file normale, **niente Git LFS**).
- `assets/logo-freespace.png`, `cover-512.png`, `icon-180.png`, `favicon.png`: derivati dal logo.
- `scripts/encode_audio.sh`: ricodifica dell'audio con ffmpeg.
- `scripts/encode_lame.py`: alternativa senza ffmpeg (afconvert di macOS + LAME), usata per la traccia attuale.
- `scripts/serve.py`: server locale con Range/206 (per provare da iPhone in Wi-Fi).
- `scripts/make_qr.py`: QR (correzione H, quiet zone 4) in `qr/` come SVG e PNG, classico e personalizzato FreeSpace con logo.

**Istruzioni operative** (cambiare la traccia, pubblicare modifiche, QR, smontaggio): vedi [ISTRUZIONI.md](ISTRUZIONI.md).

## Note tecniche

- Solo elemento `<audio>` (niente Web Audio API, niente Wake Lock): l'audio prosegue a schermo bloccato.
- `play()` è chiamato in modo sincrono nel tap. Media Session con titolo, artwork e ±15 s sulla schermata di blocco.
- La sorgente audio è impostata da JS (`data-src`), così dopo `EVENT_END` (in `js/app.js`) l'MP3 non viene nemmeno richiesto.

## Comandi

```bash
scripts/encode_audio.sh "~/Desktop/Camminiamo insieme .mp3"   # --mono / --loudnorm opzionali
python3 scripts/serve.py 8000                                   # test locale (Range 206)
python3 scripts/make_qr.py https://UTENTE.github.io/silentwalk/
```

## Smontaggio dopo l'evento

```bash
gh api -X DELETE repos/UTENTE/silentwalk/pages     # spegne la pagina (ripubblicabile, stesso URL)
gh repo delete UTENTE/silentwalk --yes             # oppure elimina il repo
```
..
