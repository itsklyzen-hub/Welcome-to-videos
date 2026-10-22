# Styles musique par pays — recettes audio "Welcome To"

Règles communes à toutes les musiques :
- 100 % original et libre de droits : tout est synthétisé en numpy. Pas d'échantillon d'un vrai enregistrement, pas de mélodie ni de chanson existante (ne pas citer d'hymne ni de chanson traditionnelle connue).
- Tempo 120 BPM, tout sur la grille : le temps dure 0,5 s, la mesure 2 s.
- Structure :
  - 0-3 s : intro + 2 impacts (0,5 s et 1,5 s)
  - 3-8 s : build-up, avec roulement + riser de 6 à 7,875 s, puis un silence de 1/8 de temps
  - 8,0 s : boom du drop
  - après le drop : groove moderne (kick 4/4, clap sur 2 et 4, hats en contretemps, basse)
  - un whoosh sur chaque coupe
  - impact de fin quand le nom du pays revient (~1 s après la dernière coupe)
  - fondu de 0,45 s sur la fin, pour la boucle
- La même mélodie « pays » passe du build au drop : elle est jouée doucement dans le build, puis plus fort et doublée à l'octave après le drop, au-dessus du beat moderne.
- Mix : normalisé à -14 LUFS (loudnorm en deux passes, TP -1,5). Le build doit être environ 6 dB en dessous du drop, pas plus.
- Code de référence : `audio_italie.py`, qui contient :
  - une corde pincée Karplus-Strong (`ks`, `mandolin_note`)
  - une anche (`reed`)
  - un tambourin, un kick, un clap, une conga, une basse afro-house, des whooshes
  - Pour un autre pays, on copie le fichier et on change l'instrument « pays », la gamme ou les accords, et le motif de percussion.

| Pays | Instrument(s) principal(aux) | Gamme / accords | Rythme / percussion « pays » | Après le drop |
|---|---|---|---|---|
| **Portugal** | Guitare portugaise : Karplus-Strong brillant, doublé en cordes métal (détune ±6 cents), arpèges en doubles croches. Pad discret de guitare classique. | Mi mineur ou la mineur, mélancolique façon fado : i-iv-V7-i, avec un VI au passage | Peu de percussion avant le drop, juste des pincements et des notes de basse sur les temps | Kick/clap/hats, l'arpège de guitare reste en avant |
| **Italie** (fait) | Mandoline en trémolo (KS, double corde, 16 attaques/s), accordéon (scies désaccordées + carré, battement musette ±9 cents, passe-bas 1,8 kHz) | La mineur harmonique : i-iv-V7-i (Am-Dm-E7-Am) | Tarentelle : tambourin en triolets sur le temps (sensation 6/8), oom-pah d'accordéon | Italo-dance / afro-house : congas, basse syncopée, mandoline doublée à l'octave |
| **Espagne** | Guitare flamenca : rasgueado, c'est-à-dire 4-5 attaques KS très rapides (~15 ms d'écart) par accord, avec des étouffés | Cadence andalouse en mi phrygien : Am-G-F-E | Palmas : claps courts filtrés 1-4 kHz sur le compás 12 temps, ou plus simple avec des accents 3+3+2 | Reggaeton léger ou house, palmas gardées |
| **Grèce** | Bouzouki : KS très brillant, cordes doublées à l'octave, trémolo | Ré mineur ou mode hijaz (seconde augmentée : ré-mi♭-fa♯-sol-la) | Rythme 9/8 évoqué en accents 2+2+2+3, ou hasapiko en 4/4 | House, bouzouki en trémolo par-dessus |
| **Japon** | Koto (KS doux, attaque piquée, legato par pitch-bend), shamisen (KS sec, décroissance courte) | Pentatonique in-sen (mi-fa-la-si-ré) ou hirajōshi | Taiko : grosse caisse grave à 60-80 Hz + bois (clic filtré) | Trap ou future-bass, koto en pizzicato |
| **Brésil** | Guitare nylon bossa (KS doux, accords de 7e et 9e), cuíca possible (sinus glissé) | Majeur jazzy : ii7-V7-Imaj7 | Samba : surdo (sinus grave sur le 2), tamborim en doubles croches, shaker | Funk carioca ou afro-house, garder surdo et shaker |
| **Mexique** | Trompettes mariachi : cuivre = scie + passe-bas qui s'ouvre à l'attaque, vibrato 6 Hz, en tierces parallèles. Guitarrón : basse KS grave. | Majeur : I-IV-V7 | Son / huapango : sensation 6/8, guitare rythmique vihuela en rasgueado | Cumbia-house ou reggaeton, trompettes sur les refrains |
| **Irlande** | Tin whistle (sinus + souffle bruité filtré, ornements) et violon (scie + vibrato + attaque d'archet) | Ré majeur ou mi dorien | Gigue en 6/8 : triolets sur le temps, bodhrán (tom grave + frottement) | House, mélodie de gigue gardée en triolets |
| **Inde** | Sitar (KS avec « jawari » : une légère distorsion en tanh qui fait buzzer, sympathiques résonantes), tanpura en bourdon (Sa-Pa en continu) | Raga-like : mode bhairav ou kafi, bourdon sur la tonique | Tabla : « na » aigu (sinus 400-600 Hz glissé) + « ge » grave (sinus glissé 80-120 Hz), motifs teental | Bhangra : dhol (tom grave + claquement aigu) sur kick 4/4 |
| **Maroc** | Oud (KS grave, moyennement brillant, pas de frettes = petits glissés), ney (souffle + sinus) | Hijaz (ré-mi♭-fa♯-sol-la-si♭-do) | Darbuka : « doum » grave + « tek » sec, motif maqsoum (D-T-T-D-T) | Afro-house / raï-électro, darbuka gardée |
| **USA** | Country : guitare acoustique (KS en strum), banjo (KS très brillant, roll en doubles croches), slide (glissés). Ou pads trap. | Majeur : I-V-vi-IV (progression générique, aucune mélodie connue) | Country : train beat (caisse claire en doubles croches balais) | Trap : 808 grave glissé, hats en triolets ou rolls, snare sur le 3 |
| **France** | Accordéon musette (même `reed`, battement plus marqué ±15 cents), guitare manouche en « pompe » | La mineur ou ré mineur, harmonie valse-musette (i-iv-V7-i) | Valse 3/4 évoquée par basse + 2 accords, sur le grid 120 BPM : temps 1 basse, 2-3 accords | French touch : kick + basse filtrée (filtre qui s'ouvre), accordéon en boucle |

## Pays non listé : règle générique
1. Identifier un ou deux instruments emblématiques du pays et un rythme traditionnel. On les évoque avec une synthèse simple :
   - cordes pincées → Karplus-Strong
   - vents/anches → scie ou carré filtrés + vibrato + souffle
   - percussions → sinus glissés + bruit filtré
2. Prendre une gamme ou un mode typique (mineur, phrygien, pentatonique…) et des accords simples sur 4 mesures. Écrire une mélodie ORIGINALE de 4 mesures sur ces accords.
3. Avant le drop : l'instrument « pays » seul + le rythme traditionnel.
4. Après le drop : la même mélodie sur un beat moderne (house, afro-house, trap ou reggaeton selon ce qui colle à la culture), toujours à 120 BPM.
5. Vérifier :
   - les niveaux par seconde : build ≈ -24 dB RMS, drop ≈ -17 dB avant loudnorm
   - l'accordage : regarder les pics du spectre
   - -14 LUFS final
   - toutes les coupes sur la grille de 0,5 s
