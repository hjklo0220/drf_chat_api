"""
ASGI config for drf_chat_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from chat import routing
from drf_chat_api.tokenauth_middleware import TokenAuthMiddlewate

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_chat_api.settings')

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": AllowedHostsOriginValidator(
		TokenAuthMiddlewate(URLRouter(routing.websocket_urlpatterns))
	)

})
