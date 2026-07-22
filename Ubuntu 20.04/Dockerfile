FROM ros:noetic-ros-base

ARG USERNAME=ktj
ARG USER_UID=1000
ARG USER_GID=1000

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    sudo \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    nano \
    vim \
    usbutils \
    udev \
    v4l-utils \
    libv4l-dev \
    ros-noetic-image-transport \
    ros-noetic-image-transport-plugins \
    ros-noetic-camera-info-manager \
    ros-noetic-cv-bridge \
    ros-noetic-diagnostic-updater \
    ros-noetic-sensor-msgs \
    net-tools \
    iputils-ping \
    python3-pip \
    python3-catkin-tools \
    python3-rosdep \
    ros-noetic-rqt \
    ros-noetic-rqt-graph \
    ros-noetic-turtlesim \
    x11-apps \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    ros-noetic-tf \
    ros-noetic-tf2-ros \
    ros-noetic-rosbridge-server \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -f video \
    && groupadd -f dialout \
    && groupadd -f plugdev \
    && if ! getent group ${USER_GID}; then groupadd --gid ${USER_GID} ${USERNAME}; fi \
    && useradd -s /bin/bash --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME} \
    && usermod -aG sudo,video,dialout,plugdev ${USERNAME} \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}

RUN mkdir -p /home/${USERNAME}/catkin_ws/src \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/catkin_ws

USER ${USERNAME}
WORKDIR /home/${USERNAME}/catkin_ws

RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin_make"

RUN echo "source /opt/ros/noetic/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "source /home/${USERNAME}/catkin_ws/devel/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "export ROS_MASTER_URI=http://127.0.0.1:11311" >> /home/${USERNAME}/.bashrc \
    && echo "export ROS_IP=127.0.0.1" >> /home/${USERNAME}/.bashrc

WORKDIR /home/${USERNAME}/catkin_ws
