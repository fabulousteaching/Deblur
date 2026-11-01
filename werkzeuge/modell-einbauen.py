"""Baut das KI-Modell (Real-ESRGAN realesr-general-x4v3) in index.html ein.

Aufruf:  python3 werkzeuge/modell-einbauen.py realesr-general-x4v3.pth index.html

Die Gewichte werden als 16-Bit-Gleitkommazahlen (Base64) zwischen den Markierungen
KI-MODELL-START / KI-MODELL-ENDE in die Seite geschrieben. Reihenfolge je Faltungsschicht
(0 bis 33): Gewichte (Ausgang × Eingang × 3 × 3), Bias, danach – ausser bei der letzten
Schicht – die PReLU-Steigungen. Eingänge: Schicht 0 hat 3, alle anderen 64;
Ausgänge: Schicht 33 hat 48 (= 3 Farben × 4 × 4), alle anderen 64.

Quelle des Modells: https://github.com/xinntao/Real-ESRGAN (BSD-3-Clause, siehe LIZENZ-Real-ESRGAN.txt)
"""
import base64, re, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pth_lesen import load

def pack(path):
    p = load(path)['params']
    convs = [k[:-len('.weight')] for k in p if k.endswith('.weight') and p[k].ndim == 4]
    convs.sort(key=lambda k: int(k.split('.')[1]))
    assert len(convs) == 34, len(convs)
    parts = []
    for i, k in enumerate(convs):
        w, b = p[k + '.weight'], p[k + '.bias']
        assert w.shape == ((48 if i == 33 else 64), (3 if i == 0 else 64), 3, 3), (k, w.shape)
        parts += [w.ravel(), b.ravel()]
        if i < 33:
            idx = int(k.split('.')[1]) + 1
            parts.append(p['body.%d.weight' % idx].ravel())
    flat = np.concatenate(parts).astype(np.float32)
    return flat, flat.astype(np.float16)

if __name__ == '__main__':
    pth, html = sys.argv[1], sys.argv[2]
    f32, f16 = pack(pth)
    print('Parameter:', f32.size, ' grösste Rundungsabweichung (16 Bit):', float(np.max(np.abs(f32 - f16.astype(np.float32)))))
    b64 = base64.b64encode(f16.tobytes()).decode('ascii')
    s = open(html, encoding='utf-8').read()
    new, n = re.subn(r'(<!--KI-MODELL-START-->).*?(<!--KI-MODELL-ENDE-->)',
                     lambda m: m.group(1) + '<script type="application/octet-stream" id="kiModell">' + b64 + '</script>' + m.group(2),
                     s, flags=re.S)
    assert n == 1, 'Markierungen KI-MODELL-START/ENDE nicht gefunden'
    open(html, 'w', encoding='utf-8').write(new)
    print('eingebaut:', len(b64) // 1024, 'KB Base64')
