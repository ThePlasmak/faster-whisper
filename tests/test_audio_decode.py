"""Exercise the installed audio decoder without a model download or GPU.

Run after installing requirements.txt: python -m unittest discover -s tests
"""
import io
import unittest
import wave

import numpy as np
from faster_whisper.audio import decode_audio


def wav_file(samples, channels=1):
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as audio:
        audio.setnchannels(channels)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(samples.astype('<i2').tobytes())
    buffer.seek(0)
    return buffer


class AudioDecodeTest(unittest.TestCase):
    def test_mono_pcm_decode(self):
        samples = (np.sin(np.arange(6400) * .1) * 10000).astype('<i2')
        decoded = decode_audio(wav_file(samples))
        self.assertEqual(decoded.shape, (6400,))
        np.testing.assert_allclose(decoded, samples.astype(np.float32) / 32768)

    def test_split_stereo_decode(self):
        samples = np.column_stack((np.full(6400, 1234), np.full(6400, -2345)))
        left, right = decode_audio(wav_file(samples, channels=2), split_stereo=True)
        self.assertEqual(left.shape, (6400,))
        self.assertEqual(right.shape, (6400,))
        np.testing.assert_allclose(left, 1234 / 32768)
        np.testing.assert_allclose(right, -2345 / 32768)


if __name__ == '__main__':
    unittest.main()
