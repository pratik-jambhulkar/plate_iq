Plate IQ Invoice APIs

- Uses SQLite DB
- Before starting the app apply migrations with command
python manage.py migrate

- Load default migrations for users, companies, invoices and invoice items with command:
python manage.py loaddata users companies invoices invoice_items

- Start the server with command:
python manage.py runserver

- Swagger supported for basic user and company creation on following URL:
localhost:8000/#/
