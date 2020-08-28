
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

import multiprocessing
import time
from .chunker import Chunker, ChImage
from .log import logger
from .ch_errors import VideoFailedToStart, VideoHistoryNotFound, InfrequentException
import av
import numpy
import datetime
import operator
from threading import Lock

class LiveVideoImage:

    def __init__(self, redis_conn, stream_name, codec=av.Codec('h264', 'r').create()):
        self.__redis_conn = redis_conn
        self.__stream_name = stream_name
        self.__chunker = Chunker(codec=codec)
        self.__codec = codec
        # all timestamps in ms
        self.__last_query = None
        self.__last_query_timestamp = 0
    
    def get_latest_image(self):
        # calculating default from time
        query_default_past_time = 30*1000
        redis_time = self.__redis_conn.time()
        redis_time = int(redis_time[0] + (redis_time[1] / 1000000)) * 1000
        
        # convert last query timestamp to timestamp
        if abs(self.__last_query_timestamp - redis_time) > query_default_past_time:
            self.__last_query_timestamp = redis_time - query_default_past_time
            self.__last_query = str(self.__last_query_timestamp)

        # logger.debug("query time from {} to {}".format(self.__last_query, datetime.datetime.fromtimestamp(redis_time/1000.0)))
        start_time = time.time()

        buffer = self.__redis_conn.xread({self.__stream_name:self.__last_query}, block=1000)
        if len(buffer) > 0:
            arr = buffer[0]
            inner_buffer = arr[1]
            # logger.debug("returned packets: {} in {} s".format(len(inner_buffer), (time.time() - start_time)))
            last = inner_buffer[-1]
            self.__last_query = last[0]
            self.__last_query_timestamp = int(self.__last_query.decode('utf-8').split("-")[0])
            # logger.debug("stored last_query_timestamp {}".format(self.__last_query))
            frames = self.__chunker.frames(inner_buffer)
            if len(frames) > 0:
                frame = None
                pair = max(frames.items(), key=operator.itemgetter(0))
                ts = pair[0]
                frame = pair[1]
                d = frame.to_ndarray(format="bgr24")
                chImage = ChImage(data=d, width=frame.width, height=frame.height, timestamp=ts, frame_type=frame.pict_type.name)
                # logger.debug("img width: {}, height: {}, type: {}".format(chImage.width, chImage.height, chImage.frame_type))
                return chImage
        return None
