FROM python:3.10
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# source
COPY . /app/

# static/media folders
RUN mkdir -p /app/static /app/media /app/staticfiles

# defaults for Postgres
ENV DB_HOST=postgres
ENV DB_PORT=5432

# wait-for-DB (generic)
RUN printf '%s\n' \
  'import os, socket, time' \
  'h=os.getenv("DB_HOST","postgres")' \
  'p=int(os.getenv("DB_PORT","5432"))' \
  'print(f"Waiting for PostgreSQL at {h}:{p} ...")' \
  'while True:' \
  '    try:' \
  '        s=socket.create_connection((h,p),2); s.close(); break' \
  '    except Exception:' \
  '        time.sleep(2)' \
  'print("DB is up.")' \
  > /app/wait_for_db.py

# entry command: wait → migrate → collectstatic → gunicorn
CMD sh -c "python /app/wait_for_db.py \
  && python manage.py migrate --noinput \
  && if [ \"$INIT_SUPERUSER\" = \"True\" ]; then python manage.py createsuperuser --noinput || true; fi \
  && python manage.py collectstatic --noinput \
  && gunicorn --bind 0.0.0.0:8000 myproject.wsgi:application"
