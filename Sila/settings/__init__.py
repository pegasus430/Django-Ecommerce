import socket
from .base import *


hostname = socket.gethostname()

if hostname in DOMAIN_PRODUCTION:
    from .production import *
elif hostname in DOMAIN_STAGING:
    from .staging import *
elif hostname in DOMAIN_DEVELOPMENT:
    from .dev import *
elif hostname.startswith(DOMAIN_FEATURE_START):
    from .feature import *
else:
    from .local import *