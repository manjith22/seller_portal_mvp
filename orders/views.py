from io import BytesIO
import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import OrderForm, BulkUploadForm
from .models import Order, SellerProfile


EXPECTED_ALIASES = {
    'customer_name': ['name', 'customer name'],
    'full_address': ['full address', 'address'],
    'city': ['city'],
    'state': ['state'],
    'pincode': ['pincode', 'pin code'],
    'phone': ['phone', 'phone number', 'mobile', 'mobile number'],
    'product': ['product'],
    'amount': ['amount', 'price'],
    'tag': ['tag'],
    'payment_type': ['payment type', 'payment'],
    'status': ['status'],
    'order_date': ['date', 'order date'],
}


def get_seller_for_user(user):
    if user.is_staff:
        return None
    return SellerProfile.objects.filter(user=user, is_active=True).first()


@login_required
def dashboard(request):
    seller = get_seller_for_user(request.user)
    orders = Order.objects.all() if request.user.is_staff else Order.objects.filter(seller=seller)

    today = timezone.localdate()
    today_orders = orders.filter(order_date=today)
    totals = orders.aggregate(total_orders=Count('id'), total_amount=Sum('amount'))
    today_totals = today_orders.aggregate(today_orders=Count('id'), today_amount=Sum('amount'))
    by_status = orders.values('status').annotate(total=Count('id')).order_by('status')
    by_payment = orders.values('payment_type').annotate(total=Count('id')).order_by('payment_type')
    seller_totals = None
    if request.user.is_staff:
        seller_totals = orders.values('seller__display_name', 'seller__seller_code').annotate(
            total_orders=Count('id'), total_amount=Sum('amount')
        ).order_by('-total_orders')

    context = {
        'seller': seller,
        'totals': totals,
        'today_totals': today_totals,
        'by_status': by_status,
        'by_payment': by_payment,
        'seller_totals': seller_totals,
        'recent_orders': orders[:10],
    }
    return render(request, 'orders/dashboard.html', context)


@login_required
def order_list(request):
    seller = get_seller_for_user(request.user)
    orders = Order.objects.all() if request.user.is_staff else Order.objects.filter(seller=seller)

    seller_code = request.GET.get('seller')
    status = request.GET.get('status')
    payment = request.GET.get('payment')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if request.user.is_staff and seller_code:
        orders = orders.filter(seller__seller_code=seller_code)
    if status:
        orders = orders.filter(status=status)
    if payment:
        orders = orders.filter(payment_type=payment)
    if start_date:
        orders = orders.filter(order_date__gte=start_date)
    if end_date:
        orders = orders.filter(order_date__lte=end_date)

    sellers = SellerProfile.objects.filter(is_active=True).order_by('display_name') if request.user.is_staff else []
    return render(request, 'orders/order_list.html', {'orders': orders[:500], 'sellers': sellers})


@login_required
def create_order(request):
    seller = get_seller_for_user(request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_staff:
                selected_seller_id = request.POST.get('seller_id')
                if not selected_seller_id:
                    messages.error(request, 'Admin must choose a seller.')
                    return redirect('create_order')
                order.seller = SellerProfile.objects.get(id=selected_seller_id)
            else:
                order.seller = seller
            order.save()
            messages.success(request, f'Order {order.order_id} created successfully.')
            return redirect('order_list')
    else:
        form = OrderForm(initial={'order_date': timezone.localdate()})

    duplicate_phones = []
    phone = request.GET.get('phone')
    if phone:
        duplicate_phones = Order.objects.filter(phone__icontains=phone).order_by('-created_at')[:5]

    sellers = SellerProfile.objects.filter(is_active=True).order_by('display_name') if request.user.is_staff else []
    return render(request, 'orders/create_order.html', {
        'form': form,
        'sellers': sellers,
        'duplicate_phones': duplicate_phones,
    })


def normalize_columns(df):
    mapping = {}
    normalized = {c.strip().lower(): c for c in df.columns}
    for target, aliases in EXPECTED_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapping[normalized[alias]] = target
                break
    return df.rename(columns=mapping)


@login_required
def bulk_upload_orders(request):
    seller = get_seller_for_user(request.user)
    if request.method == 'POST':
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.cleaned_data['file']
            try:
                if upload.name.endswith('.csv'):
                    df = pd.read_csv(upload)
                else:
                    df = pd.read_excel(upload)
                df = normalize_columns(df)

                created = 0
                errors = []
                for index, row in df.fillna('').iterrows():
                    try:
                        row_seller = seller
                        if request.user.is_staff:
                            seller_code = str(row.get('seller_code', '')).strip()
                            if seller_code:
                                row_seller = SellerProfile.objects.filter(seller_code=seller_code).first()
                            if not row_seller:
                                errors.append(f'Row {index + 2}: seller missing or invalid')
                                continue
                        order = Order(
                            seller=row_seller,
                            customer_name=str(row.get('customer_name', '')).strip(),
                            full_address=str(row.get('full_address', '')).strip(),
                            city=str(row.get('city', '')).strip(),
                            state=str(row.get('state', '')).strip(),
                            pincode=str(row.get('pincode', '')).strip(),
                            phone=str(row.get('phone', '')).strip(),
                            product=str(row.get('product', '')).strip(),
                            amount=float(row.get('amount', 0) or 0),
                            tag=str(row.get('tag', '')).strip(),
                            payment_type=str(row.get('payment_type', 'COD')).strip().upper() or 'COD',
                            status=str(row.get('status', 'PENDING')).strip().upper() or 'PENDING',
                            order_date=pd.to_datetime(row.get('order_date', timezone.localdate())).date(),
                        )
                        if not order.customer_name or not order.phone:
                            errors.append(f'Row {index + 2}: name or phone missing')
                            continue
                        if order.payment_type not in {'COD', 'PREPAID'}:
                            order.payment_type = 'COD'
                        if order.status not in {'PENDING', 'SHIPPED', 'DELIVERED', 'RTO', 'CANCELLED'}:
                            order.status = 'PENDING'
                        order.save()
                        created += 1
                    except Exception as e:
                        errors.append(f'Row {index + 2}: {e}')

                if created:
                    messages.success(request, f'{created} orders uploaded successfully.')
                if errors:
                    messages.warning(request, 'Some rows failed: ' + ' | '.join(errors[:8]))
                return redirect('order_list')
            except Exception as e:
                messages.error(request, f'Upload failed: {e}')
    else:
        form = BulkUploadForm()

    return render(request, 'orders/bulk_upload.html', {'form': form})


@login_required
def export_orders_excel(request):
    seller = get_seller_for_user(request.user)
    orders = Order.objects.all() if request.user.is_staff else Order.objects.filter(seller=seller)

    rows = list(orders.values(
        'order_id', 'seller__display_name', 'seller__seller_code', 'customer_name', 'full_address',
        'city', 'state', 'pincode', 'phone', 'product', 'amount', 'tag',
        'payment_type', 'status', 'order_date', 'created_at'
    ))
    df = pd.DataFrame(rows)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')

    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=orders_export.xlsx'
    return response
