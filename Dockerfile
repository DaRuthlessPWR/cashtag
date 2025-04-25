FROM python:3.10-slim-bullseye

WORKDIR /app

# Preinstall required OS packages for Playwright with minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip gnupg libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libxss1 libasound2 libxshmfence1 libgbm1 libxcomposite1 \
    libxrandr2 libxi6 libxcursor1 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its browser dependencies
RUN pip install playwright && playwright install chromium

# Copy the application code
COPY ./app ./app
COPY start.sh .

EXPOSE 8000

CMD ["sh", "start.sh"]
