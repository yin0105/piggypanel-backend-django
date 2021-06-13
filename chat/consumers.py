import sys

from django.conf import settings

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from asgiref.sync import sync_to_async

from .exceptions import ClientError
from .serializers import MessageSerializer, MessageSerializerWS

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from datetime import date, datetime
import pytz
from .models import Chat


from .utils import (
    get_chat_or_error, create_message, get_public_key,
    rsa_decrypted_text, aes_decrypted_text, add_unread, set_user_status,
)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chatting_room'
        self.chats = set()
        self.receivers = ""

        # Join room group
        await self.channel_layer.group_add(
            'chatting_room',
            self.channel_name
        )   
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        contents = json.loads(text_data)
        command = contents.get("command", None)
        try:
            if command == "prejoin":
                await self.prejoin_chat(contents["group"], contents["user"])

            elif command == "join":
                await self.join_chat(contents["chat"], contents["user"])

            elif command == "leave":
                await self.leave_chat(contents["chat"], contents["user"])

            elif command == "send":
                await add_unread(contents["chat"], contents["user"])
                await self.send_chat(
                    contents["chat"], contents["message"], 
                    contents['user'], contents['type']
                )

            elif command == "client_status":
                await self.set_client_status(contents["user"], contents["status"])

        except ClientError as e:
            await self.send_json({"error": e.code})


    async def join_chat(self, chat_id, user):
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        chat = await get_chat_or_error(chat_id, user)
        public_key = await get_public_key(chat)
        # Store that we're in the chat
        self.chats.add(chat_id)        
        # Add them to the group so they get chat messages
        await self.channel_layer.group_add(
            'chatting_room',
            # chat.group_name,
            # self.room_group_name,
            self.channel_name,
        )
        # Instruct their client to finish opening the chat
        await self.send_json({
            "join": str(chat.id),
            "key": str(public_key)
        })

    async def leave_chat(self, chat_id, user):
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        chat = await get_chat_or_error(chat_id, user)
        # Remove that we're in the chat
        self.chats.discard(chat_id)
        # Remove them from the group so they no longer get chat messages
        await self.channel_layer.group_discard(
            chat.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the chat
        await self.send_json({
            "leave": str(chat.id),
        })

    async def send_chat(self, chat_id, encrypted_message, user, encryption_type):
        if chat_id not in self.chats:
            raise ClientError("chat_ACCESS_DENIED")
        
        chat = await get_chat_or_error(chat_id, user)

        if encryption_type == 'rsa':
            decrypted_message = await rsa_decrypted_text(chat, encrypted_message)
        else:
            decrypted_message = await aes_decrypted_text(encrypted_message)

        message = await create_message(chat.id, user, decrypted_message)
        MessageSerializerWS(message)

        if message.date_sent != None:
            diff = (datetime.utcnow().replace(tzinfo=pytz.UTC) - message.date_sent).total_seconds()
            if diff < 1:
                message.diff_time = "just now"
            elif diff < 60:
                message.diff_time = "{} seconds ago".format(int(diff))
            elif diff < 3600:
                message.diff_time = "{} minutes ago".format(int(diff // 60))
            elif diff < 86400:
                message.diff_time = "{} hours ago".format(int(diff // 3600))
            elif diff < 86400 * 30:
                message.diff_time = "{} days ago".format(int(diff // 86400))
            elif diff < 86400 * 365:
                message.diff_time = "{} months ago".format(int(diff // (86400 * 30)))
            else:
                message.diff_time = "{} years ago".format(int(diff // (86400 * 365)))
        
        new_message = {}
        new_message["date_sent"] = str(message.date_sent)
        new_message["diff_time"] = message.diff_time
        new_message["text"] = message.text
        new_message["id"] = message.id
        new_message["sender"] = {"id": user}
       
        # new_message["id"] = message.chat.id
        self.receivers = chat.receivers
        await self.channel_layer.group_send(
            "chatting_room",
            {
                "type": "chat.message",
                "chat_id": chat_id,
                "username": self.scope["user"].username,
                "message": new_message,
                "receiver": self.receivers,
            }
        )

    async def set_client_status(self, user, status):
        await set_user_status(user, status)
        await self.channel_layer.group_send(
            "chatting_room",
            {
                "type": "chat.status",
                "user": user,
                "user_status": status,
            }
        )



    async def chat_join(self, event):
        await self.send_json(
            {
                "chat": event["chat_id"],
                "username": event["username"],
            },
        )

    async def chat_leave(self, event):
        await self.send_json(
            {
                "chat": event["chat_id"],
                "username": event["username"],
            },
        )

    async def chat_message(self, event):
        await self.send_json(
            {
                "chat": event["chat_id"],
                "username": event["username"],
                "message": event["message"],
                "receiver": event["receiver"],                
            },
        )

    async def chat_status(self, event):
        await self.send_json(
            {
                "user": event["user"],
                "user_status": event["user_status"],
            },
        )
        