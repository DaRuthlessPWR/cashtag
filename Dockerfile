FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 libpango-1.0-0 libcairo2

# Install playwright deps
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps

# Copy project
COPY . /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
