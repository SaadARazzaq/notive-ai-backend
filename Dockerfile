# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc musl-dev python3-dev libffi-dev openssl-dev cargo make \
    portaudio-dev alsa-lib alsa-utils alsa-plugins pulseaudio pulseaudio-alsa \
    curl wget

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install pip explicitly and upgrade it
RUN python -m ensurepip && pip install --no-cache-dir --upgrade pip

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir pyaudio && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose the application port
EXPOSE 8000

# Run the application using uv
CMD ["uv", "run", "src/voice_assistant/main.py"]
