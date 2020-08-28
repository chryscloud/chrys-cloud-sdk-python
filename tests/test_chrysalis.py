# Copyright 2020 Wearless Tech Inc All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest import TestCase
import unittest
import time
from datetime import datetime, timedelta
import chrysalis
from chrysalis.ch_errors import VideoFailedToStart

ch = chrysalis.Connect(host="127.0.0.1", port="1111", password="aaaaaaaa", ssl_ca_cert="server.crt")

class TestInit(TestCase):

    def test_init(self):
        print(ch)

    def test_probeinfo(self):
        p = ch.Probe()
        print(p.duration)
        print(p.start_timestamp)
        print(p.end_timestamp)
        print(p.fps)

    def test_past_buffered_video(self):
        p = ch.Probe()
        end = p.start_timestamp + (1000 * 30)
        count = 0
        while True:
            if count > 50:
                break
            img = ch.VideoPastImage(p.start_timestamp, end)
            print(img)
            count += 1

    def test_screenshot(self):
        d = datetime.today() - timedelta(hours=0, minutes=0, seconds=20)
        img = ch.Screenshot(dt=d)
        print(img.width, img.height)

    def test_screenshot_latest(self):
        img = ch.Screenshot()
        print(img)

    def test_live_video(self):
        for _ in range(50):
            _ = ch.VideoLatestImage()
            time.sleep(0.05)

if __name__ == '__main__':
    unittest.main()