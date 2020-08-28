
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

import math

class ProbeInfo(object):
    """
    ProbeInfo object hold stream probing data

    Attributes
    ----------
    start_timestamp : int
        Earlies contained media data in video stream cache
    end_timestamp : int
        Latest contained media data in video stream cache
    duration : int
        Duration of the buffered media stream in seconds
    """
    start_timestamp = 0
    end_timestamp = 0
    duration = 0
    fps = 0

    def __init__(self, start, end, fps=0):
        self.start_timestamp = start
        self.end_timestamp = end
        self.duration = math.ceil((end-start) / 1000)
        self.fps = fps


class ChImage(object):
    """
    Chrysalis Image object

    Attributes
    ----------
    data : numpy.ndarray
        Image data in BGR24 format
    timestamp: int
        Timestamp of the image stored in video cache
    width: int
        width of the image
    height: int
        height of the image

    Methods
    -------
    describe()
        Describes the acquired image
    """

    data = None # numpy 
    timestamp = 0
    width = 0
    height = 0
    frame_type = None # can be one of the I, B, P

    def __init__(self, data, width=0, height=0, timestamp=0, frame_type=None):
        self.data = data
        self.width = width
        self.height = height
        self.timestamp = timestamp
        self.frame_type = frame_type

    def describe(self):
        print("TBD")