# Outils de montage « Welcome To »

Scripts de référence de l'edit « Welcome to Italie » (modèle validé), à copier et adapter pour chaque nouvel edit.

- `render.py` : rendu des images (1080x1920, 30 fps) écrites sur stdout pour ffmpeg. À adapter :
  - `PH` : dossier des photos 01.jpg … NN.jpg
  - `CUTS`, `TRANS`, `ORDER`, `MOVES`, `DUR`, `END_POP` : timeline (120 BPM, drop à 8.0 s)
  - `FLAG` et le texte `'ITALIE'` : nom du sujet EN FRANÇAIS et ses couleurs
  - `python3 render.py still 1.6 8.03 …` sort des images fixes pour vérifier
- `audio_italie.py` : musique originale de style italien (tarentelle puis drop dance). Exemple de musique typique d'un pays.
- `audio_beat_generique.py` : beat générique 120 BPM (pad, arpège, riser, boom, kick/clap/hats).
- `styles_musique_pays.md` : recette musicale par pays (et règle générique) pour composer une musique originale typique.
- `build.sh` : génère la musique, rend la vidéo sans son, puis mixe avec loudnorm -14 LUFS.

Les vidéos à publier vont dans `videos/AAAA-MM-JJ_Sujet.mp4` (moins de 20 Mo). Metricool les récupère via
`https://raw.githubusercontent.com/itsklyzen-hub/welcome-to-videos/main/videos/<fichier>`.
