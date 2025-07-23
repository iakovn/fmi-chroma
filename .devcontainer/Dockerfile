# Install uv
FROM openmodelica/openmodelica:v1.25.1-ompython
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Switch to root to install system packages
USER root

# Install prerequisites, now including git and bash-completion
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    bzip2 \
    ca-certificates \
    git \
    bash-completion \
    sudo \
    wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Configure Conda environment variables
ENV CONDA_DIR=/opt/conda
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV PATH="${CONDA_DIR}/bin:${PATH}"

# Create a non-root user and set up permissions
RUN useradd -ms /bin/bash -u 1000 vscode && \
    mkdir -p "${CONDA_DIR}" && \
    mkdir -p /workspaces/fmi-chroma/ && \
    chown -R vscode:vscode "${CONDA_DIR}" /workspaces && \
    # Add micromamba shell hook to the user's bashrc for interactive sessions
    echo 'eval "$(micromamba shell hook -s bash)"' >> /home/vscode/.bashrc


USER vscode
WORKDIR  /workspaces/fmi-chroma/
