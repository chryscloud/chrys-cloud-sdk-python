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

import redis
from .models import ProbeInfo
import math

class Probe:

    def __init__(self, redis, stream_name):
        self.redis = redis
        self.stream_name = stream_name

    def info(self):
        first_frame = self.redis.xrevrange(self.stream_name, min="-", max="+", count=1)
        ts_first = 0
        ts_last = 0
        fps = 0
        if len(first_frame) > 0:
            if len(first_frame[0]) > 0:
                ts_str = first_frame[0][0].decode("utf-8")
                ts_first = int(ts_str.split("-")[0])
        
        last_frame = self.redis.xrange(self.stream_name, min="-", max="+", count=60)
        if len(last_frame) > 0:
            if len(last_frame[0]) > 0:
                ts_str = last_frame[0][0].decode("utf-8")
                ts_last = int(ts_str.split("-")[0])
            
            # asses FPS
            lf = last_frame[-1:]
            ts_str = lf[0][0].decode("utf-8")
            ts = int(ts_str.split("-")[0])

            fps = math.floor(len(last_frame) / abs(ts_last - ts) * 1000)

        return ProbeInfo(ts_last, ts_first, fps=fps)
        
        