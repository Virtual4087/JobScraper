ARG PORT=443
FROM cypress/browsers:latest

# Update first, then install Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Create and activate a virtual environment
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements before installing dependencies
WORKDIR /app
COPY requirements.txt .

# Install Python packages (in the virtual environment)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port $PORT