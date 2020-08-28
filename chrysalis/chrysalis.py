
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
import redis
import av
import collections
import logging as logger
from datetime import datetime
from .live_video_image import LiveVideoImage
from .past_video_image import PastVideoImage
from .chunker import Chunker, ChImage
from .probe import Probe, ProbeInfo
from .hls import HLS
import sys

class RtmpMedia:
    """
    This class represents main Rtmp Media stream from Chrysalis Cloud server

    Attributes:
    host (string): Server host (e.g. 127.0.0.1, http://mystream.chrysvideo.com)
    port (int): Port of the streaming media server cache
    buffer_size (int): The default buffer size for decoded frame per frame data (audio or video) when streaming live video (default 10)
    """

    def __init__(self, host, port, password=None, ssl_ca_cert=None, buffer_size=10):
        self.password = password
        self.buffer_size = buffer_size
        self.rtmp_video_stream = "input_rtmp_stream"
        self.rtmp_audio_stream = "input_rtmp_audio_stream"
        try:
            ssl_cert_reqs = None
            if ssl_ca_cert is not None:
                ssl_cert_reqs = "required"
                pool = redis.ConnectionPool(host=host, port=port, password=password, connection_class=redis.SSLConnection, ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_cert)
            else:
                pool = redis.ConnectionPool(host=host, port=port, password=password)
            self.redis_conn = redis.StrictRedis(connection_pool=pool)
            test_time = self.redis_conn.time() # test connection right away
            logger.info("redis current time: " + str(test_time[0]))
        except redis.ConnectionError as ex:
            logger.error("failed to connect to remote streaming instance: " + str(ex), stack_info=True)
            raise ConnectionError()
        except:
            print("Error: ", sys.exc_info()[0])
            # logger.error("failed to connect to remote streaming instance", stack_info=True)
            raise ConnectionError()

        self.audio_codec = av.Codec('aac', 'r').create()
        self.video_codec = av.Codec('h264', 'r').create()
        self.__playvideo = LiveVideoImage(redis_conn=self.redis_conn, stream_name=self.rtmp_video_stream)
        self.__playpastvideo = PastVideoImage(redis_conn=self.redis_conn, stream_name=self.rtmp_video_stream, audio_stream_name=self.rtmp_audio_stream)
        logger.debug("Chrysalis SDK init success with host " + host + ":" + str(port) + ", buffer size: " + str(buffer_size))

    def VideoLatestImage(self):
        """
        Latest frame from the video stream.

        Decoding the latest image from video stream

        Returns:
        ChImage object
        """
        img = self.__playvideo.get_latest_image()
        return img

    def VideoPastImage(self, fromTsMs, toTsMs):
        """
        Frame from the video buffer between two timestamps (in milliseconds).

        Decoding all images in a buffer between two timestamps

        Returns:
        ChImage object
        """
        img = self.__playpastvideo.get_latest_image_from(fromtimestamp=fromTsMs, totimestamp=toTsMs)
        return img

    def VideoPastImageStopNow(self):
        """
        Stopping VideoPastImage before it reached it's natural end

        natural end = end_timestmap reached

        Returns:
        ChImage object
        """
        self.__playpastvideo.stop_now()

    def Probe(self) -> ProbeInfo:
        """
        Probe the video stream.

        Determening approximate cached video duration, start timestamp of the cache and end timestamp of the cache.

        Returns:
        ProbeInfo object
        """
        p = Probe(self.redis_conn, self.rtmp_video_stream)
        return p.info()

    def Screenshot(self, dt:datetime=datetime.now(), within_seconds:int=10) -> ChImage:
        """
        BGR24 image as numpy array. Screenshot does not guarantee to find an image withing the given timespan.
        This is due to H264 algorithm stream chunking the frames into I,B,P frames. Screenshot function actually returns an I frame if found
        withing given timestamp +/- (within_seconds/2)

        Attributes
        ----------
        timestamp : int
            around which  timestamp  to look for I frame
        within_seconds : int
            allowed search area around timestamp

        Returns
        -------
        ChImage or None if not found
        """
        timestamp = int(dt.timestamp() * 1000)
        
        # if less than 10 ms from time it's the latest time
        buffer_to_ts = timestamp
        if abs(int(time.time() * 1000) - timestamp) > 10:
            # otherwise we're searching withing_seconds/2 ahead
            logger.debug("searching 1/2 of withing seconds in the future")
            buffer_to_ts = timestamp  + int(within_seconds / 2 * 1000)

        min_found = None
        # seeks in the past 5 seconds (second per second)
        
        for stride in range(within_seconds):
            buffer_to_ts = buffer_to_ts - (stride * 1000)
            # reverse 1 second back in time
            buffer_from_ts = buffer_to_ts - (stride * 1000) - 1000
            logger.debug("querying stream " + self.rtmp_video_stream + "between " + str(buffer_from_ts) + " and " + str(buffer_to_ts) + ", diff[ms]: " + str(buffer_to_ts-buffer_from_ts))
            buffer = self.redis_conn.xrange(name=self.rtmp_video_stream, min=buffer_from_ts, max=buffer_to_ts, count=60)
            frames = Chunker(self.video_codec).frames(buffer)

            # find closest image to given timestamp
            min_diff = None
            for ts, frame in frames.items():
                if frame.pict_type.name == "I":
                    logger.debug("found I frame at " + str(ts))
                    if min_found is None:
                        d = frame.to_ndarray(format="bgr24")
                        chImage = ChImage(data=d, width=frame.width, height=frame.height, timestamp=ts)
                        min_found = chImage
                        min_diff = abs(timestamp - ts)
                        continue

                    diff = abs(timestamp - ts)
                    if diff < min_diff:
                        d = frame.to_ndarray(format="bgr24")
                        chImage = ChImage(data=d, width=frame.width, height=frame.height, timestamp=ts)
                        min_diff = diff
                        min_found = chImage
            if  min_found is not None:
                break

        return min_found