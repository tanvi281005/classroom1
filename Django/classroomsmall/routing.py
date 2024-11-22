# routing.py
from django.urls import path
from . import consumers
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from . import consumers  

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/assignments/", consumers.AssignmentConsumer.as_asgi()),
        ])
    ),
})
