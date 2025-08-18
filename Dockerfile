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

# ค่าดีฟอลต์สำหรับสคริปต์รอ DB (ถ้ามีใน .env จะทับค่าเหล่านี้)
ENV DB_HOST=mysql
ENV DB_PORT=3306

# รอ MySQL -> migrate -> collectstatic -> runserver
CMD sh -c "\
python - <<'PY'\n\
import os, socket, time\n\
h=os.getenv('DB_HOST','mysql'); p=int(os.getenv('DB_PORT','3306'))\n\
print(f'Waiting for MySQL at {h}:{p} ...')\n\
while True:\n\
    try:\n\
        s=socket.create_connection((h,p), timeout=2); s.close(); break\n\
    except Exception:\n\
        time.sleep(2)\n\
print('MySQL is up.')\n\
PY\n\
 && python manage.py migrate --noinput \
 && python manage.py collectstatic --noinput \
 && python manage.py runserver 0.0.0.0:8000"
