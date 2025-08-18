FROM python:3.10
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# รัน migrate + collectstatic แล้วสตาร์ตเซิร์ฟเวอร์อัตโนมัติ
CMD sh -c "python manage.py migrate \
  && python manage.py collectstatic --noinput \
  && python manage.py runserver 0.0.0.0:8000"
# ถ้าต้องการ production ค่อยเปลี่ยนเป็น gunicorn
# CMD ["gunicorn","--bind","0.0.0.0:8000","myproject.wsgi:application"]
