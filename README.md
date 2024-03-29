# 🐳 Docker Compose for Backup Utility 🚀

This repository contains a Docker Compose setup for a backup utility service, designed to simplify your backup management tasks with Docker. 📦🔒

## Services 🛠️

Below is an overview of the services defined in our `docker-compose.yml`:

| Service | Description                                                       | Image                           | Environment Variables                                  |
| ------- | ----------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------ |
| backup  | A service for running backup scripts. It executes once and exits. | mbround18/backup-utility:latest | INPUT_FOLDER, OUTPUT_FOLDER, OUTPUT_USER, OUTPUT_GROUP |
| cron    | A service for running backup that can run on a cron.              | mbround18/backup-cron:latest    | INPUT_FOLDER, OUTPUT_FOLDER, OUTPUT_USER, OUTPUT_GROUP |

## Getting Started 🚀

To get started with this Docker Compose project, ensure you have Docker and Docker Compose installed on your system.

```yaml
version: "3.8"
services:
  backup:
    image: mbround18/backup-utility:latest
    environment:
      - INPUT_FOLDER=/input
      - OUTPUT_FOLDER=/output
    volumes:
      - ./input:/input
      - ./output:/output
  cron:
    image: mbround18/backup-cron:latest
    environment:
      - SCHEDULE=0 0 * * *
      - INPUT_FOLDER=/input
      - OUTPUT_FOLDER=/output
    volumes:
      - ./input:/input
      - ./output:/output
    restart: unless-stopped
```

### Contributing

To get started with this Docker Compose project, ensure you have Docker and Docker Compose installed on your system.

1. Clone this repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate into the repository directory:
   ```bash
   cd <repository-name>
   ```
3. Run Docker Compose up:
   ```bash
   docker-compose up -d
   ```

## Configuration 🛠

To customize the backup service, you can modify the environment variables in the `docker-compose.yml` file. Here's a brief on what each variable does:

| Variable         | Description                                                                                   | Default Value |
| ---------------- | --------------------------------------------------------------------------------------------- | ------------- |
| `INPUT_FOLDER`   | The folder to back up from.                                                                   | None          |
| `OUTPUT_FOLDER`  | The destination folder for backups.                                                           | None          |
| `OUTPUT_USER`    | UID for the output files.                                                                     | `1000`        |
| `OUTPUT_GROUP`   | GID for the output files.                                                                     | `1000`        |
| `SCHEDULE`       | The cron schedule for the backup. (Only used by the `cron` service.)                          | `0 * * * *`   |
| `RETAIN_N_DAYS`  | The number of days to retain backups. (Only used by the `cron` service. `0` means disabled.)  | `0`           |
| `RETAIN_N_FILES` | The number of files to retain backups. (Only used by the `cron` service. `0` means disabled.) | `0`           |

Feel free to explore the `docker-compose.yml` for additional configurations and services.

## Contribution 🤝

Contributions are welcome! If you have suggestions or improvements, please open an issue or pull request.

## License ⚖️

This project is licensed under the BSD License—see the [LICENSE](./LICENSE.md) file for details.
