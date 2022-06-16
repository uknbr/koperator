import kopf
import kubernetes.client
from kubernetes.client.rest import ApiException

@kopf.on.create("uknbr.io", "v1", "indicatorpods")
def create_fn(spec, name, namespace, logger, **kwargs):
    restart = spec.get('restarts', 0) 
    label = spec.get('label', 'error')

    logger.info("Starting creation of label")
    logger.info(f"Detected name is '{name}'")
    logger.info(f"Add label {label} when restart count is {restart}")

    body = {
        "data": {
            "label": f"{label}"
        },
        "metadata": {
            "name": f"{name}-config"
        }
    }

    api = kubernetes.client.CoreV1Api()
    try:
        cm = api.create_namespaced_config_map(namespace, body)
        logger.info(f"Successfully created configmap with UID {cm.metadata.uid}")
    except ApiException as e:
        logger.error(f"indicatorpods -> failed to create configmap: repr{e}")