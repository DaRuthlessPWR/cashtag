FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libxss1 libasound2 libxshmfence1 libgbm1 libxcomposite1 \
    libxrandr2 libxi6 libxcursor1 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and required browsers
RUN playwright install --with-deps

# Copy app source code
COPY ./app ./app
COPY start.sh .

EXPOSE 8000

CMD ["sh", "start.sh"]
