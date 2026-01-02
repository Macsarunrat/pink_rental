from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Dress, Rental, Customer, Accessory
from .forms import AccessoryForm, RentalForm, DressForm, CustomerForm
from django.contrib.auth.decorators import login_required

@login_required
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

@login_required
def dress_list(request):
    dresses = Dress.objects.all()
    return render(request, 'dress_list.html', {'dresses': dresses})

@login_required
def add_dress(request):
    if request.method == "POST":
        form = DressForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dress_list')
    else:
        form = DressForm()
    return render(request, 'form.html', {'form': form, 'title': 'เพิ่มชุดใหม่'})

@login_required
# core/views.py

@login_required
def add_rental(request):
    if request.method == "POST":
        form = RentalForm(request.POST)
        if form.is_valid():
            # ดึงข้อมูลที่กรอกมาพักไว้ก่อน (ยังไม่ Save ลงฐานข้อมูลจริง)
            # แต่เราจะดึงค่าจาก cleaned_data มาเช็ค
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            selected_accessories = form.cleaned_data.get('accessories')

            # --- 🔥 เริ่ม LOGIC ตรวจกันชน ---
            
            # 1. หาใบจองอื่นที่ "วันที่ทับซ้อน" กับเรา
            overlapping_rentals = Rental.objects.filter(
                start_date__lte=end_date,   # เริ่มก่อนที่เราจะคืน
                end_date__gte=start_date    # คืนหลังที่เราเริ่ม
            ).exclude(status='RETURNED')    # ไม่นับคนที่คืนของแล้ว

            # 2. วนลูปเช็คว่า "ของที่เราเลือก" ไปชนกับ "ของในใบจองพวกนั้น" ไหม?
            collision_msg = None
            
            for rental in overlapping_rentals:
                # หาของที่ซ้ำกัน (Intersection)
                # แปลงเป็น set เพื่อเทียบหาตัวซ้ำได้ง่ายๆ
                booked_items = set(rental.accessories.all())
                selected_items = set(selected_accessories)
                
                duplicates = booked_items.intersection(selected_items)
                
                if duplicates:
                    # เจอตัวซ้ำ! เตรียมข้อความด่า (เอ้ย เตือน)
                    dup_names = ", ".join([acc.name for acc in duplicates])
                    collision_msg = f"บันทึกไม่ได้! '{dup_names}' ถูกจองโดยคุณ {rental.customer.name} แล้ว (วันที่ {rental.start_date.strftime('%d/%m')} - {rental.end_date.strftime('%d/%m')})"
                    break # เจอที่เดียวก็พอแล้ว หยุดเช็ค
            
            # --- 🔥 จบ LOGIC ---

            if collision_msg:
                # ถ้ามีรถชนกัน -> เพิ่ม Error ใส่ฟอร์ม แล้วเด้งกลับไปหน้าเดิม
                form.add_error('accessories', collision_msg)
            else:
                # ทางสะดวก -> บันทึกได้เลย!
                form.save()
                return redirect('dashboard')

    else:
        form = RentalForm()
    
    accessories = Accessory.objects.all()

    return render(request, 'form_rental.html', {
        'form': form,
        'accessories': accessories
    })

@login_required
def customer_history(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    rentals = Rental.objects.filter(customer=customer).order_by('-start_date')
    return render(request, 'customer_history.html', {'customer': customer, 'rentals': rentals})

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

@login_required
def update_rental_status(request, rental_id, status):
    # ฟังก์ชันสำหรับเปลี่ยนสถานะ (เช่น กดคืนชุด)
    rental = get_object_or_404(Rental, id=rental_id)
    if status in ['ACTIVE', 'RETURNED', 'BOOKED']:
        rental.status = status
        rental.save()
    return redirect('dashboard')

@login_required
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list') # บันทึกเสร็จเด้งกลับมารายชื่อ
    else:
        form = CustomerForm()
    return render(request, 'form.html', {'form': form, 'title': 'เพิ่มลูกค้าใหม่'})

@login_required
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

@login_required
def delete_dress(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    dress.delete()
    return redirect('dress_list')

@login_required
def delete_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    rental.delete() # ลบข้อมูลทิ้งทันที
    
    # เช็คว่ากดลบมาจากหน้าไหน? (ถ้ามาจากหน้าลูกค้า ให้กลับไปหน้าลูกค้า)
    next_url = request.GET.get('next', 'dashboard')
    if next_url != 'dashboard':
        return redirect(next_url)
    
    return redirect('dashboard')


# 1. เพิ่มฟังก์ชัน Landing Page (ไว้ล่างสุดก็ได้ หรือบนสุดก็ได้)
def landing_page(request):
    # ถ้าเป็นลูกค้า (มี session) ให้เด้งไปหน้า Portal เลย
    if 'customer_id' in request.session:
        return redirect('customer_portal')
        
    # ถ้าเป็น Admin (login ระบบ Django) ให้เด้งไป Dashboard เลย
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    latest_dresses = Dress.objects.filter(image__isnull=False).order_by('-id')[:5]

    return render(request, 'landing_page.html', {
        'latest_dresses': latest_dresses # ส่งไปหน้าเว็บ
    })


@login_required
def accessory_list(request):
    accessories = Accessory.objects.all()
    return render(request, 'accessory_list.html', {'accessories': accessories})

@login_required
def add_accessory(request):
    if request.method == 'POST':
        form = AccessoryForm(request.POST, request.FILES) # อย่าลืม request.FILES เพราะมีรูป
        if form.is_valid():
            form.save()
            return redirect('accessory_list')
    else:
        form = AccessoryForm()
    return render(request, 'form.html', {'form': form, 'title': 'เพิ่มเครื่องประดับใหม่'})

@login_required
def delete_accessory(request, acc_id):
    acc = get_object_or_404(Accessory, id=acc_id)
    acc.delete()
    return redirect('accessory_list')

# core/views.py

# 1. ล็อคอินลูกค้า (ใช้เบอร์โทร)
def customer_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        try:
            # ค้นหาลูกค้าจากเบอร์โทร
            customer = Customer.objects.get(phone=phone)
            # เจอ! เก็บ ID ลง Session (เหมือนการจำว่า login แล้ว)
            request.session['customer_id'] = customer.id
            return redirect('customer_portal')
        except Customer.DoesNotExist:
            return render(request, 'customer_login.html', {'error': 'ไม่พบเบอร์โทรนี้ในระบบค่ะ'})
            
    return render(request, 'customer_login.html')

# 2. หน้าหลักลูกค้า (โชว์รายการเช่าของตัวเอง)
def customer_portal(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login') # ถ้ายังไม่ login ดีดกลับไป
    
    customer = Customer.objects.get(id=customer_id)
    # ดึงเฉพาะรายการที่ จองอยู่ (BOOKED) หรือ รับชุดไปแล้ว (ACTIVE)
    my_rentals = Rental.objects.filter(customer=customer, status__in=['BOOKED', 'ACTIVE']).order_by('-start_date')
    
    return render(request, 'customer_portal.html', {'customer': customer, 'rentals': my_rentals})

# core/views.py

def customer_select_accessories(request, rental_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')
    
    current_rental = get_object_or_404(Rental, id=rental_id)
    
    if current_rental.customer.id != customer_id:
        return redirect('customer_portal')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('accessories')
        if len(selected_ids) > 2:
            pass # (จัดการ error ตามเดิม)
        else:
            current_rental.accessories.set(selected_ids)
            return redirect('customer_portal')

    # ---------------------------------------------------------
    # 🔥 LOGIC ป้องกันการจองชนกัน (เพิ่มตรงนี้ครับ)
    # ---------------------------------------------------------
    
    # 1. หาใบจองอื่น ที่วัน "คาบเกี่ยว" กับใบจองนี้
    # สูตร: (StartA <= EndB) และ (EndA >= StartB)
    overlapping_rentals = Rental.objects.filter(
        start_date__lte=current_rental.end_date, # เริ่มก่อนที่เราจะคืน
        end_date__gte=current_rental.start_date  # คืนหลังจากที่เราเริ่ม
    ).exclude(id=current_rental.id).exclude(status='RETURNED') 
    # exclude id: ไม่นับตัวเอง (เผื่อเราเคยเลือกไว้แล้ว จะได้แก้ได้)
    # exclude RETURNED: ถ้าคืนแล้ว ถือว่าว่าง จองต่อได้

    # 2. เก็บ ID ของเครื่องประดับที่ "ไม่ว่าง" ใส่ลิสต์ไว้
    booked_acc_ids = []
    for r in overlapping_rentals:
        for acc in r.accessories.all():
            booked_acc_ids.append(acc.id)

    accessories = Accessory.objects.all()
    
    return render(request, 'customer_select_accessories.html', {
        'rental': current_rental, 
        'accessories': accessories,
        'booked_acc_ids': booked_acc_ids # ✅ ส่งบัญชีดำไปหน้าเว็บ
    })

# 4. ออกจากระบบลูกค้า
def customer_logout(request):
    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('landing_page')


# core/views.py

@login_required
def edit_customer(request, customer_id):
    # ดึงข้อมูลลูกค้าคนเก่าออกมา
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == "POST":
        # รับค่าใหม่มาทับของเดิม (instance=customer)
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list') # แก้เสร็จกลับไปหน้ารายชื่อ
    else:
        # เปิดฟอร์มพร้อมข้อมูลเดิม
        form = CustomerForm(instance=customer)
    
    # ใช้ form.html ตัวเดิมได้เลย ประหยัดเวลา
    return render(request, 'form.html', {'form': form, 'title': 'แก้ไขข้อมูลลูกค้า'})

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('customer_list')