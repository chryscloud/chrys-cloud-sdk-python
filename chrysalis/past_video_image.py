import multiprocessing

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

import time
from .chunker import Chunker, ChImage
from .log import logger
from .ch_errors import VideoFailedToStart, VideoHistoryNotFound, InfrequentException
import av
import numpy
import datetime
import operator
import multiprocessing as mp
import sys

class PastVideoImage:

    def __init__(self, redis_conn, stream_name, audio_stream_name, codec=av.Codec('h264', 'r').create()):
        self.__redis_conn = redis_conn
        self.__stream_name = stream_name
        self.__audio_stream_name = audio_stream_name

        self.__last_history_query = None
        self.__last_history_query_timestamp = 0
        self.__history_chunker = None
        self.__last_history_request_time = 0
        self.__history_queue = mp.Queue()
        self.__is_first_run = True
        self.__lock = mp.Lock()

    def get_latest_image_from(self, fromtimestamp, totimestamp) -> ChImage:

        redis_time = self.__redis_conn.time()
        redis_time = int(redis_time[0] + (redis_time[1] / 1000000)) * 1000

        self.__process = mp.Process(target=self.fetch_next_frames, args=(totimestamp,True,))

        with self.__lock:
            if self.__last_history_request_time == 0:    
                self.__last_history_request_time = redis_time

            if self.__last_history_query_timestamp == 0:
                self.__last_history_query_timestamp = fromtimestamp
                self.__last_history_query = str(self.__last_history_query_timestamp)
                self.__history_chunker = Chunker(codec=av.Codec('h264', 'r').create())
                self.__history_queue = mp.Queue()
            else:
                # check if more than 10 seconds between 2 queries, throw exception
                last_query_diff = abs(self.__last_history_request_time - redis_time)
                if last_query_diff > 10*1000:
                    self.__history_cleanup()
                    raise InfrequentException
        
       
            self.__last_history_request_time = redis_time

        if self.__is_first_run:
            self.__process.start()
            self.__is_first_run = False

        while True:
            if self.__history_queue.qsize() > 0:
                img = self.__history_queue.get()
                if img.timestamp == 0 and img.data is None:
                    # sentinel img received (no more data)
                    break
                else:
                    return img
            else:
                time.sleep(0.1)

        self.__history_cleanup()
        return None

    def stop_now(self):
        with self.__lock:
            self.__last_history_query_timestamp = sys.maxsize

    def fetch_next_frames(self, totimestamp, is_forward_process=False):

        while True:
            if self.__last_history_query_timestamp < totimestamp:
                if self.__history_queue.qsize() < 10:
                    # dt_object = datetime.datetime.fromtimestamp(int(self.__last_history_query_timestamp / 1000))
                    # logger.debug("running process {}".format(self.__last_history_query_timestamp))

                    buffer = self.__redis_conn.xread({self.__stream_name:self.__last_history_query}, block=1000, count=10)

                    # start_time = time.time()
                    if len(buffer) > 0:
                        arr = buffer[0]
                        inner_buffer = arr[1]
                        # logger.debug("returned packets: {} in {} s".format(len(inner_buffer), (time.time() - start_time)))
                        last = inner_buffer[-1]
                        with self.__lock:
                            self.__last_history_query = last[0]
                            self.__last_history_query_timestamp = int(self.__last_history_query.decode('utf-8').split("-")[0])
                        # logger.debug("NEXT ONE should query FROM: {}".format(self.__last_history_query))
                        frames = self.__history_chunker.frames(inner_buffer)
                        if len(frames) > 0:
                            for frame_ts, frame in frames.items():
                                d = frame.to_ndarray(format="bgr24")
                                chImage = ChImage(data=d, width=frame.width, height=frame.height, timestamp=frame_ts, frame_type=frame.pict_type.name)
                                self.__history_queue.put(chImage)
                else: 
                    if is_forward_process:
                        time.sleep(0.15)
                    else:
                        break
            else:
                sentinel_img = ChImage(data=None, width=0, height=0, timestamp=0)
                self.__history_queue.put(sentinel_img)
                self.__history_queue.close()
                break

    def __history_cleanup(self):
        with self.__lock:
            self.__last_history_query_timestamp = 0
            self.__last_history_query = None
            self.__last_history_request_time = 0
            self.__history_chunker = None

        if self.__history_queue is not None:
            self.__history_queue.close()