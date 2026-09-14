# Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg chromium chromium-driver default-jre \
    libnss3 libxss1 libasound2 fonts-liberation libgbm1 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Симлинки для Chrome (без chromedriver, он уже в /usr/bin)
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome \
    && ln -sf /usr/bin/chromium /usr/bin/google-chrome-stable

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

RUN wget https://github.com/allure-framework/allure2/releases/download/2.32.0/allure-2.32.0.zip \
    && unzip allure-2.32.0.zip -d /opt/ \
    && ln -s /opt/allure-2.32.0/bin/allure /usr/local/bin/allure \
    && rm allure-2.32.0.zip

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

CMD ["pytest", "tests/test_release_types.py", "-v", "--headless", "--alluredir=allure-results", "--capture=no"]