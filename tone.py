# Copyright (c) 2023 Rohan Singh
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

import libtone as lib
import numpy as np
import scipy.signal as signal
from gain import gain

VOLUME_OFFSET = 9
BASS_OFFSET = MID_OFFSET = TREBLE_OFFSET = 5

args = lib.tone_args()
volume = gain(args.volume, VOLUME_OFFSET)
bass = gain(args.bass, BASS_OFFSET)
mid = gain(args.midrange, MID_OFFSET)
treble = gain(args.treble, TREBLE_OFFSET)

wav = args.wav
out = args.out

rate, data = lib.read_wav(wav)

# https://numpy.org/doc/stable/reference/generated/numpy.transpose.html
transposed_data = np.transpose(data)


# Get number of channels
channels = 0
if isinstance(data[0], np.ndarray):
    channels = len(data[0])
elif isinstance(data[0], np.float64):
    channels = 1

if channels == 1:
    channel_1 = transposed_data

elif channels == 2:
    # Extract channels from stereo track
    channel_1 = transposed_data[0]
    channel_2 = transposed_data[1]


# https://medium.com/analytics-vidhya/how-to-filter-noise-with-a-low-pass-filter-python-885223e5e9b7
# https://stackoverflow.com/questions/48101564/create-a-band-pass-filter-via-scipy-in-python

order = 255
cutoff_low = 300
cutoff_high = 4000
nyquist = 0.5 * rate

# Apply filters
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html
firwin_low = signal.firwin(order, cutoff_low / nyquist)
firwin_mid = signal.firwin(order, [cutoff_low / nyquist, cutoff_high / nyquist])
firwin_high = signal.firwin(order, cutoff_high / nyquist)

filtered_low_1 = signal.lfilter(firwin_low, 1.0, channel_1)
filtered_band_1 = signal.lfilter(firwin_mid, 1.0, channel_1)
filtered_high_1 = signal.lfilter(firwin_high, 1.0, channel_1)

if channels == 2:
    filtered_low_2 = signal.lfilter(firwin_low, 1.0, channel_2)
    filtered_band_2 = signal.lfilter(firwin_mid, 1.0, channel_2)
    filtered_high_2 = signal.lfilter(firwin_high, 1.0, channel_2)


# Apply the tone and volume controls
output_1 = output_2 = np.empty(len(channel_1))
output_1  = volume * (bass * filtered_low_1 + mid * filtered_band_1 + treble * filtered_high_1)
if (channels == 2):
    output_2 = volume * (bass * filtered_low_2 + mid * filtered_band_2 + treble * filtered_high_2)


# Decide whether to play the modified sound or write it to a WAV file
if (channels == 2):
    stereo_output_data = np.transpose([output_1, output_2])
    if (out is None):
        lib.play(rate, stereo_output_data)
    else:
        lib.write_wav(out, rate, stereo_output_data)
elif (channels == 1):
    if (out is None):
        lib.play(rate, output_1)
    else:
        lib.write_wav(out, rate, output_1)
