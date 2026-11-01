# Foto-Schärfer

Ein Programm, in das du Fotos einfügst. Es erkennt die unscharfen Ebenen (Bereiche) im Bild und schärft sie nach. Scharfe Bereiche bleiben unverändert.

Alles steckt in der einen Datei `index.html`. Sie läuft im Browser, auch ohne Internet. Deine Fotos werden nirgendwohin hochgeladen, alles wird auf deinem Gerät berechnet.

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

## Wie es funktioniert

1. **Erkennen:** An jeder Kante wird gemessen, wie steil der Hell-Dunkel-Übergang ist. Danach wird das Bild leicht weichgezeichnet und noch einmal gemessen. Aus dem Verhältnis der beiden Werte lässt sich die vorhandene Unschärfe berechnen. Für starke Unschärfe wird zusätzlich auf halber und viertel Auflösung gemessen. Aus diesen Messwerten entsteht eine Unschärfe-Karte. Sie wird an den Konturen im Bild ausgerichtet und in Ebenen eingeteilt.
2. **Schärfen:** Das Bild wird in Kacheln geteilt. Jede Kachel wird mit einer Wiener-Entfaltung per FFT zurückgerechnet, und zwar passend zu der Unschärfe, die dort gemessen wurde. Zwischen benachbarten Unschärfe-Stufen wird weich gemischt.
   - Eine Halo-Begrenzung verhindert helle und dunkle Säume.
   - Eine Detailmaske sorgt dafür, dass glatte Flächen nicht körnig werden.
   - Geschärft wird die Helligkeit, die Farben bleiben, wie sie sind.

   Gerechnet wird in mehreren Hintergrund-Threads (Web Worker). Ein 12-Megapixel-Foto braucht auf einem üblichen Rechner einige Sekunden.

## Grenzen

- Leichte bis mittlere Unschärfe lässt sich gut verbessern, etwa wenn der Fokus knapp daneben lag oder die Linse weich zeichnet. Sehr starke Unschärfe oder Verwacklung kann kein Programm vollständig zurückholen.
- Fotos über 16 Megapixel werden für die Bearbeitung verkleinert, weil Browser bei Bildgrössen und Speicher Grenzen haben.
- Metadaten (EXIF, z. B. Aufnahmedatum oder GPS) werden beim Speichern nicht übernommen.
- HEIC-Fotos vom iPhone öffnet nur Safari. In anderen Browsern wandelst du sie vorher in JPG um.
