import base64
import json
import secrets

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from chat.models import Conversation, Message
from chat.serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):
	def connect(self):
		print("here")
		self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
		self.room_group_name = f"chat_{self.room_name}"

		"""
		그룹 룸 참여 (채널을 그룹에 등록하는 함수)
		해당 함수는 기본적으로 비동기로 작동하기 때문에
		 async_to_sync통해서 동기모드로 실행함
		"""
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		# Websocket 연결 accept
		self.accept()

	def disconnect(self, close_code):
		# 그룹 룸 나가기
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name, self.channel_name
		)

	# Websocket에서 메세지 받기
	def receive(self, text_data=None, bytes_data=None):
		# 딕셔너리 객체에서 json데이터 파싱
		text_data_json = json.loads(text_data)

		# 그룹 룸에 메세지 보내기
		chat_type = {"type": "chat_message"}
		return_dict = {**chat_type, **text_data_json}
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name,
			return_dict,
		)

	# 그룸 룸에서 메세지 받기
	def chat_message(self, event):
		text_data_json = event.copy()
		text_data_json.pop("type")
		message, attachment = (
			text_data_json["message"],
			text_data_json.get("attchment"),
		)

		conversation = Conversation.objects.get(id=int(self.room_name))
		sender = self.scope['user']

		# 파일 있다면
		if attachment:
			file_str, file_ext = attachment["data"], attachment["format"]

			file_data = ContentFile(
				base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
			)
			_message = Message.objects.create(
				sender=sender,
				attachment=file_data,
				text=message,
				conversation_id=conversation
			)
		else:
			_message = Message.objects.create(
				sender=sender,
				text=message,
				conversation_id=conversation
			)

		seriallizer = MessageSerializer(instance=_message)

		# Websocket에 메세지 보내기
		self.send(
			text_data=json.dumps(
				seriallizer.data
			)
		)
