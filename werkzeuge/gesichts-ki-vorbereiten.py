"""Bereitet die Gesichts-KI für den Browser vor (Ordner gesichts-ki/).

Aufruf:
  python3 werkzeuge/gesichts-ki-vorbereiten.py gfpgan_1.4.onnx face_detection_yunet_2023mar.onnx \\
          onnxruntime-web/dist gesichts-ki/

Ergebnis im Zielordner:
  gfpgan.onnx                Aufbau von GFPGAN (klein); die Gewichte liegen ausserhalb («gfpgan.data»)
  gfpgan-NN.bin              die Gewichte als 16-Bit-Zahlen, in Teilen von höchstens 14 MB
  gfpgan.json                Anzahl Teile und Zahlen (liest das Programm)
  yunet.onnx                 Gesichtsfinder
  ort.webgpu.min.js, ort-wasm-simd-threaded.jsep.mjs
                             ONNX Runtime Web (Rechen-Laufzeit für die Modelle)
  ort-wasm-1.bin, ort-wasm-2.bin
                             der WebAssembly-Teil von ONNX Runtime, in zwei Hälften
                             (Artefakte erlauben höchstens 15 MB pro Datei)
Der Browser lädt die Teile, setzt sie zusammen und wandelt die Gewichte in 32-Bit-Zahlen um.

Quellen:
  GFPGAN v1.4, Tencent ARC – https://github.com/TencentARC/GFPGAN (ONNX-Fassung aus
    https://github.com/facefusion/facefusion-assets, Release models-3.0.0)
  YuNet, Shiqi Yu – https://github.com/opencv/opencv_zoo (MIT)
  ONNX Runtime Web 1.20.1, Microsoft – https://www.npmjs.com/package/onnxruntime-web (MIT)
"""
import json, os, shutil, sys
import numpy as np, onnx
from onnx.external_data_helper import convert_model_to_external_data

gfp_src, yunet_src, ort_dist, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)

# GFPGAN: Aufbau und Gewichte trennen, Gewichte als 16 Bit in Teilen
m = onnx.load(gfp_src)
assert all(t.data_type == onnx.TensorProto.FLOAT for t in m.graph.initializer), 'nur 32-Bit-Gewichte erwartet'
convert_model_to_external_data(m, all_tensors_to_one_file=True, location='gfpgan.data', size_threshold=0)
onnx.save_model(m, os.path.join(out, 'gfpgan.onnx'))
data = np.fromfile(os.path.join(out, 'gfpgan.data'), dtype=np.float32)
os.remove(os.path.join(out, 'gfpgan.data'))
h = data.astype(np.float16)
assert np.all(np.isfinite(h)), 'Wert ausserhalb des 16-Bit-Bereichs'
print('GFPGAN: grösste relative Abweichung durch 16 Bit:', float(np.max(np.abs(h.astype(np.float32) - data) / (np.abs(data) + 1e-3))))
raw, part, n = h.tobytes(), 14 * 1024 * 1024, 0
for i in range(0, len(raw), part):
    n += 1
    with open(os.path.join(out, 'gfpgan-%02d.bin' % n), 'wb') as f: f.write(raw[i:i + part])
json.dump({'teile': n, 'zahlen': int(data.size)}, open(os.path.join(out, 'gfpgan.json'), 'w'))
print('GFPGAN:', data.size, 'Zahlen in', n, 'Teilen')

# Gesichtsfinder
shutil.copy(yunet_src, os.path.join(out, 'yunet.onnx'))

# ONNX Runtime Web
for f in ('ort.webgpu.min.js', 'ort-wasm-simd-threaded.jsep.mjs'):
    shutil.copy(os.path.join(ort_dist, f), os.path.join(out, f))
w = open(os.path.join(ort_dist, 'ort-wasm-simd-threaded.jsep.wasm'), 'rb').read()
half = (len(w) + 1) // 2
open(os.path.join(out, 'ort-wasm-1.bin'), 'wb').write(w[:half])
open(os.path.join(out, 'ort-wasm-2.bin'), 'wb').write(w[half:])
print('ONNX Runtime Web: WebAssembly', len(w), 'Bytes in 2 Teilen')
