from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Dress, Rental, Customer
from .forms import RentalForm, DressForm, CustomerForm

def dashboard(request):
    today = timezone.now().date()
    
    # 1. คิววันนี้และเร็วๆ นี้ (Calendar View แบบง่าย)
    # แบบที่ 2: เรียงตามวันที่ (งานด่วนอยู่บน) แต่ซ่อนคนคืนแล้ว
    upcoming_rentals = Rental.objects.exclude(status='RETURNED').order_by('start_date')

    # 2. คำนวณรายได้
    # รายได้สัปดาห์นี้
    start_week = today - timedelta(days=today.weekday())
    weekly_income = Rental.objects.filter(start_date__gte=start_week).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # รายได้เดือนนี้
    monthly_income = Rental.objects.filter(start_date__month=today.month).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # 3. กำไรของแต่ละชุด (Profit Per Item)
    dresses = Dress.objects.all()
    # Logic คำนวณกำไรอยู่ใน Model Dress.profit() แล้ว เราแค่ส่ง object ไป loop ใน html

    context = {
        'upcoming_rentals': upcoming_rentals,
        'weekly_income': weekly_income,
        'monthly_income': monthly_income,
        'dresses': dresses,
    }
    return render(request, 'dashboard.html', context)

def dress_list(request):
    dresses = Dress.objects.all()
    return render(request, 'dress_list.html', {'dresses': dresses})

def add_dress(request):
    if request.method == "POST":
        form = DressForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dress_list')
    else:
        form = DressForm()
    return render(request, 'form.html', {'form': form, 'title': 'เพิ่มชุดใหม่'})

def add_rental(request):
    if request.method == "POST":
        form = RentalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = RentalForm()
    return render(request, 'form.html', {'form': form, 'title': 'สร้างรายการเช่า'})

def customer_history(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    rentals = Rental.objects.filter(customer=customer).order_by('-start_date')
    return render(request, 'customer_history.html', {'customer': customer, 'rentals': rentals})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def update_rental_status(request, rental_id, status):
    # ฟังก์ชันสำหรับเปลี่ยนสถานะ (เช่น กดคืนชุด)
    rental = get_object_or_404(Rental, id=rental_id)
    if status in ['ACTIVE', 'RETURNED', 'BOOKED']:
        rental.status = status
        rental.save()
    return redirect('dashboard')
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list') # บันทึกเสร็จเด้งกลับมารายชื่อ
    else:
        form = CustomerForm()
    return render(request, 'form.html', {'form': form, 'title': 'เพิ่มลูกค้าใหม่'})

def edit_dress(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    if request.method == "POST":
        # instance=dress บอก Django ว่าเป็นการแก้ของเดิม ไม่ใช่สร้างใหม่
        form = DressForm(request.POST, request.FILES, instance=dress) 
        if form.is_valid():
            form.save()
            return redirect('dress_list')
    else:
        form = DressForm(instance=dress)
    return render(request, 'form.html', {'form': form, 'title': 'แก้ไขข้อมูลชุด'})

def delete_dress(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    dress.delete()
    return redirect('dress_list')

def delete_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.delete() # ลบข้อมูลทิ้งทันที
    
    # เช็คว่ากดลบมาจากหน้าไหน? (ถ้ามาจากหน้าลูกค้า ให้กลับไปหน้าลูกค้า)
    next_url = request.GET.get('next', 'dashboard')
    if next_url != 'dashboard':
        return redirect(next_url)
    
    return redirect('dashboard')