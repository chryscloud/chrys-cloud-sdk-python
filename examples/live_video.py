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
from time import strftime

ch = chrysalis.RtmpMedia(host="127.0.0.1", port="1111", password="aaaaaaaaaaaaaaa", ssl_ca_cert="example.cer")

os.environ['DISPLAY'] = ":0"

if __name__ == "__main__":
    print("hello")
    while True:
        img = ch.VideoLatestImage()

        if img is not None:
            frame = img.data
            # draw current time on the screen
            cv2.putText(frame, strftime("%H:%M:%S"), (10,100), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,255,0),2,cv2.LINE_AA)
            cv2.imshow("720p/20 FPS live video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
