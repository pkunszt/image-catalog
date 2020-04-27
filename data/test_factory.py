from unittest import TestCase
from data.factory import Factory


class TestFactory(TestCase):
    def test_checksum(self):
        a = Factory.checksum("../testfiles/milky-way-nasa.jpg")
        self.assertEqual(a, "485291fa0ee50c016982abbfa943957bcd231aae0492ccbaa22c58e3997b35e0")

    def test_mydecode(self):
        testbinary = b"ffprobe version 3.0-static http://johnvansickle.com/ffmpeg/  Copyright (c) 2007-2016 the FFmpeg developers\n  built with gcc 5.3.1 (Debian 5.3.1-8) 20160205\n  configuration: --enable-gpl --enable-version3 --disable-shared --disable-debug --enable-runtime-cpudetect --enable-libmp3lame --enable-libx264 --enable-libx265 --enable-libwebp --enable-libspeex --enable-libvorbis --enable-libvpx --enable-libfreetype --enable-fontconfig --enable-libxvid --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvo-amrwbenc --enable-gray --enable-libopenjpeg --enable-libopus --enable-libass --enable-gnutls --enable-libvidstab --enable-libsoxr --enable-frei0r --enable-libfribidi --disable-indev=sndio --disable-outdev=sndio --enable-librtmp --enable-libmfx --cc=gcc\n  libavutil      55. 17.103 / 55. 17.103\n  libavcodec     57. 24.102 / 57. 24.102\n  libavformat    57. 25.100 / 57. 25.100\n  libavdevice    57.  0.101 / 57.  0.101\n  libavfilter     6. 31.100 /  6. 31.100\n  libswscale      4.  0.100 /  4.  0.100\n  libswresample   2.  0.101 /  2.  0.101\n  libpostproc    54.  0.100 / 54.  0.100\nInput #0, mov,mp4,m4a,3gp,3g2,mj2, from '/files/HLXG4486.mov':\n  Metadata:\n    major_brand     : qt  \n    minor_version   : 0\n    compatible_brands: qt  \n    creation_time   : 2016-01-02 10:03:39\n    com.apple.quicktime.artwork: \xff\xd8\xff\xe0\n  Duration: 00:01:25.37, start: 0.000000, bitrate: 4754 kb/s\n    Stream #0:0(und): Video: h264 (Baseline) (avc1 / 0x31637661), yuv420p(tv, bt709), 960x540, 4617 kb/s, 30 fps, 30 tbr, 600 tbn, 1200 tbc (default)\n    Metadata:\n      creation_time   : 2016-01-02 10:03:39\n      handler_name    : Core Media Data Handler\n      encoder         : H.264\n    Stream #0:1(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 128 kb/s (default)\n    Metadata:\n      creation_time   : 2016-01-02 10:03:39\n      handler_name    : Core Media Data Handler\n"
        teststr = Factory.mydecode(testbinary)
        for lines in teststr.splitlines():
            print(lines)
