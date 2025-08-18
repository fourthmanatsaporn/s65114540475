# FROM python:3.10
# ENV PYTHONUNBUFFERED=1
# WORKDIR /app

# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . /app/

# # รัน migrate + collectstatic แล้วสตาร์ตเซิร์ฟเวอร์อัตโนมัติ
# CMD sh -c "python manage.py migrate \
#   && python manage.py collectstatic --noinput \
#   && python manage.py runserver 0.0.0.0:8000"
# # ถ้าต้องการ production ค่อยเปลี่ยนเป็น gunicorn
# # CMD ["gunicorn","--bind","0.0.0.0:8000","myproject.wsgi:application"]

FROM python:3.10
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# source
COPY . /app/

# กัน warning ถ้าไม่มีโฟลเดอร์
RUN mkdir -p /app/static /app/media /app/staticfiles

# ดีฟอลต์ (จะถูก override ได้จาก .env)
ENV DB_HOST=mysql
ENV DB_PORT=3306

# สร้างสคริปต์รอ MySQL ตอน build (เลี่ยงปัญหา quoting)
RUN printf '%s\n' \
  'import os, socket, time' \
  'h=os.getenv("DB_HOST","mysql")' \
  'p=int(os.getenv("DB_PORT","3306"))' \
  'print(f"Waiting for MySQL at {h}:{p} ...")' \
  'while True:' \
  '    try:' \
  '        s=socket.create_connection((h,p),2); s.close(); break' \
  '    except Exception:' \
  '        time.sleep(2)' \
  'print("MySQL is up.")' \
  > /app/wait_for_db.py

# รอ DB -> migrate -> collectstatic -> runserver
CMD sh -c "python /app/wait_for_db.py \
  && python manage.py migrate --noinput \
  && python manage.py collectstatic --noinput \
  && python manage.py runserver 0.0.0.0:8000"
