import os
from sentry.runner import configure
configure()
from sentry.users.models.user import User
email = os.environ['ADMIN_EMAIL']
if not User.objects.filter(email=email).exists():
    user = User.objects.create_user(username=email, email=email, password=os.environ['ADMIN_PASSWORD'], is_superuser=True)
    user.is_staff = True
    user.save()
    print('Initial admin created', flush=True)
else:
    print('Admin exists; password preserved', flush=True)
