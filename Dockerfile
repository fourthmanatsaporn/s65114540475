# ใช้ Python 3.10 เป็น base image
FROM python:3.10

# ตั้งค่าตัวแปร ENV ให้ Python ทำงานได้เต็มที่
ENV PYTHONUNBUFFERED 1

# ตั้งค่าโฟลเดอร์ทำงานใน Container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt ไปใน Container
COPY requirements.txt /app/

# ติดตั้ง Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์ทั้งหมดของโปรเจคไปใน Container
COPY . /app/

# รันคำสั่ง Migrations (ถ้าใช้ SQLite อาจต้องแก้ไข)
RUN python manage.py collectstatic --noinput

# ใช้ Gunicorn ในการรัน Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
