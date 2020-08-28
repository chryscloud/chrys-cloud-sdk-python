# Chrysalis Python Cloud SDK

This repository houses the official Chrysalis Cloud Python SDK for use with [Chryscloud.com](https://chryscloud.com/) cloud, end-to-end media streaming and analytics platform.

Chrysalis Cloud SDK aims to provide easy and powerful control over live media streaming consumption and ingestion into various machine learning libraries in the cloud.

If you're looking for a hybrid edge-cloud solution we recommend you look into our open source project [Chrysalis Edge Proxy](https://github.com/chryscloud/video-edge-ai-proxy)

## Contents

- [Features](#features)
- [Prerequisite](#prerequisite)
- [Installation](#installation)
- [Usage](#usage)
    - [Probing](#probing-the-stream)
    - [Thumbnail from video](#Thumbnail-image-from-video-stream)
    - [Live stream with OpenCV](#displaying-live-stream-with-opencv)
    - [HLS streaming](#hls-streaming)
- [Development](#development)
    - [Mac OS X](#mac-os-x)
    - [Ubuntu >= 18.04 LTS](#mac-os-x)
    - [Ubuntu < 18.04 LTS](#mac-os-x)
    - [Installing](#installing)

## Features

- Easy integration with numerous machine learning platforms
- Support for easy access to RTMP live video stream from Chrysalis Cloud (live video/audio streaming)
- Supporting for any camera that has RTMP streaming abilities
- Deals with complexities of media stream management
- Secure access media streams

## Prerequisite

- [Install anaconda](https://docs.anaconda.com/anaconda/install/)
- [Install FFmpeg > 4.0](https://ffmpeg.org/download.html)

Check `FFmpeg` version:
```
ffmpeg -version
```

## Installation

Create `environment.yml` file. 

You can easily add to this file dependencies and additional image manipulation libraries such as Pillow and OpenCV.

[If you need GPU support, you can check how to work with Anaconda and GPU packages](https://docs.anaconda.com/anaconda/user-guide/tasks/gpu-packages/). 


```yaml
name: chryssdk
channels:
  - conda-forge
dependencies:
  - ca-certificates=2020.1.1=0
  - certifi=2020.4.5.1=py37_0
  - python=3.7.7=hcf32534_0_cpython
  - av=7.0.1
  - numpy=1.18.1
  - redis-py=3.4.1
  - pip:
    - chryssdk=1.0.0
    - Cython
```

Create new conda environment:
```shell
conda env create -f environment.yml
```

## Usage

Probing returns information about the streaming media. It gives you a sense if the camera is streaming, when it was last seen, what is the frame cache duration stored on the Chrysalis streaming server.

- all images are in numpy format.
- all images are in bgr24 pixel format.

```python
import chrysalis
# connection to Chrysalis Cloud
chrys = chrysalis.RtmpMedia(host="https://myserver.at.chrysvideo.com", port="1234", password="mypassword", ssl_ca_cert="mycert.cer")
# returns ProbeInfo object
probe = chrys.Probe()
print("start {}, end {}, duration {} s, assessed fps {}".format(probe.start_timestamp, probe.end_timestamp, probe.duration, probe.fps))
```

The ProbeInfo object returns the information about cached frames as well as assessment of FPS (frames per second) streamed from the camera.

`start_timestamp` and `end_timestamp` are UTC times in milliseconds since epoch.

```python
ProbeInfo Attributes
    ----------
    start_timestamp : int
        Earlies contained media data in video stream cache
    end_timestamp : int
        Latest contained media data in video stream cache
    duration : int
        Duration of the buffered media stream in seconds
    fps : int
        Approximation of Frames per Second of source stream
    """
```

## Retrieve latest video image from a live stream

Chrysalis Cloud Python SDK takes care of delivering crisp and clear images from your live video stream, regardless of the processing speeds, speed ups or slow downs because of the latency or even if your camera disconnects from the network.

```python
import chrysalis

# connection to Chrysalis Cloud
chrys = chrysalis.RtmpMedia(host="https://myserver.at.chrysvideo.com", port="1234", password="mypassword", ssl_ca_cert="mycert.cer")

# Perpetual reading of the stream
while True:
    # VideoLatestImage returns ChImage object
    img = chrys.VideoLatestImage()
```

`ChImage` object returned from VideoLatestImage has a following structure:

```python
ChImage Attributes
    ----------
    start_timestamp : int
        Earlies contained media data in video stream cache
    end_timestamp : int
        Latest contained media data in video stream cache
    duration : int
        Duration of the buffered media stream in seconds
    fps : int
        Approximation of Frames per Second of source stream
    """
```

VideoLatestImage returns `None` image when frame not available.

VideoLatestImage might return None in cases when querying for the next frame is faster than the camera stream produces them.

The SDK will not return already consumed frames (images) in the perpetual reading of the stream.

You can also consume live stream images from mutliple sinks in case when you need to run the same live stream (e.g. the same image) through multiple Computer Vision algorithms. Not returning already consumed frames applies per SDK instance basis.

## Retrieve video images from the past

Based on what is available in the frame cache on Chrysalis streaming nodes you can also query video images from the past. Use `Probing` in case you need more information how much back in time you can query the video stream.

```python
import chrysalis

# connection to Chrysais Cloud
chrys = chrysalis.RtmpMedia(hos="https://myserver.at.chrysvideo.com", prt="1234", password="mypassword", ssl_ca_cert="mycert.cer")

probe = ch.Probe()
start = probe.end_timestamp - (1000 * 30) # 30 seconds in the past
end = probe.end_timestamp - (1000 * 15) # until 15 seconds in the past (end > start)

# Perpetual reading of the stream until end is reached
while True:
    # VideoLatestImage returns ChImage object
    img = ch.VideoPastImage(start, end)
```

## Thumbnail image from video stream

Thumbnails are in `bgr24 format in numpy array`. In fact all images for local consumption are in the same format. This makes it easy to consume images in any processing and analytics after. 

```python
import chrysalis

chrys = chrysalis.RtmpMedia(host="https://myserver.at.chrysalis.com", port="1234", password="mypassword", ssl_ca_cert="mycert.crt")

 d = datetime.today() - timedelta(hours=0, minutes=0, seconds=2)
img = chrys.Screenshot(dt=d)
```

Due to the nature of H.264 straming it is not guaranteed the successfulness of the Screenshot method. In case no screenshot was found `img = None`. 

This function tries to traverse the H.264 buffered stream seeking for I-Frame. the closest I-Frame to given `dt` (timestamp) is returned if I-Frame found. 

## Turn Storage On and Off

Based on video analysis you can decide to store a stream into the permanent Chrysalis Cloud storage. Since live video form a webcam might be streaming 24/7 we don’t necessarily need to store everything, but rather we can perform simple analysis (e.g. movement detection, face recognition, …) to decide when and for how long we want to permanently store that video segment.

`Coming soon`

## Example: Display live stream with OpenCV

```python
import chrysalis

# connection to Chrysalis Cloud
chrys = chrysalis.RtmpMedia(host="https://myserver.at.chrysalis.com", port="1234", password="mypassword", ssl_ca_cert="mycert.cer")

# Perpetual reading of the stream
while True:
    # VideoLatestImage returns ChImage object
    img = chrys.VideoLatestImage()
    if img is not None:
        cv2.imshow("live video", img.data)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
```

# Development

## Install FFmpeg

### Mac OS X

```
brew install ffmpeg pkg-config
```

### Ubuntu >= 18.04 LTS

On Ubuntu 18.04 LTS everything can come from the default sources:

```
sudo apt-get install -y python-dev pkg-config

# Library components
sudo apt-get install -y \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
```

### Ubuntu < 18.04 LTS

On older Ubuntu releases you will be unable to satisfy these requirements with the default package sources. We recommend compiling and installing FFmpeg from source. For FFmpeg:

```
sudo apt install \
    autoconf \
    automake \
    build-essential \
    cmake \
    libass-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libtheora-dev \
    libtool \
    libvorbis-dev \
    libx264-dev \
    pkg-config \
    wget \
    yasm \
    zlib1g-dev

wget http://ffmpeg.org/releases/ffmpeg-3.2.tar.bz2
tar -xjf ffmpeg-3.2.tar.bz2
cd ffmpeg-3.2

./configure --disable-static --enable-shared --disable-doc
make
```


## Installing


```bash
git clone https://github.com/cocoonhealth/ChrysalisPythonSDK.git

cd ChrysalisPythonSDK

sudo pip install -e . 
```
This should install it's dependencies also. 

