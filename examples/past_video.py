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

import chrysalis
import time
import cv2
import os

ch = chrysalis.Connect(host="127.0.0.1", port="1111", password="aaaaaaaaaaaaaaa", ssl_ca_cert="example.cer")

os.environ['DISPLAY'] = ":0"

if __name__ == "__main__":
    # probe the stream first, to check what's in the media cache
    probe = ch.Probe()
    print("start {}, end {}, duration {} s, assessed fps {}".format(probe.start_timestamp, probe.end_timestamp, probe.duration, probe.fps))
    start = probe.end_timestamp - (1000 * 30) # X seconds in the past
    end = probe.end_timestamp - (1000 * 15) # until Y seconds in the past (Y > X)

    print("streaming from: {} to {} ms".format(start, end))

    while True:
        img = ch.VideoPastImage(start, end)

        if img is not None:
            frame = img.data

            cv2.imshow("720p/20 FPS (300 sec -> 200 sec ago)", frame)
            if cv2.waitKey(80) & 0xFF == ord('q'):
                ch.VideoPastImageStopNow()
                break
        else:
            # done
            break