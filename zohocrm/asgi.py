# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zohocrm.settings')

# application = get_asgi_application()

# import os
# import django

# from channels.routing import get_default_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
# django.setup()
# application = get_default_application()


import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zohocrm.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            # routing.websocket_urlpatterns,
            chat.routing.websocket_urlpatterns,
        )
    ),
})

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": AuthMiddlewareStack(
#             RouteNotFoundMiddleware(
#                 URLRouter(chat.routing.websocket_urlpatterns)
#             )
#         )
#     }
# )