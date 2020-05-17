import logging

import docker
from docker.models.containers import Container
from docker.models.images import Image


LOGGER = logging.getLogger(__name__)


class DockerClientWrapper:

    docker_client = docker.from_env()

    @classmethod
    def get_container_by_name(cls, container_name: str) -> Container:
        try:
            return cls.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            LOGGER.warning(('Container not found: %s', container_name))
            return None

    @classmethod
    def run_detached_container(cls, image_name: str, container_name: str, **kwargs) -> Container:
        container = cls.docker_client.containers.run(image_name, name=container_name, detach=True, **kwargs)
        LOGGER.info('Starting new container: %s', container.name)
        LOGGER.info('Container logs: %s', ['\n' + line for line in container.logs()])
        return container

    @classmethod
    def build_image(cls, path: str, tag: str, **kwargs) -> Image:
        build_image, build_logs = cls.docker_client.images.build(path=path, tag=tag, **kwargs)
        LOGGER.info('Building new image: %s', build_image)
        LOGGER.info('Build logs: %s', ['\n' + line for line in build_logs])
        return build_image

    @classmethod
    def is_container_running(cls, container_name: str) -> bool:
        containers = cls.docker_client.containers.list()
        if container_name in [c.name for c in containers]:
            return True
        return False
