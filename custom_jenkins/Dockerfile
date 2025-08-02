# Use the Jenkins image as the base image
FROM jenkins/jenkins:lts

# Switch to root user to install dependencies
USER root

# --- FIX: Configure Docker Daemon with a reliable DNS ---
# Create the Docker daemon configuration file to prevent DNS errors inside the container
RUN mkdir -p /etc/docker && \
    echo '{"dns": ["8.8.8.8", "8.8.4.4"]}' > /etc/docker/daemon.json

# --- ADDED: Install all dependencies in a single RUN command for efficiency ---
# Install Python, Docker prerequisites, Docker, and Google Cloud SDK
RUN apt-get update -y && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common python3 python3-pip python3-venv && \
    # Install Docker
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    echo "deb [arch=amd64] https://download.docker.com/linux/debian bullseye stable" > /etc/apt/sources.list.d/docker.list && \
    # Install Google Cloud SDK
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    # Update package list again and install all tools
    apt-get update -y && \
    apt-get install -y docker-ce docker-ce-cli containerd.io google-cloud-sdk kubectl google-cloud-sdk-gke-gcloud-auth-plugin && \
    # --- ADDED: Create symbolic link for python -> python3 ---
    ln -s /usr/bin/python3 /usr/bin/python && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- ADDED: Give Docker permissions to the Jenkins user ---
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# Create the Docker directory and volume for DinD
RUN mkdir -p /var/lib/docker
VOLUME /var/lib/docker

# Switch back to the Jenkins user
USER jenkins
