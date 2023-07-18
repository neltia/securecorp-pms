FROM python:3.9
WORKDIR /app
COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# logging env set
RUN mkdir /app/securecorp_app/logs
RUN touch /app/logs/service_info.log

# apt dependencies
RUN apt-get update
# - pdf to img
RUN apt-get install -y libreoffice
RUN apt-get install -y poppler-utils
# - nanum font
RUN apt-get install fontconfig
RUN curl -o nanumfont.zip http://cdn.naver.com/naver/NanumFont/fontfiles/NanumFont_TTF_ALL.zip
RUN unzip -d /usr/share/fonts/nanum nanumfont.zip
RUN fc-cache -f -v

# requirements install
RUN pip install -r requirements.txt
