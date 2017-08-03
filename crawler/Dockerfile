FROM ubuntu:16.04
MAINTAINER Doro Wu <fcwu.tw@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN sed -i 's#http://archive.ubuntu.com/#http://tw.archive.ubuntu.com/#' /etc/apt/sources.list

# built-in packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends software-properties-common curl \
    && add-apt-repository ppa:fcwu-tw/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
        supervisor \
        openssh-server pwgen sudo unzip vim wget cron rsyslog \
        net-tools \
        lxde x11vnc xvfb \
        gtk2-engines-murrine ttf-ubuntu-font-family \
        libreoffice firefox libmysqlclient-dev \
        fonts-wqy-microhei \
        language-pack-zh-hant language-pack-gnome-zh-hant firefox-locale-zh-hant libreoffice-l10n-zh-tw \
        nginx \
        python-pip python-dev build-essential \
        mesa-utils libgl1-mesa-dri \
        gnome-themes-standard gtk2-engines-pixbuf gtk2-engines-murrine pinta \
        dbus-x11 x11-utils \
        postfix libsasl2-modules mailutils 

# tini for subreap
ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /bin/tini
RUN chmod +x /bin/tini

# pytohn lib
ADD image /
RUN pip install setuptools wheel && pip install -r /usr/lib/web/requirements.txt

# opencv
RUN apt-get update \
    && apt-get install -y -q wget curl build-essential checkinstall  cmake python2.7 python2.7-dev \
       libopencv-dev yasm libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev libv4l-dev \ 
       libtbb-dev libqt4-dev libgtk2.0-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev \
       libxvidcore-dev x264 v4l-utils pkg-config \
    && curl -sL https://github.com/Itseez/opencv/archive/3.0.0.tar.gz | tar xvzf -  \
    && mkdir -p opencv-3.0.0/release \
    && cd opencv-3.0.0/release \
    && cmake -DWITH_FFMPEG=OFF -DWITH_OPENEXR=OFF -DBUILD_TIFF=OFF -DWITH_CUDA=OFF -DWITH_NVCUVID=OFF -DBUILD_PNG=OFF .. \
    && make \
    && make install \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf \
    && ldconfig \
    && ln /dev/null /dev/raw1394 \
    && cd / \
    && rm -rf opencv-3.0.0 \
    && pip install opencv-python
   
# selenium firefox driver
RUN wget "https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz" \
    && tar -zxvf geckodriver-v0.16.1-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v0.16.1-linux64.tar.gz

# selenium chrome/driver
RUN wget "https://chromedriver.storage.googleapis.com/2.31/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip -d /usr/local/bin \
    && rm chromedriver_linux64.zip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

EXPOSE 80
WORKDIR /root
ENV HOME=/home/ubuntu \
    SHELL=/bin/bash
ENTRYPOINT ["/startup.sh"]
