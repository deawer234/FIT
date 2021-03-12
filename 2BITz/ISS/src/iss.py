
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import IPython
from scipy.signal import spectrogram, lfilter, freqz, tf2zpk

s, fs = sf.read("../audio/maskoff_tone.wav")
#data = data / 2**15
s = s[:16000]
t = np.arange(s.size) / fs

seg_start = 2
seg = 0.04

seg_start_samples = int(seg_start * fs)
seg_end_samples = int((seg_start+seg) * fs)

s_seg = s[seg_start_samples:seg_end_samples]
N = s_seg.size

s_seg_spec = np.fft(s_seg)
G = 10 * np.log10(1/N * np.abs(s_seg_sec)**2)

_, ax = plt.subplots(2,1)

# np.arange(n) vytváří pole 0..n-1 podobně jako obyč Pythonovský range
ax[0].plot(np.arange(s_seg.size) / fs + odkud, s_seg)
ax[0].set_xlabel('$t[s]$')
ax[0].set_title('Segment signalu $s$')
ax[0].grid(alpha=0.5, linestyle='--')

f = np.arange(G.size) / N * fs
# zobrazujeme prvni pulku spektra
ax[1].plot(f[:f.size//2+1], G[:G.size//2+1])
ax[1].set_xlabel('$f[Hz]$')
ax[1].set_title('Spektralni hustota vykonu [dB]')
ax[1].grid(alpha=0.5, linestyle='--')

plt.tight_layout()
