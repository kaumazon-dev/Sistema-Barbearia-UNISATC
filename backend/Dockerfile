FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser \
 && chmod +x entrypoint.sh \
 && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
# O Render (e outros PaaS) informa a porta na variavel PORT; local cai no 5000.
# Forma shell para o ${PORT} ser expandido; o exec deixa o gunicorn como PID 1.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --access-logfile - wsgi:app"]
