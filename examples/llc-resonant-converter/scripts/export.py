import numpy as np, csv
from parse_raw import read_raw
names, arr = read_raw(r'LLC_converter.raw')
t = np.abs(arr['time'])
# derived signals
Vcr = arr['V(sw)'] - arr['V(na)']          # voltage across resonant cap Cr
Ires = arr['I(Lr)']                         # resonant (primary) current
Imag = arr['I(Lp)']                         # magnetizing current
Vsw  = arr['V(sw)']
Vout = arr['V(vout)']
Irect = arr['I(Rload)']
# use last ~3 switching periods for a clean zoomed view (~22.7us)
tmax = t.max()
win = 3*(1/132e3)
mask = t >= (tmax - win)
idx = np.where(mask)[0]
if len(idx) > 900:
    idx = idx[::len(idx)//900]
t0 = t[idx][0]
rows = list(zip((t[idx]-t0)*1e6, Vsw[idx], Ires[idx], Imag[idx], Vcr[idx], Vout[idx], Irect[idx]))
with open(r'wave.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['t_us','Vsw','Ires','Imag','Vcr','Vout','Irect'])
    for r in rows: w.writerow(['%.6g'%x for x in r])
# stats
print('rows', len(rows))
print('Vout mean=%.2f ripple_mVpp=%.1f'%(Vout[mask].mean(), (Vout[mask].max()-Vout[mask].min())*1000))
print('Ires peak=%.3f rms=%.3f'%(np.max(np.abs(Ires[mask])), np.sqrt(np.mean(Ires[mask]**2))))
print('Imag peak=%.3f'%np.max(np.abs(Imag[mask])))
print('Vcr min=%.1f max=%.1f pkpk=%.1f'%(Vcr[mask].min(),Vcr[mask].max(),Vcr[mask].max()-Vcr[mask].min()))
print('Vsw min=%.1f max=%.1f'%(Vsw[mask].min(),Vsw[mask].max()))
print('Pout=%.1fW'%(Vout[mask].mean()**2/25))
# measured switching frequency from Vsw rising edges
sw=Vsw; th=200
above=sw>th
edges=np.where((~above[:-1])&(above[1:]))[0]
if len(edges)>1:
    per=np.diff(t[edges]); print('fsw_meas=%.1f kHz'%(1/np.mean(per)/1e3))
