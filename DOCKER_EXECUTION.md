# Docker Execution Instructions

This document provides comprehensive instructions for running the Adobe Challenge 1B PDF Analysis Tool using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)
- PDF files to analyze

## Quick Start

### Method 1: Using Docker Compose (Recommended)

1. **Prepare your PDF files**:
   ```bash
   # Create input folder and place your PDF files
   mkdir -p input
   cp your-documents.pdf input/
   ```

2. **Build and run the container**:
   ```bash
   docker-compose up --build
   ```

3. **Check results**:
   ```bash
   # Results will be in the output folder
   ls output/
   ```

### Method 2: Using Docker Commands

1. **Build the Docker image**:
   ```bash
   docker build -t adobe1b-pdf-analyzer .
   ```

2. **Run the container**:
   ```bash
   docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer
   ```

### Method 3: Interactive Mode

For debugging or development:

```bash
# Run container in interactive mode
docker run -it -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer bash

# Inside the container, you can run:
python script.py
```

## File Structure

```
adobe_1b/
├── input/              # Place your PDF files here
│   ├── document1.pdf
│   └── document2.pdf
├── output/             # Results will appear here
│   └── challenge1b_output.json
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── script.py           # Main application
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Configuration

### Modifying Script Parameters

To change the persona, job description, or other parameters:

1. **Edit the script before building**:
   ```bash
   # Modify script.py with your desired parameters
   # Then rebuild the image
   docker-compose build
   ```

2. **Or mount the script as a volume**:
   ```bash
   docker run -v $(pwd)/script.py:/app/script.py -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer
   ```

### Environment Variables

You can set environment variables:

```bash
docker run -e PERSONA="Data Scientist" -e JOB="Analyze market trends" -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe1b-pdf-analyzer
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**:
   ```bash
   # On Linux/Mac, ensure proper permissions
   chmod -R 755 input output
   ```

2. **Container can't find PDF files**:
   ```bash
   # Verify files are in the input directory
   ls -la input/
   ```

3. **Model download issues**:
   ```bash
   # The model will download on first run
   # Ensure internet connection is available
   ```

4. **Memory issues**:
   ```bash
   # Increase Docker memory allocation
   # In Docker Desktop: Settings > Resources > Memory
   ```

### Debugging

1. **Check container logs**:
   ```bash
   docker-compose logs
   ```

2. **Run container interactively**:
   ```bash
   docker run -it adobe1b-pdf-analyzer bash
   ```

3. **Inspect container filesystem**:
   ```bash
   docker exec -it adobe1b-pdf-analyzer ls -la /app
   ```

## Performance Optimization

### Multi-stage Build (Advanced)

For production deployments, you can use a multi-stage build:

```dockerfile
# Build stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY script.py .
RUN mkdir -p input output
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "script.py"]
```

### Resource Limits

Set resource limits in docker-compose.yml:

```yaml
services:
  pdf-analyzer:
    build: .
    volumes:
      - ./input:/app/input
      - ./output:/app/output
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml adobe1b
```

### Using Kubernetes

Create a Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pdf-analyzer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pdf-analyzer
  template:
    metadata:
      labels:
        app: pdf-analyzer
    spec:
      containers:
      - name: pdf-analyzer
        image: adobe1b-pdf-analyzer:latest
        volumeMounts:
        - name: input-volume
          mountPath: /app/input
        - name: output-volume
          mountPath: /app/output
      volumes:
      - name: input-volume
        persistentVolumeClaim:
          claimName: input-pvc
      - name: output-volume
        persistentVolumeClaim:
          claimName: output-pvc
```

## Security Considerations

1. **Run as non-root user**:
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

2. **Scan for vulnerabilities**:
   ```bash
   docker scan adobe1b-pdf-analyzer
   ```

3. **Use specific base image tags**:
   ```dockerfile
   FROM python:3.9.18-slim
   ```

## Monitoring and Logging

### Health Check

Add to Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sentence_transformers; print('OK')" || exit 1
```

### Logging

```bash
# View logs
docker-compose logs -f

# Export logs
docker-compose logs > logs.txt
```

## Cleanup

```bash
# Remove containers
docker-compose down

# Remove images
docker rmi adobe1b-pdf-analyzer

# Clean up volumes (if any)
docker volume prune
``` 