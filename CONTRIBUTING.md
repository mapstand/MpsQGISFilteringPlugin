# Contributing

## Local Development with Docker

The repo includes a `docker-compose.yml` that runs QGIS with the plugin mounted directly from your working directory, so any code changes are reflected immediately on restart.

### Prerequisites

- Docker and Docker Compose
- An X server (Linux: built-in, Mac: [XQuartz](https://www.xquartz.org/), Windows: [VcXsrv](https://sourceforge.net/projects/vcxsrv/))

### Setup

All commands must be run from the `docker/` directory:

```bash
cd docker
```

1. Run setup (copies the env file and sets `UID`/`GID` from your current user automatically):

   ```bash
   make setup
   ```

2. Start QGIS:

   ```bash
   make run
   ```

   This handles the `xhost` permission and starts the container in one step.

3. Stop the container:

   ```bash
   make stop
   ```

### Switching QGIS versions

Override `QGIS_VERSION` with any tag from the [qgis/qgis Docker Hub](https://hub.docker.com/r/qgis/qgis/tags) repository:

```bash
make run QGIS_VERSION=ltr
```

Common tags:

| Tag | Version |
|---|---|
| `latest` | Latest QGIS 4.x |
| `stable` | Latest stable release |
| `ltr` | Latest long-term release (currently 3.44) |
| `3.44` | QGIS 3.44.x |
| `4.0` | QGIS 4.0.x |

Full list of available tags: [qgis/qgis on Docker Hub](https://hub.docker.com/r/qgis/qgis/tags)
