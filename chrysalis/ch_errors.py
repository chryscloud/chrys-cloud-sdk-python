
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

class VideoFailedToStart(Exception):
    """ raise when video failed to start in designated time """
    pass

class FolderNotFound(Exception):
    """ raise when folder doesn't exist """
    pass

class VideoHistoryNotFound(Exception):
    """ raise when video from history can't be retrieved due to recordings not existing """
    pass

class InfrequentException(Exception):
    """ raise when queries to streaming video not frequent enough """