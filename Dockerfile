ARG PORT=443
FROM cypress/browsers:latest

# Update first, then install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy requirements before installing dependencies
WORKDIR /app
COPY requirements.txt .

# Fix PATH environment variable
ENV PATH=/root/.local/bin:${PATH}

# Install Python packages
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT