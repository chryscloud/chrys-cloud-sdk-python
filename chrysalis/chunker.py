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

import io
import av
from .log import logger
from .models import ChImage
import numpy

class Chunker:

    def __init__(self, codec):
        self.codec = codec

    def frames(self, buffer):
        """
        Decoding raw video packets into frames

        Returns
        -------
        Returns dictionary od key = timestamp, value = av.frame.Frame
        """
        frames = self.__decode_video_packets_to_frames(buffer)
        return frames

    def packets(self, buffer):
        """
        Raw packets

        Returns
        -------
        Returns dictionary with key as timestamp of a packet and av.Packet value
        """
        return self.__packet_chunker(buffer)

    def __decode_video_packets_to_frames(self, buffer):
        """
        Decoding raw video packets into frames

        Returns
        -------
        Returns dictionary od key = timestamp, value = av.frame.Frame
        """
        all_frames = {}
        packets = self.__packet_chunker(buffer)
        if len(packets) > 0:
            for ts, packet in packets.items():
                try:
                    frames = self.codec.decode(packet)
                    for frame in frames:
                        all_frames[ts] = frame
                except Exception as e:
                    print(e)
                    continue
                    # logger.debug("packet decoding failed", exc_info=True)
        return all_frames

    def __packet_chunker(self, buffer):
        """
        Chunks packets into a dictionary with key as timestamp of a packet and av.Packet value
        """
        packet_results = {}
        if buffer:
            buffer_array = []
            buffer_array_ts = []
            for x in buffer:
                timestamp_x = x[0].decode("utf-8")
                dictionary_x = x[1]
                splitted = timestamp_x.split("-")
                timestamp = splitted[0]
                content = {}
                for key, value in dictionary_x.items():
                    content[key.decode("utf-8")] = value
                buffer_array.append(content["frame"])
                buffer_array_ts.append(int(timestamp))
            for idx, fr in enumerate(buffer_array):
                frame_buf = io.BytesIO(fr)
                size = frame_buf.getbuffer().nbytes
                packet = av.Packet(size)
                frame_buf.readinto(packet)
                
                frame_ts = buffer_array_ts[idx]
                packet_results[frame_ts] = packet

        return packet_results

