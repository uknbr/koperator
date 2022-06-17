import kopf
import kubernetes.client
from kubernetes.client.rest import ApiException

@kopf.on.create("uknbr.io", "v1", "milks")
def on_create(spec, name, namespace, logger, **kwargs):
    replicas = spec.get("replicas", 1) 
    url = spec.get("url")

    if not url:
        raise kopf.PermanentError("URL of milk image must be set!")

    logger.info("Starting creation of Milk")
    logger.info(f"Detected name is '{name}'")

    json = {
        "kind": "Deployment",
        "apiVersion": "apps/v1",
        "metadata": {
            "name": f"milk-{name}",
            "labels": {
                "app": f"milk-{name}"
            }
        },
        "spec": {
            "replicas": replicas,
            "selector": {
                "matchLabels": {
                    "app": f"milk-{name}"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": f"milk-{name}"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": f"milk-{name}",
                            "image": "uknbr/milk:latest",
                        }
                    ]
                }
            },
        },
    }

    kopf.adopt(json)
    api = kubernetes.client.AppsV1Api()

    # Deployment
    try:
        deploy = api.create_namespaced_deployment(namespace=namespace, body=json)
        logger.info(f"Successfully created deployment {deploy.metadata.uid}")
    except ApiException as e:
        logger.error(f"Failed to create deployment: {repr(e)}")

    json = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "labels": {
                "app": f"milk-{name}"
            },
            "name": f"milk-{name}"
        },
        "spec": {
            "ports": [
                {
                    "port": 8080,
                    "protocol": "TCP",
                    "targetPort": 8080
                }
            ],
            "selector": {
                "app": f"milk-{name}"
            },
            "sessionAffinity": "None",
            "type": "ClusterIP"
        }
    }

    kopf.adopt(json)
    api = kubernetes.client.CoreV1Api()

    # Service
    try:
        service = api.create_namespaced_service(namespace=namespace, body=json)
        logger.info(f"Successfully created service {service.metadata.uid}")
    except ApiException as e:
        logger.error(f"Failed to create service: {repr(e)}")

    json = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"milk-{name}"
        },
        "spec": {
            "rules": [
                {
                    "host": "localhost",
                    "http": {
                        "paths": [
                            {
                                "backend": {
                                    "service": {
                                        "name": f"milk-{name}",
                                        "port": {
                                            "number": 8080
                                        }
                                    }
                                },
                                "path": f"/milk-{name}",
                                "pathType": "Prefix"
                            }
                        ]
                    }
                }
            ]
        }
    }

    kopf.adopt(json)
    api = kubernetes.client.NetworkingV1Api()
    
    # Ingress
    try:
        ingress = api.create_namespaced_ingress(namespace=namespace, body=json)
        logger.info(f"Successfully created ingress {ingress.metadata.uid}")
    except ApiException as e:
        logger.error(f"Failed to create ingress: {repr(e)}")

    # Children
    return {'children': [deploy.metadata.uid, service.metadata.uid, ingress.metadata.uid]}