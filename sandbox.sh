xhost +local:root # for the lazy and reckless

SHAPELY_IMAGE_NAME="shapely"
SHAPELY_VERSION="latest"

CONTAINER_NAME="shapely_sandbox"

DOCKER_ARGS='-it'
#DOCKER_ARGS+=" --user=1000:1000"
DOCKER_ARGS+=" --env=DISPLAY"
DOCKER_ARGS+=" --env=QT_X11_NO_MITSHM=1"
DOCKER_ARGS+=" -v /tmp/.X11-unix:/tmp/.X11-unix:rw"
DOCKER_ARGS+=" -v $PWD:/workspace"
DOCKER_ARGS+=" -w /workspace"
DOCKER_ARGS+=" --name $CONTAINER_NAME"

CMD="bash"

EXISTING_STOPPED_CONTAINER=$(docker ps --all --quiet --filter "name=$CONTAINER_NAME" --filter "exited=0")
EXISTING_RUNNING_CONTAINER=$(docker ps --all --quiet --filter "name=$CONTAINER_NAME" --filter "status=running")

echo $EXISTING_STOPPED_CONTAINER
echo $EXISTING_RUNNING_CONTAINER

if [ -z $EXISTING_STOPPED_CONTAINER ] && [ -z $EXISTING_RUNNING_CONTAINER ]; then
    docker run $DOCKER_ARGS ${SHAPELY_IMAGE_NAME}:${SHAPELY_VERSION} $CMD 
elif [ -z $EXISTING_RUNNING_CONTAINER ]; then
    docker start $EXISTING_STOPPED_CONTAINER
    docker exec -ti $EXISTING_STOPPED_CONTAINER bash
else
    docker exec -ti $EXISTING_RUNNING_CONTAINER bash
fi
