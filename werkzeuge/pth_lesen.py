# Liest eine PyTorch-.pth-Datei (Zip-Format) ohne torch; erlaubt nur Tensor-Rekonstruktion.
import zipfile, pickle, numpy as np, collections, sys
DT = {'FloatStorage': np.float32, 'HalfStorage': np.float16, 'LongStorage': np.int64, 'IntStorage': np.int32}
class Storage:
    def __init__(self, kind): self.kind = kind
def load(path):
    z = zipfile.ZipFile(path)
    pre = z.namelist()[0].split('/')[0]
    def rebuild(storage, offset, size, stride, *rest):
        kind, key = storage
        arr = np.frombuffer(z.read('%s/data/%s' % (pre, key)), dtype=DT[kind])
        n = int(np.prod(size)) if len(size) else 1
        if len(size) == 0: return arr[offset]
        st = [s * arr.itemsize for s in stride]
        return np.lib.stride_tricks.as_strided(arr[offset:], shape=size, strides=st).copy()
    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if mod == 'collections' and name == 'OrderedDict': return collections.OrderedDict
            if mod == 'torch._utils' and name == '_rebuild_tensor_v2': return rebuild
            if mod == 'torch' and name in DT: return name
            raise pickle.UnpicklingError('nicht erlaubt: %s.%s' % (mod, name))
        def persistent_load(self, pid):
            # ('storage', kind, key, location, numel)
            return (pid[1], pid[2])
    return U(z.open('%s/data.pkl' % pre)).load()
if __name__ == '__main__':
    d = load(sys.argv[1])
    print(type(d), list(d.keys())[:5])
    sd = d.get('params', d.get('params_ema', d))
    tot = 0
    for k, v in sd.items():
        tot += v.size
    print(len(sd), 'Tensoren,', tot, 'Parameter')
    for k in list(sd)[:4] + list(sd)[-4:]: print(k, sd[k].shape, sd[k].dtype)
