# 1. Base Image
FROM python:3.12-slim

# 2. Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Set Working Directory
WORKDIR /app

# 4. Install system dependencies (Optional but good for stability)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and INSTALL
# --no-cache-dir saves space, --upgrade ensures latest
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the code
COPY . .

# 7. Expose Port
EXPOSE 8000

# 8. Use the absolute path or python -m to call uvicorn
# This is the 'Swiss trick' to ensure the executable is found
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]