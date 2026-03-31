from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_code', models.CharField(max_length=20, unique=True)),
                ('display_name', models.CharField(max_length=120)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=40, unique=True)),
                ('customer_name', models.CharField(max_length=150)),
                ('full_address', models.TextField()),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('pincode', models.CharField(blank=True, max_length=10)),
                ('phone', models.CharField(max_length=20)),
                ('product', models.CharField(max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tag', models.CharField(blank=True, max_length=120)),
                ('payment_type', models.CharField(choices=[('COD', 'COD'), ('PREPAID', 'Prepaid')], default='COD', max_length=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('SHIPPED', 'Shipped'), ('DELIVERED', 'Delivered'), ('RTO', 'RTO'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('order_date', models.DateField(default=django.utils.timezone.localdate)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.sellerprofile')),
            ],
            options={'ordering': ['-order_date', '-created_at']},
        ),
    ]
