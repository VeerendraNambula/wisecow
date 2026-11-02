# Wisecow

A tiny HTTP service that displays a random `fortune` rendered by `cowsay`. The original Bash launcher is retained; the HTTP implementation uses Python's standard library so request handling, health checks, and container operation are predictable.

## Run locally

Requirements: Python 3.10+, `fortune-mod`, and `cowsay`.

On Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y fortune-mod cowsay
./wisecow.sh
```

Open `http://localhost:4499`. Set `PORT` to change the listening port. The `/healthz` endpoint returns `200 OK` for container and Kubernetes probes.

## Run with Docker

```bash
docker build -t wisecow .
docker run --rm -p 4499:4499 wisecow
```

The image runs as a non-root user, exposes only the HTTP port, and includes a Docker health check.

## Kubernetes deployment

The manifests in `k8s/` include a two-replica Deployment, ClusterIP Service, TLS Ingress, and cert-manager Certificate.

Before applying them:

1. Replace `wisecow.example.com` in `k8s/ingress.yaml` and `k8s/certificate.yaml` with a DNS name you control.
2. Ensure an NGINX Ingress Controller and cert-manager are installed.
3. Ensure a ClusterIssuer named `letsencrypt-prod` exists, or change `issuerRef` to your configured issuer.
4. Ensure the container image is available at `ghcr.io/veerendranambula/wisecow:latest`. GitHub Actions builds and publishes it on pushes to `main`.
5. Apply the manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/certificate.yaml
kubectl apply -f k8s/ingress.yaml
```

TLS terminates at the Ingress. cert-manager provisions the certificate secret; do not commit private keys or TLS secrets.

## CI/CD

GitHub Actions runs unit tests on pushes and pull requests. On pushes to `main`, it builds and publishes a container image to GitHub Container Registry after tests pass.

For a public repository, make the GHCR package public separately if you want unauthenticated Kubernetes pulls. Private packages require an image pull secret.

## Security and repository visibility

The original challenge brief requested a private repository and access for a named collaborator. This repository is currently public, so do not place credentials, private keys, personal data, or cluster configuration here. If the original access restriction still applies, change repository visibility and grant collaborator access in GitHub repository settings.
