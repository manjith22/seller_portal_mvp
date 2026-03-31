# Seller Portal MVP

A Django-based seller portal where sellers can log in, add daily orders, upload orders in bulk, and admins can analyze all orders later.

## Features
- Seller login and dashboard
- Manual order entry
- Bulk CSV/Excel upload
- Auto order ID generation
- Admin analytics dashboard
- Filters by seller, date, status, payment type
- Excel export
- Duplicate phone warning on form

## Default roles
- `is_staff=True` users are admins
- non-staff users are sellers

## Quick start
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Recommended setup
Create one Django user account per seller. Then create one `SellerProfile` row in Django admin linked to that user.

## Bulk upload columns
Accepted columns (case-insensitive where possible):
- Name
- Full Address / Address
- City
- State
- Pincode
- Phone / Phone Number
- Product
- Amount
- Tag
- Payment Type
- Status
- Date

## Notes
- SQLite is used by default for quick setup.
- You can later move to PostgreSQL.
- This MVP is intentionally simple so you can extend it quickly.
