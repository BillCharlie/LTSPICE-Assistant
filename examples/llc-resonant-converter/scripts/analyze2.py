# -*- coding: utf-8 -*-
import numpy as np
from parse_raw import read_raw
names, arr = read_raw(r'LLC_converter.raw')
t = np.abs(arr['time'])
def g(n): return arr[n]
Vsw  = g('V(sw)')
Ilp  = g('I(Lp)')        # primary / resonant tank current ( = I(Lr) )
Ils  = g('I(Ls)')        # secondary winding current
Id1  = g('I(D1)'); Id2=g('I(D2)'); Id3=g('I(D3)'); Id4=g('I(D4)')
Irl  = g('I(Rload)')
Vca  = g('V(seca)'); Vcb=g('V(secb)')
Vout = g('V(vout)')
Vna  = g('V(na)')
Vcr  = Vsw - Vna          # voltage across Cr
n = 4.0
Imag = Ilp - Ils/n        # magnetizing current referred to primary

# steady-state window (whole saved set is steady state)
m = t > t.min()
def stats(x):
    return x.min(), x.max(), np.sqrt(np.mean(x**2)), x.mean()

print('=== switching frequency / duty ===')
th = 200.0
above = Vsw > th
rise = np.where((~above[:-1]) & (above[1:]))[0]
fall = np.where((above[:-1]) & (~above[1:]))[0]
if len(rise) > 1:
    per = np.diff(t[rise]); Tsw = per.mean()
    print('fsw = %.2f kHz, Tsw = %.3f us' % (1/Tsw/1e3, Tsw*1e6))
    # high-side on time: from a rise to next fall
    ontimes = []
    for r in rise:
        nf = fall[fall > r]
        if len(nf): ontimes.append(t[nf[0]] - t[r])
    ont = np.mean(ontimes)
    print('S1 on-time (Vsw>200) = %.3f us  -> duty = %.2f %%' % (ont*1e6, ont/Tsw*100))

print('\n=== resonant / primary current I(Lr)=I(Lp) ===')
print('min=%.3f max=%.3f rms=%.3f mean=%.4f' % stats(Ilp))
print('\n=== magnetizing current Imag = I(Lp)-I(Ls)/n ===')
print('min=%.3f max=%.3f rms=%.3f mean=%.4f' % stats(Imag))
print('peak-peak=%.3f A' % (Imag.max()-Imag.min()))
print('\n=== secondary current I(Ls) ===')
print('min=%.3f max=%.3f rms=%.3f' % stats(Ils)[:3])
print('\n=== Cr voltage ===')
print('min=%.1f max=%.1f mean=%.1f pkpk=%.1f' % (Vcr.min(),Vcr.max(),Vcr.mean(),Vcr.max()-Vcr.min()))
print('\n=== Vout ===')
print('min=%.4f max=%.4f mean=%.4f ripple_mVpp=%.1f' % (Vout.min(),Vout.max(),Vout.mean(),(Vout.max()-Vout.min())*1e3))
print('Iload mean=%.4f A  Pout=%.2f W' % (Irl.mean(), Vout.mean()*Irl.mean()))

# diode conduction: which pair conducts when SECA>0
print('\n=== rectifier diode peak currents ===')
for nm,d in [('D1',Id1),('D2',Id2),('D3',Id3),('D4',Id4)]:
    print('%s peak=%.3f rms=%.3f' % (nm, np.max(np.abs(d)), np.sqrt(np.mean(d**2))))

# phase: does Ils reach ~0 at switching instants (ZCS)?
print('\n=== ZCS check: |I(Ls)| at high-side turn-off instants ===')
vals=[]
for f in fall[:6]:
    vals.append(abs(Ils[f]))
print('mean |Ils| at S1 turn-off = %.3f A  (small => ZCS)' % np.mean(vals))

# ZVS check: Vsw at the moment S1 gate turns on - was it already near 0->Vin via body diode?
# Look at slope/level just before rise
print('\n=== ZVS check: Vsw minimum just before each rising edge ===')
print('global Vsw min=%.2f max=%.2f (clamped 0..Vin => body-diode ZVS)' % (Vsw.min(), Vsw.max()))
