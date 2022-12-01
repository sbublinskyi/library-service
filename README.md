# library-service

To start:
 - `pip install -r requirements.txt`
 - `python manage.py migrate`
 - `python manage.py runserver`

To run celery:
 - Docker must be installed `docker pull redis`
 - `celery -A library_service worker -l info`
 - `celery -A library_service beat -l INFO`

In the admin page you can create schedule of task


# Implemented apps:

books:
- implemented all CRUD

user:
- implemented create & retrieve views
- username were changed to email

borrowing:
- implemented list, create & retrieve views
- implemented custom action return_book
- implemented notifications into telegram if new borrowing is created
- implemented celery task, that checks if in db are outdated borrowings & send notification through telegram

payment:
- performed through Stripe
- uses for borrowings