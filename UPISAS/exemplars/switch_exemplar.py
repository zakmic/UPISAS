import docker
import logging
from UPISAS.exemplar import Exemplar

logging.getLogger().setLevel(logging.INFO)


class SwitchExemplar(Exemplar):
    """
    A class to manage the backend container for a self-adaptive system.
    """

    def __init__(self, auto_start: bool = False, container_name: str = "backend"):
        """
        Initialize the SwitchExemplar with the backend Docker configuration.

        :param auto_start: Whether to immediately start the container after creation.
        :param container_name: Name of the backend Docker container.
        """
        backend_docker_kwargs = {
            "name": container_name,
            "image": "switch-backend:latest",  # Backend image defined in Dockerfile
            "ports": {
                3001: 3001,
                8089: 8089,
                5001: 5001,
                8000: 8000,
            },
            "environment": {
                "ELASTICSEARCH_HOST": "http://elasticsearch:9200",
            },
        }

        super().__init__("http://localhost:8000", backend_docker_kwargs, auto_start)

        # Attach the container to the ELK network
        self.attach_to_network("elk")

    def attach_to_network(self, network_name):
        """
        Attaches the container to a specified Docker network.

        :param network_name: Name of the Docker network to attach the container to.
        """
        try:
            docker_client = docker.from_env()
            network = docker_client.networks.get(network_name)
            network.connect(self.exemplar_container.id)
            logging.info(f"Container '{self.exemplar_container.name}' attached to network '{network_name}'.")
        except docker.errors.NotFound:
            logging.error(f"Network '{network_name}' not found.")
        except Exception as e:
            logging.error(f"Error attaching to network '{network_name}': {e}")

    def start_run(self):
        """
        Start the backend container and ensure it is running.
        """
        try:
            container_status = self.get_container_status()
            if container_status == "running":
                logging.info("Container is already running.")
            else:
                logging.info("Starting the backend container...")
                self.start_container()
        except Exception as e:
            logging.error(f"Error during start_run execution: {e}")
