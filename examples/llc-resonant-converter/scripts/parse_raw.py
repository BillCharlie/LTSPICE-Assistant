import struct, sys

def read_raw(path):
    with open(path, 'rb') as f:
        data = f.read()
    # Header is ASCII (UTF-16LE in LTspice). Find 'Binary:' marker.
    # LTspice writes header in UTF-16LE
    txt = data.decode('utf-16-le', errors='ignore')
    bidx = txt.find('Binary:')
    header = txt[:bidx]
    # byte offset of binary data
    bmarker = 'Binary:\n'
    # locate in raw bytes (utf-16-le)
    marker_bytes = 'Binary:\n'.encode('utf-16-le')
    pos = data.find(marker_bytes)
    bin_start = pos + len(marker_bytes)

    info = {}
    varnames = []
    lines = header.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('No. Variables:'):
            info['nvars'] = int(line.split(':')[1])
        elif line.startswith('No. Points:'):
            info['npoints'] = int(line.split(':')[1])
        elif line.startswith('Flags:'):
            info['flags'] = line.split(':')[1].strip()
        elif line.startswith('Variables:'):
            for j in range(info['nvars']):
                i += 1
                parts = lines[i].split('\t')
                parts = [p for p in parts if p != '']
                varnames.append(parts[1])
        i += 1

    nvars = info['nvars']
    npts = info['npoints']
    real = 'real' in info.get('flags', '')
    # In binary: time is double(8 bytes), other vars are float? Actually LTspice
    # transient: first var (time) is double, rest are float (4 bytes) when not 'double' flag.
    # If flags has 'double', all doubles. Default tran: time=double(8), vars=float(4)?
    # LTspice actually stores all as double for the first var and single for rest unless numdgt high.
    # Robust approach: try the standard LTspice layout: time=8 bytes double, vars=4 bytes float
    import numpy as np
    body = data[bin_start:]

    if real:
        # try time double + others float
        rowsize = 8 + 4*(nvars-1)
        if rowsize*npts == len(body):
            arr = {}
            cols = [np.zeros(npts) for _ in range(nvars)]
            off = 0
            for p in range(npts):
                cols[0][p] = struct.unpack_from('<d', body, off)[0]; off += 8
                for v in range(1, nvars):
                    cols[v][p] = struct.unpack_from('<f', body, off)[0]; off += 4
            for k,name in enumerate(varnames):
                arr[name] = cols[k]
            return varnames, arr
        else:
            # all doubles
            rowsize = 8*nvars
            cols = [np.zeros(npts) for _ in range(nvars)]
            off = 0
            for p in range(npts):
                for v in range(nvars):
                    cols[v][p] = struct.unpack_from('<d', body, off)[0]; off += 8
            arr = {name: cols[k] for k,name in enumerate(varnames)}
            return varnames, arr
    raise RuntimeError('complex not handled')

if __name__ == '__main__':
    import numpy as np
    names, arr = read_raw(r'LLC_converter.raw')
    print('VARS:', names)
    t = np.abs(arr[names[0]])  # time (LTspice may store sign on first/last)
    # find a name helper
    def find(sub):
        for n in names:
            if sub.lower() in n.lower():
                return n
        return None
    nv = find('v(vout)')
    nsw = find('v(sw)')
    # current through Lr: I(Lr)
    ilr = find('i(lr)')
    icr = find('i(cr)')
    vcr_na = find('v(na)')
    print('npoints', len(t), 'tspan', t.min(), t.max())
    if nv:
        vo = arr[nv]
        print('Vout: mean=%.3f min=%.3f max=%.3f ripple_pp=%.4f' % (vo.mean(), vo.min(), vo.max(), vo.max()-vo.min()))
    if ilr:
        i = arr[ilr]
        print('I(Lr): peak=%.3f rms=%.3f' % (np.max(np.abs(i)), np.sqrt(np.mean(i**2))))
    # export a downsampled CSV for plotting
    import csv
    cols_want = [names[0]] + [x for x in [nsw, ilr, icr, find('v(seca)'), nv] if x]
    # downsample to ~600 points within last 100us window
    mask = t >= 200e-6
    idx = np.where(mask)[0]
    if len(idx) > 1200:
        sel = idx[::len(idx)//1200]
    else:
        sel = idx
    with open(r'wave.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(cols_want)
        for p in sel:
            w.writerow(['%.9g'%arr[c][p] for c in cols_want])
    print('CSV cols:', cols_want, 'rows:', len(sel))
