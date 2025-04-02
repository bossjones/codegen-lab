---
project_name:
deployments:
  - url:
    name: dev
git_repo:
developer_contacts:
  - name: Malcolm Jones
    username: bossjones
tags:
  - MinIO
  - S3
  - under construction
---

# 🚧 MinIO

## About

[MinIO][] is an object storage solution that provides an Amazon Web Services
S3-compatible API and supports all core S3 features. MinIO is built to deploy
anywhere - public or private cloud, baremetal infrastructure, orchestrated
environments, and edge infrastructure.

## Setup in Kubernetes (WIP)

### Create pod

!!! note inline end "🚧 Todo: This is not in git yet!"

[[@bossjones]] has the manifest below in `minio-dev.yaml`

??? note "Kubernetes manifest (`minio-dev.yaml`)"

    ```yaml
    # Deploys a MinIO pod
    apiVersion: v1
    kind: Pod
    metadata:
    labels:
        app: minio
    name: minio
    spec:
    containers:
    - name: minio
        image: quay.io/minio/minio:latest
        command:
        - /bin/bash
        - -c
        args:
        - minio server /data --console-address :9090
        resources:
        limits:
            cpu: "1"
            memory: 2048Mi
        requests:
            cpu: 100m
            memory: 256Mi
    ```

He runs this command to create a MinIO pod:

```shell
kubectl apply -f minio-dev.yaml
```

and now the pod is running:

```shell
$ kubectl config current-context
gtw-paas-sandbox

$ kubectl get pod/minio
NAME    READY   STATUS    RESTARTS   AGE
minio   1/1     Running   0          9h
```

### `kubectl port-forward`

There's no `service` or `ingressroute` yet, so he's using a `port-forward`:

```shell
kubectl port-forward pod/minio 9000 9090
```

!!! info inline end "Note"

    The `kubectl port-forward` command may exit from time to time, because of
    network connectivity problems.
    You will need to rerun it when that happens so that the localhost links
    work.

That allows these links to work:

- http://localhost:9090/browser/boss-bucket
- http://localhost:9090/access-keys

### Access using AWS CLI

=== "Command"

    ```shell
    export AWS_ACCESS_KEY_ID=theaccesskey
    export AWS_SECRET_ACCESS_KEY=thesecretkey
    aws --endpoint-url http://localhost:9000 s3 ls boss-bucket
    ```

=== "Output"

    ```
    $ export AWS_ACCESS_KEY_ID=theaccesskey
    export AWS_SECRET_ACCESS_KEY=thesecretkey
    aws --endpoint-url http://localhost:9000 s3 ls boss-bucket
                            PRE folder1/
    2024-02-13 23:03:45      26044 SmartHighlights_PlantUML_class_diagram.png
    ```

## Links

- [Quickstart: MinIO for Kubernetes](https://min.io/docs/minio/kubernetes/upstream/index.html#quickstart-minio-for-kubernetes)
- [AWS CLI with MinIO Server](https://min.io/docs/minio/linux/integrations/aws-cli-with-minio.html)

### Scratch links

These only work on [[@bossjones]]'s machine (these are hitting a MinIO pod in
Kubernetes but currently using a `kubectl port-forward` to access them) and
should be removed soon:

- http://localhost:9090/browser/boss-bucket
- http://localhost:9090/access-keys


[MinIO]: https://min.io/
