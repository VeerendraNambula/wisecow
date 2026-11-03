# Wisecow

A lightweight HTTP service that serves a random `fortune` message rendered with `cowsay`. The repository packages the service in a minimal Docker image and includes Kubernetes manifests and a GitHub Actions workflow for testing and publishing the image to GitHub Container Registry (GHCR).

## What it demonstrates

- A small Python HTTP service built with the standard library.
- Health-check endpoint for containers and Kubernetes probes.
- Safe HTML escaping of generated terminal output.
- Container hardening: non-root execution and a Docker health check.
- Kubernetes deployment with readiness/liveness probes, resource limits, and a restricted security context.
- CI testing and automated container publishing on pushes to `main`.

## Architecture

```mermaid
flowchart TD
    Client[Browser / HTTP client] --> Service[Wisecow HTTP service :4499]
    Service --> Health[/healthz]
    Service --> Root[GET /]
    Root --> Fortune[fortune command]
    Fortune --> Cowsay[cowsay command]
    Cowsay --> Escape[HTML escaping]
    Escape --> Response[HTML response]
    subgraph Delivery
      CI[GitHub Actions] --> Tests[Unit tests]
      Tests --> Build[Docker build]
      Build --> GHCR[GitHub Container Registry]
      GHCR --> K8s[Kubernetes Deployment]
    end
```

## Endpoints

| Method | Path | Behavior |
|---|---|---|
| `GET` | `/` | Returns an HTML page containing a randomly generated fortune rendered by cowsay |
| `GET` | `/healthz` | Returns `200 OK` and `ok` for health probes |
| `GET` | Any other path | Returns `404 Not Found` |

The server listens on port `4499` by default. Set the `PORT` environment variable to override it.

## Run locally

### Requirements

- Python 3.10+
- `fortune-mod`
- `cowsay`

On Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y fortune-mod cowsay
python3 server.py
```

Open [http://localhost:4499](http://localhost:4499). Visit the root path again to get another fortune.

The original shell launcher is also retained:

```bash
./wisecow.sh
```

## Run with Docker

Build and start the service:

```bash
docker build -t wisecow .
docker run --rm -p 4499:4499 wisecow
```

Open [http://localhost:4499](http://localhost:4499).

The image uses a slim Python base, installs the two command-line dependencies, runs as UID/GID `10001`, and defines a Docker health check against `/healthz`.

To use a different host port:

```bash
docker run --rm -e PORT=4499 -p 8080:4499 wisecow
```

Then visit [http://localhost:8080](http://localhost:8080).

## Run tests

The test suite uses Python's built-in `unittest` framework:

```bash
python -m unittest discover -s tests -v
```

The tests cover the health endpoint, HTML escaping of generated output, and 404 handling for unknown paths. External `fortune` and `cowsay` processes are mocked in the root-route test.

## Kubernetes deployment

The `k8s/` directory contains:

| Manifest | Purpose |
|---|---|
| `deployment.yaml` | Two replicas, probes, resource requests/limits, and container security settings |
| `service.yaml` | ClusterIP service exposing the application inside the cluster |
| `ingress.yaml` | NGINX Ingress routing and TLS configuration |
| `certificate.yaml` | cert-manager Certificate resource |

### Prerequisites

- A Kubernetes cluster and configured `kubectl` context.
- NGINX Ingress Controller.
- cert-manager.
- A ClusterIssuer named `letsencrypt-prod`, or an issuer reference adjusted to match your cluster.
- A DNS name that you control and that points to your Ingress endpoint.
- The image available at `ghcr.io/veerendranambula/wisecow:latest`.

### Configure and apply

1. Replace `wisecow.example.com` in `k8s/ingress.yaml` and `k8s/certificate.yaml` with your DNS name.
2. Confirm the issuer name and Ingress class match your cluster.
3. Ensure the GHCR package is public for unauthenticated image pulls. If it is private, configure an image pull secret.
4. Apply the manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/certificate.yaml
kubectl apply -f k8s/ingress.yaml
```

Check rollout and service state:

```bash
kubectl rollout status deployment/wisecow
kubectl get pods,svc,ingress
```

TLS terminates at the Ingress. cert-manager provisions the certificate secret; do not commit private keys or TLS secrets.

## CI/CD

GitHub Actions runs the unit tests on pushes and pull requests targeting `main`. On a push to `main`, after the test job succeeds, the workflow builds and publishes two image tags:

- `ghcr.io/veerendranambula/wisecow:latest`
- `ghcr.io/veerendranambula/wisecow:<commit-sha>`

The workflow uses the repository's `GITHUB_TOKEN` to authenticate to GHCR. Make the package public separately if Kubernetes nodes need to pull it without credentials.

## Security notes

- The service escapes the fortune output before inserting it into HTML.
- The container runs as a non-root user.
- The Kubernetes pod disables service-account token mounting, drops Linux capabilities, disallows privilege escalation, uses a read-only root filesystem, and sets resource limits.
- Do not commit credentials, private keys, personal data, or cluster-specific secrets.
- The Kubernetes manifests are templates: configure DNS, Ingress, cert-manager, and image-pull access for your own cluster before deploying.

## Repository structure

```text
wisecow/
├── .github/workflows/ci.yml
├── k8s/
│   ├── certificate.yaml
│   ├── deployment.yaml
│   ├── ingress.yaml
│   └── service.yaml
├── tests/test_server.py
├── Dockerfile
├── server.py
├── wisecow.sh
└── README.md
```

## License

See [LICENSE](LICENSE).
