from django.db import models
from django.utils import timezone
from datetime import timedelta

class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อลูกค้า")
    phone = models.CharField(max_length=15, verbose_name="เบอร์โทร")
    line_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="Line ID")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

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

class Rental(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'จองแล้ว'),
        ('ACTIVE', 'กำลังเช่า'),
        ('RETURNED', 'คืนแล้ว'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="ลูกค้า")
    dress = models.ForeignKey(Dress, on_delete=models.CASCADE, verbose_name="ชุดที่เช่า")
    start_date = models.DateField(verbose_name="วันที่ยืม")
    end_date = models.DateField(verbose_name="วันที่คืน")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคารวมรอบนี้")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='BOOKED', verbose_name="สถานะ")
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