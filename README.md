# Foto-Schärfer

Ein Programm, in das du Fotos einfügst. Es erkennt die unscharfen Ebenen (Bereiche) im Bild und schärft sie nach. Scharfe Bereiche bleiben unverändert.

Das Programm ist die Datei `index.html`. Sie läuft im Browser, auch ohne Internet. Nur die wahlweise Gesichts-KI lädt zusätzliche Dateien aus dem Ordner `gesichts-ki/`. Deine Fotos werden nirgendwohin hochgeladen, alles wird auf deinem Gerät berechnet.

## Online nutzen

Wenn du GitHub Pages für dieses Repository einschaltest (Settings → Pages → Branch `main`, Ordner `/ (root)`), läuft das Programm unter `https://fabulousteaching.github.io/Deblur/`. Auch dort wird alles im Browser berechnet, und die Fotos werden nicht hochgeladen.

## Benutzen

1. `index.html` im Browser öffnen (Doppelklick genügt; Chrome, Edge, Firefox oder Safari).
2. Fotos einfügen. Dafür gibt es drei Wege:
   - ins Fenster ziehen,
   - mit «Fotos hinzufügen» auswählen,
   - mit `Strg` + `V` (Mac: `⌘` + `V`) aus der Zwischenablage einfügen.
3. Das Programm erkennt automatisch die Unschärfe und schärft das Foto.
4. Mit dem Regler im Bild vergleichst du Vorher und Nachher. Mit dem Mausrad zoomst du, und mit gedrückter Maustaste verschiebst du das Bild. Ein Doppelklick wechselt zwischen 1:1 und dem ganzen Bild.
5. Mit «Herunterladen» speicherst du das Ergebnis als `name-scharf.jpg`, `.png` oder `.webp`. Mit «Alle schärfen» werden alle eingefügten Fotos nacheinander geschärft und gespeichert.

## Die Ebenen

| Ebene | Geschätzte Unschärfe* | Standard |
|---|---|---|
| Scharf | unter 1.3 px | bleibt unverändert |
| Leicht unscharf | 1.3 – 2.3 px | wird geschärft |
| Unscharf | 2.3 – 3.8 px | wird geschärft |
| Stark unscharf | 3.8 – 6.0 px | wird geschärft |
| Sehr unscharf | über 6.0 px | wird geschärft |

\* Gemeint ist die Breite der Unschärfe (Gauss-Radius) in Pixeln. Die Grenzen verschieben sich mit dem Regler «Empfindlichkeit».

In der Ansicht **Ebenen** siehst du die Bereiche farbig. Mit den Häkchen wählst du, welche Ebenen geschärft werden. Soll zum Beispiel ein absichtlich unscharfer Hintergrund (Bokeh) so bleiben, nimmst du die Häkchen bei «Stark unscharf» und «Sehr unscharf» weg.

## Einstellungen

- **Empfindlichkeit:** Ab welcher Unschärfe ein Bereich als «unscharf» gilt.
- **Stärke:** Wie kräftig nachgeschärft wird.
- **Rauschschutz:** Höher bedeutet weniger verstärktes Bildrauschen und weniger Säume an Kanten, dafür wird das Ergebnis etwas weicher.
- **KI-Details (experimentell):** Zusätzlich ergänzt ein neuronales Netz Feinheiten, die in der Unschärfe verloren gingen, zum Beispiel Augen, Brauen und Lippen. Das wirkt deutlich schärfer, aber diese Details sind **erfunden**. Gesichter können sich dadurch leicht verändern.
- **KI-Anteil:** Wie stark das KI-Ergebnis mit dem normal geschärften Bild gemischt wird. Standard ist 70 %; wenn ein Gesicht zu glatt oder «gemalt» wirkt, weniger nehmen.
- **Gesichter neu zeichnen (experimentell):** Eine Gesichts-KI zeichnet unscharfe Gesichter komplett scharf neu, mit Augen, Wimpern, Brauen und Haut. Damit sieht ein Gesicht im unscharfen Hintergrund so scharf aus wie eines im Vordergrund. Die Details sind **erfunden**: Das Gesicht kann leicht anders aussehen als in Wirklichkeit.
- **Gesichts-Anteil:** Wie stark das neu gezeichnete Gesicht eingesetzt wird. Standard ist 100 %.

## Wie es funktioniert

1. **Erkennen:** An jeder Kante wird gemessen, wie steil der Hell-Dunkel-Übergang ist. Danach wird das Bild leicht weichgezeichnet und noch einmal gemessen. Aus dem Verhältnis der beiden Werte lässt sich die vorhandene Unschärfe berechnen. Für starke Unschärfe wird zusätzlich auf halber und viertel Auflösung gemessen. Aus diesen Messwerten entsteht eine Unschärfe-Karte. Sie wird an den Konturen im Bild ausgerichtet und in Ebenen eingeteilt.
2. **Schärfen:** Das Bild wird in Kacheln geteilt. Jede Kachel wird mit einer Wiener-Entfaltung per FFT zurückgerechnet, und zwar passend zu der Unschärfe, die dort gemessen wurde. Zwischen benachbarten Unschärfe-Stufen wird weich gemischt.
   - Eine Halo-Begrenzung verhindert helle und dunkle Säume.
   - Eine Detailmaske sorgt dafür, dass glatte Flächen nicht körnig werden.
   - Geschärft wird die Helligkeit, die Farben bleiben, wie sie sind.

   Gerechnet wird in mehreren Hintergrund-Threads (Web Worker). Ein 12-Megapixel-Foto braucht auf einem üblichen Rechner einige Sekunden.

## KI-Details

Ausgangslage: Normales Schärfen kann nur zurückholen, was noch im Bild steckt. Bei deutlicher Unschärfe sind die feinsten Einzelheiten (Wimpern, einzelne Haare, Hautporen) aber nicht mehr vorhanden.

So arbeitet die KI:
1. Sie verkleinert die unscharfen Stellen, und zwar so stark, dass die kleine Kopie nur noch leicht unscharf ist (je nach gemessener Unschärfe um das 2- bis 8-Fache; bei grossen Kamerafotos stärker als bei kleinen Bildern).
2. Sie vergrössert sie wieder auf das Vierfache. Dabei ergänzt sie Feinheiten, wie sie es an sehr vielen Fotos gelernt hat.
3. Das Ergebnis wird auf die Originalgrösse zurückgerechnet und nur in den angehakten unscharfen Ebenen eingemischt, die genug Struktur haben. Glatte Flächen wie Wände lässt sie aus.

Die KI rechnet auf der Grafikkarte (WebGL2), auf einem normalen Rechner dauert das wenige Sekunden. Ohne nutzbare Grafikkarte rechnet sie im Prozessor, das ist das gleiche Ergebnis, dauert aber deutlich länger. Auch die KI läuft vollständig auf deinem Gerät.

Das Modell ist Real-ESRGAN `realesr-general-x4v3` von Xintao Wang u. a. (https://github.com/xinntao/Real-ESRGAN, BSD-3-Clause-Lizenz, siehe `LIZENZ-Real-ESRGAN.txt`). Es steckt als 16-Bit-Zahlen in `index.html`, deshalb ist die Datei etwa 3.3 MB gross. Wie es eingebaut wurde, zeigt `werkzeuge/modell-einbauen.py`:

```bash
python3 werkzeuge/modell-einbauen.py realesr-general-x4v3.pth index.html
```

## Gesichter neu zeichnen

So arbeitet die Gesichts-KI:
1. Ein Gesichtsfinder (YuNet) sucht im Foto nach Gesichtern.
2. Nur Gesichter, die in einer angehakten unscharfen Ebene liegen, werden bearbeitet. Scharfe Gesichter bleiben, wie sie sind.
3. Jedes dieser Gesichter wird an Augen, Nase und Mund ausgerichtet. GFPGAN 1.4 zeichnet es in 512 × 512 Pixeln neu.
4. Das neue Gesicht wird mit weichem Rand zurück ins Foto gesetzt.

Beim ersten Gebrauch lädt der Browser etwa 190 MB nach (Ordner `gesichts-ki/`). Danach geht es schneller.

Die Rechenzeit hängt vom Gerät ab:
- **Mit Grafikkarte (WebGPU):** Gemessen habe ich das noch nicht, es sollte aber deutlich schneller gehen als ohne.
- **Ohne Grafikkarte:** In meinem Test dauerte das Neuzeichnen rund 15 Sekunden pro Gesicht, das erste Mal kommt das Nachladen dazu.

Auch die Gesichts-KI rechnet nur auf deinem Gerät.

Wichtig: Das Nachladen funktioniert nur, wenn die Seite über eine Webadresse geöffnet wird, also über GitHub Pages oder als Artefakt. Öffnest du `index.html` per Doppelklick, blockiert der Browser das Nachladen. Das normale Schärfen und die KI-Details gehen dann trotzdem.

Verwendete Teile:
- **GFPGAN 1.4** von Tencent ARC (https://github.com/TencentARC/GFPGAN), als ONNX-Fassung aus https://github.com/facefusion/facefusion-assets. Die Lizenz ist Apache-2.0, enthält aber Bestandteile, die nur für nicht-kommerzielle Nutzung frei sind (StyleGAN2/NVIDIA, DFDNet), siehe `LIZENZ-GFPGAN.txt`. Für private Fotos ist das kein Problem; das Programm mit der Gesichts-KI darf aber nicht verkauft werden.
- **YuNet** von Shiqi Yu (https://github.com/opencv/opencv_zoo), MIT-Lizenz, siehe `LIZENZ-YuNet.txt`.
- **ONNX Runtime Web 1.20.1** von Microsoft, MIT-Lizenz, siehe `LIZENZ-onnxruntime.txt`.

Wie der Ordner `gesichts-ki/` entsteht, zeigt `werkzeuge/gesichts-ki-vorbereiten.py`:

```bash
python3 werkzeuge/gesichts-ki-vorbereiten.py gfpgan_1.4.onnx face_detection_yunet_2023mar.onnx onnxruntime-web/dist gesichts-ki/
```

## Grenzen

- Leichte bis mittlere Unschärfe lässt sich gut verbessern, etwa wenn der Fokus knapp daneben lag oder die Linse weich zeichnet. Sehr starke Unschärfe oder Verwacklung kann kein Programm vollständig zurückholen. Die KI-Details können das überspielen, erfinden die fehlenden Details aber.
- Fotos über 16 Megapixel werden für die Bearbeitung verkleinert, weil Browser bei Bildgrössen und Speicher Grenzen haben.
- Metadaten (EXIF, z. B. Aufnahmedatum oder GPS) werden beim Speichern nicht übernommen.
- HEIC-Fotos vom iPhone öffnet nur Safari. In anderen Browsern wandelst du sie vorher in JPG um.
