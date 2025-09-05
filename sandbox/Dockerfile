# Start with a base image that includes R and a Linux distribution
FROM rocker/rstudio:4.3.2

# Install Quarto CLI
RUN wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.7.33/quarto-1.7.33-linux-amd64.tar.gz -O quarto.tar.gz && \
    tar -xzf quarto.tar.gz -C /opt && \
    ln -sf /opt/quarto/bin/quarto /usr/local/bin/quarto && \
    rm quarto.tar.gz

# Install Python and essential packages
RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    git \
    libxml2-dev \
    libcurl4-openssl-dev

# Install R packages
RUN R -e "install.packages(c('ggplot2', 'dplyr', 'terra', 'ggspatial', 'sf', 'reticulate', 'leaflet', 'leafem', 'purrr', 'stringr', 'here'))"

# Set up a working directory
WORKDIR /app

# Copy the R and Python code into the container
# This copies your entire project folder into the container
COPY . /app

# Install Python packages using pip
RUN pip3 install -r requirements.txt

# Explicitly add the Quarto binary path to the system's PATH variable
ENV PATH="/opt/quarto/bin:${PATH}"

# Expose a port if you want to access RStudio IDE (optional)
EXPOSE 8787

# Command to run Quarto render on container startup (optional)
# This is a one-off command to render your document
CMD ["quarto", "render", "fire-severity-landsat.qmd"]