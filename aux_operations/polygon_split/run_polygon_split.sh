xhost +local:root # for the lazy and reckless

CGAL_IMAGE_NAME="cgal"
CGAL_VERSION="latest"

CONTAINER_NAME="cgal_polygon_split"

DOCKER_ARGS='-it'
DOCKER_ARGS+=" --rm"
DOCKER_ARGS+=" --user=1000:1000"
DOCKER_ARGS+=" --env=DISPLAY"
DOCKER_ARGS+=" --env=QT_X11_NO_MITSHM=1"
DOCKER_ARGS+=" -v /tmp/.X11-unix:/tmp/.X11-unix:rw"
DOCKER_ARGS+=" -v $PWD:/workspace"
DOCKER_ARGS+=" -w /workspace"
DOCKER_ARGS+=" --name $CONTAINER_NAME"

CMD="python3 polygon_split.py"

docker run $DOCKER_ARGS ${CGAL_IMAGE_NAME}:${CGAL_VERSION} $CMD 