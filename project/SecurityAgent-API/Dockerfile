# Step 1: Use a lightweight Python base image
FROM python:3.12-slim

# Step 2: Set environment variables to optimize Python inside the container
# Prevents Python from writing .pyc files and ensures logs are sent to terminal directly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Install system dependencies (if needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Step 6: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 7: Copy the rest of the application code
COPY . .

# Step 8: Expose the port FastAPI runs on
EXPOSE 8000

# Step 9: Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]