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
    rsa_decrypted_text, aes_decrypted_text, add_unread
)


# class ChatConsumer(AsyncJsonWebsocketConsumer):
#     async def connect(self):
#         if self.scope["user"].is_anonymous:
#             await self.close()
#         else:
#             await self.accept()
#         self.chats = set()

#     async def receive_json(self, content):
#         command = content.get("command", None)
#         try:
#             if command == "join":
#                 await self.join_chat(content["chat"])
#             elif command == "leave":
#                 await self.leave_chat(content["chat"])
#             elif command == "send":
#                 await self.send_chat(
#                     content["chat"], content["message"], 
#                     content['user'], content['type']
#                 )
#         except ClientError as e:
#             await self.send_json({"error": e.code})

#     async def disconnect(self, code):
#         for chat_id in list(self.chats):
#             try:
#                 await self.leave_chat(chat_id)
#             except ClientError:
#                 pass

#     ##### Command helper methods called by receive_json

#     async def join_chat(self, chat_id):
#         # The logged-in user is in our scope thanks to the authentication ASGI middleware
#         chat = await get_chat_or_error(chat_id, self.scope["user"])
#         public_key = await get_public_key(chat)
#         # Store that we're in the chat
#         self.chats.add(chat_id)
#         # Add them to the group so they get chat messages
#         await self.channel_layer.group_add(
#             chat.group_name,
#             self.channel_name,
#         )
#         # Instruct their client to finish opening the chat
#         await self.send_json({
#             "join": str(chat.id),
#             "key": str(public_key)
#         })

#     async def leave_chat(self, chat_id):
#         # The logged-in user is in our scope thanks to the authentication ASGI middleware
#         chat = await get_chat_or_error(chat_id, self.scope["user"])
#         # Remove that we're in the chat
#         self.chats.discard(chat_id)
#         # Remove them from the group so they no longer get chat messages
#         await self.channel_layer.group_discard(
#             chat.group_name,
#             self.channel_name,
#         )
#         # Instruct their client to finish closing the chat
#         await self.send_json({
#             "leave": str(chat.id),
#         })

#     async def send_chat(self, chat_id, encrypted_message, user, encryption_type):
#         if chat_id not in self.chats:
#             raise ClientError("chat_ACCESS_DENIED")

#         chat = await get_chat_or_error(chat_id, self.scope["user"])
#         print(encrypted_message, file=sys.stderr)

#         if encryption_type == 'rsa':
#             decrypted_message = await rsa_decrypted_text(chat, encrypted_message)
#         else:
#             decrypted_message = await aes_decrypted_text(encrypted_message)

#         print(decrypted_message, file=sys.stderr)
#         message = await create_message(chat.id, self.scope["user"], decrypted_message)
#         message = MessageSerializer(message).data
        
#         await self.channel_layer.group_send(
#             chat.group_name,
#             {
#                 "type": "chat.message",
#                 "chat_id": chat_id,
#                 "username": self.scope["user"].username,
#                 "message": message,
#             }
#         )

#     async def chat_join(self, event):
#         await self.send_json(
#             {
#                 "chat": event["chat_id"],
#                 "username": event["username"],
#             },
#         )

#     async def chat_leave(self, event):
#         await self.send_json(
#             {
#                 "chat": event["chat_id"],
#                 "username": event["username"],
#             },
#         )

#     async def chat_message(self, event):
#         await self.send_json(
#             {
#                 "chat": event["chat_id"],
#                 "username": event["username"],
#                 "message": event["message"],
#             },
#         )


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # print("""
        
        # === connect
        
        # """)
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
        print("""
        
        === custom disconnect
        
        """)
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # print("""
        
        # === receive
        
        # """)
        contents = json.loads(text_data)
        print("== contents ", contents)
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
        except ClientError as e:
            await self.send_json({"error": e.code})


    async def join_chat(self, chat_id, user):
        print("""
        
        === join_chat
        
        """)
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
        print("""
        
        === leave_chat
        
        """, chat_id, user)
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
        print("""
        
        === send_chat
        
        """)
        print("chat_id = ", chat_id)
        print("self.chats = ", self.chats)
        if chat_id not in self.chats:
            print("chat_ACCESS_DENIED")
            raise ClientError("chat_ACCESS_DENIED")
        
        chat = await get_chat_or_error(chat_id, user)
        # print(encrypted_message, file=sys.stderr)

        if encryption_type == 'rsa':
            decrypted_message = await rsa_decrypted_text(chat, encrypted_message)
        else:
            decrypted_message = await aes_decrypted_text(encrypted_message)

        # print(decrypted_message, file=sys.stderr)
        message = await create_message(chat.id, user, decrypted_message)
        MessageSerializerWS(message)
        # print(" == message = ", message.date_sent)
        # message = await database_sync_to_async(MessageSerializerWS(message).data, thread_sensitive=True)
        # message = MessageSerializerWS(message)
        # message = await message
        # # message = await MessageSerializer(message).data
        # print(message)

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
        # new_message["date_sent"] = str(message.date_sent)
        new_message["diff_time"] = message.diff_time
        new_message["text"] = message.text
        new_message["id"] = message.id
        new_message["sender"] = {"id": user}
       
        # new_message["id"] = message.chat.id
        print("group name = ", chat.group_name)
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

    async def chat_join(self, event):
        print("""
        
        === chat_join :: {}
        
        """.format(event["username"]))
        await self.send_json(
            {
                "chat": event["chat_id"],
                "username": event["username"],
            },
        )

    async def chat_leave(self, event):
        print("""
        
        === chat_leave
        
        """)
        await self.send_json(
            {
                "chat": event["chat_id"],
                "username": event["username"],
            },
        )

    async def chat_message(self, event):
        print("""
        
        === chat_message :: 
        
        """, event["username"], " : ", self.scope["user"])
        await self.send_json(
            {
                "chat": event["chat_id"],
                "username": event["username"],
                "message": event["message"],
                "receiver": event["receiver"],                
            },
        )


        # print("== receive", text_data)
        # """
        # Receive message from WebSocket.
        # Get the event and send the appropriate event
        # """
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']

        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

    # async def send_message(self, res):
    #     print("""
        
    #     === send message
        
    #     """)
    #     """ Receive message from room group """
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         "payload": res,
    #     }))

    # async def chat_message(self, event):
    #     message = event['message']

    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # self.room_name = self.scope['url_route']['kwargs']['room_name']
#         # self.room_group_name = 'chat_%s' % self.room_name
#         self.room_group_name = 'chat_room'

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))