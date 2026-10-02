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

# Reuse the pinned UI validation instead of asking for already-preset options.
import sentry
from sentry import options
from sentry.web.client_config import _needs_upgrade
options.set("sentry:version-configured", sentry.get_version())
if _needs_upgrade():
    raise RuntimeError("Required installation options missing; bootstrap aborted")
print("Installation configuration complete", flush=True)
