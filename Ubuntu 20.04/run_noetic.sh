#!/usr/bin/env bash
set -e

CONTAINER_NAME="morai_noetic_topic"
IMAGE_NAME="morai-noetic-topic:camera"
ROOT="/home/ktj/MORAI/Ubuntu 20.04"

# X11 허용
xhost +SI:localuser:$(whoami) >/dev/null
xhost +local:docker >/dev/null

# 이미 실행 중이면 접속
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[INFO] Container already running. Entering..."
  docker exec -it ${CONTAINER_NAME} bash
  exit 0
fi

# 정지된 컨테이너가 있으면 시작 후 접속
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[INFO] Starting existing container..."
  docker start ${CONTAINER_NAME} >/dev/null
  docker exec -it ${CONTAINER_NAME} bash
  exit 0
fi

# 없으면 GUI 설정 포함해서 새로 생성
echo "[INFO] Creating persistent GUI-enabled container..."
docker run -d \
  --name ${CONTAINER_NAME} \
  --net=host \
  --ipc=host \
  --privileged \
  --group-add video \
  --group-add dialout \
  --group-add plugdev \
  -e DISPLAY=${DISPLAY} \
  -e QT_X11_NO_MITSHM=1 \
  -e LIBGL_ALWAYS_SOFTWARE=1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v /dev:/dev \
  -v /dev/bus/usb:/dev/bus/usb \
  -v "$ROOT":/home/ktj/MORAI:rw \
  ${IMAGE_NAME} \
  tail -f /dev/null

docker exec -it ${CONTAINER_NAME} bash
