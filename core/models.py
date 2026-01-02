from django.db import models
from django.utils import timezone
from PIL import Image, ExifTags # เพิ่มตัวจัดการรูปภาพ
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import timedelta
import os

class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อลูกค้า")
    phone = models.CharField(max_length=15, verbose_name="เบอร์โทร")
    line_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Line ID")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Dress(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อชุด")
    image = models.ImageField(upload_to='dresses/', verbose_name="รูปภาพสินค้า")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ต้นทุนชุด (บาท)")
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาเช่าต่อครั้ง (บาท)")
    is_available = models.BooleanField(default=True, verbose_name="สถานะพร้อมเช่า")

    def __str__(self):
        return self.name
    
    def total_revenue(self):
        # คำนวณรายได้รวมของชุดนี้
        rentals = self.rental_set.all()
        return sum(r.total_price for r in rentals)

    def profit(self):
        # กำไร = รายได้รวม - ต้นทุน
        return self.total_revenue() - self.cost_price
    
    def save(self, *args, **kwargs):
        # 1. เช็คว่ามีรูปไหม
        if self.image:
            try:
                # เปิดรูปขึ้นมา
                img = Image.open(self.image)
                
                # 🔧 แก้ปัญหาหมุนภาพ (ถ้าถ่ายจากมือถือบางทีภาพจะตะแคง)
                if hasattr(img, '_getexif') and img._getexif():
                    exif = dict(img._getexif().items())
                    # รหัส 274 คือ Orientation
                    if 274 in exif:
                        if exif[274] == 3: img = img.rotate(180, expand=True)
                        elif exif[274] == 6: img = img.rotate(270, expand=True)
                        elif exif[274] == 8: img = img.rotate(90, expand=True)

                # 2. แปลงเป็น RGB (เผื่อเจอไฟล์ PNG จะได้ไม่ error)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 3. กำหนดขนาดสูงสุด (เช่น กว้างไม่เกิน 800px)
                max_size = (800, 800) 
                
                # ถ้ารูปใหญ่กว่ากำหนด ให้ย่อลง
                if img.height > 800 or img.width > 800:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # เตรียมเซฟทับ
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=85) # Quality 85 ชัดแต่ไฟล์เล็ก
                    output.seek(0)

                    # เปลี่ยนชื่อไฟล์ใน Memory ให้เป็นค่าใหม่
                    self.image = ContentFile(output.read(), name=os.path.basename(self.image.name))

            except Exception as e:
                print(f"Error resizing image: {e}")
                # ถ้า error ก็เซฟแบบเดิมไป ไม่ต้องย่อ

        # บันทึกลง Database
        super().save(*args, **kwargs)
    

class Accessory(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อเครื่องประดับ")
    image = models.ImageField(upload_to='accessories/', verbose_name="รูปภาพ", blank=True, null=True) # ✅ ต้องมีรูป
    

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 1. เช็คว่ามีรูปไหม
        if self.image:
            try:
                # เปิดรูปขึ้นมา
                img = Image.open(self.image)
                
                # 🔧 แก้ปัญหาหมุนภาพ (ถ้าถ่ายจากมือถือบางทีภาพจะตะแคง)
                if hasattr(img, '_getexif') and img._getexif():
                    exif = dict(img._getexif().items())
                    # รหัส 274 คือ Orientation
                    if 274 in exif:
                        if exif[274] == 3: img = img.rotate(180, expand=True)
                        elif exif[274] == 6: img = img.rotate(270, expand=True)
                        elif exif[274] == 8: img = img.rotate(90, expand=True)

                # 2. แปลงเป็น RGB (เผื่อเจอไฟล์ PNG จะได้ไม่ error)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 3. กำหนดขนาดสูงสุด (เช่น กว้างไม่เกิน 800px)
                max_size = (800, 800) 
                
                # ถ้ารูปใหญ่กว่ากำหนด ให้ย่อลง
                if img.height > 800 or img.width > 800:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # เตรียมเซฟทับ
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=85) # Quality 85 ชัดแต่ไฟล์เล็ก
                    output.seek(0)

                    # เปลี่ยนชื่อไฟล์ใน Memory ให้เป็นค่าใหม่
                    self.image = ContentFile(output.read(), name=os.path.basename(self.image.name))

            except Exception as e:
                print(f"Error resizing image: {e}")
                # ถ้า error ก็เซฟแบบเดิมไป ไม่ต้องย่อ

        # บันทึกลง Database
        super().save(*args, **kwargs)
    

class Rental(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'จองแล้ว'),
        ('ACTIVE', 'กำลังเช่า'),
        ('RETURNED', 'คืนแล้ว'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="ลูกค้า")
    # ✅ เชื่อมโยงแบบเลือกได้หลายชิ้น (Many-to-Many)
    accessories = models.ManyToManyField(Accessory, blank=True, verbose_name="เครื่องประดับที่แถม")
    dress = models.ForeignKey(Dress, on_delete=models.CASCADE, verbose_name="ชุดที่เช่า")
    start_date = models.DateField(verbose_name="วันที่ยืม")
    end_date = models.DateField(verbose_name="วันที่คืน")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคารวมรอบนี้")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BOOKED', verbose_name="สถานะ")
    # ✅ เพิ่ม 2 บรรทัดนี้ครับ
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาพิเศษ (ถ้ามี)")
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, verbose_name="ค่ามัดจำ")
    note = models.TextField(blank=True, null=True, verbose_name="หมายเหตุ")

    def save(self, *args, **kwargs):
        # ถ้าไม่ได้กรอกราคารวม ให้คำนวณอัตโนมัติ (วัน * ราคาต่อชุด)
        if not self.total_price:
            days = (self.end_date - self.start_date).days
            if days <= 0: days = 1
            self.total_price = self.dress.rental_price # หรือ * days ถ้าคิดเป็นวัน
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.dress.name}"
    

