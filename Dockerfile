FROM python:3.12

WORKDIR /app

# install firefox
RUN wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
RUN sh -c 'echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null'
RUN apt-get -y update
RUN apt-get install -y firefox xvfb libgtk2.0-0 libgconf-2-4

# set display port to avoid crash
ENV DISPLAY=:99

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "./app.py"]