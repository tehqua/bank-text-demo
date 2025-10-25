from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import threading
import queue
import uuid
from src.utils.logger import default_logger as logger

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"

class MessagePriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.EVENT
    priority: MessagePriority = MessagePriority.MEDIUM
    sender: str = ""
    recipient: Optional[str] = None
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None

class MessageBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.subscribers: Dict[str, List[Callable]] = {}
            self.message_queue = queue.PriorityQueue()
            self.message_history: List[Message] = []
            self.running = False
            self.worker_thread = None
            self.initialized = True
            logger.info("MessageBus initialized")

    def subscribe(self, topic: str, callback: Callable[[Message], Any]):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.info(f"Subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, callback: Callable):
        if topic in self.subscribers:
            self.subscribers[topic].remove(callback)

    def publish(self, message: Message):
        priority_value = message.priority.value
        self.message_queue.put((priority_value * -1, message))
        self.message_history.append(message)
        logger.debug(f"Published message: {message.topic} from {message.sender}")

        if not self.running:
            self._process_queue()

    def _process_queue(self):
        while not self.message_queue.empty():
            try:
                _, message = self.message_queue.get_nowait()
                self._deliver_message(message)
            except queue.Empty:
                break

    def _deliver_message(self, message: Message):
        if message.recipient:
            if message.recipient in self.subscribers:
                for callback in self.subscribers[message.recipient]:
                    try:
                        callback(message)
                    except Exception as e:
                        logger.error(f"Error delivering message to {message.recipient}: {e}")

        if message.topic in self.subscribers:
            for callback in self.subscribers[message.topic]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback for {message.topic}: {e}")

    def request(self, sender: str, recipient: str, topic: str, payload: Dict[str, Any], timeout: int = 30) -> Optional[Message]:
        request_msg = Message(
            type=MessageType.REQUEST,
            sender=sender,
            recipient=recipient,
            topic=topic,
            payload=payload,
            priority=MessagePriority.HIGH
        )

        response_received = threading.Event()
        response_data = {}

        def response_handler(msg: Message):
            if msg.correlation_id == request_msg.id:
                response_data['message'] = msg
                response_received.set()

        self.subscribe(f"{topic}_response", response_handler)
        self.publish(request_msg)

        if response_received.wait(timeout):
            self.unsubscribe(f"{topic}_response", response_handler)
            return response_data.get('message')
        else:
            self.unsubscribe(f"{topic}_response", response_handler)
            logger.warning(f"Request timeout: {topic} from {sender} to {recipient}")
            return None

    def respond(self, original_message: Message, payload: Dict[str, Any]):
        response_msg = Message(
            type=MessageType.RESPONSE,
            sender=original_message.recipient,
            recipient=original_message.sender,
            topic=f"{original_message.topic}_response",
            payload=payload,
            correlation_id=original_message.id,
            priority=MessagePriority.HIGH
        )
        self.publish(response_msg)

    def get_history(self, topic: Optional[str] = None, limit: int = 100) -> List[Message]:
        if topic:
            filtered = [msg for msg in self.message_history if msg.topic == topic]
            return filtered[-limit:]
        return self.message_history[-limit:]

    def clear_history(self):
        self.message_history.clear()
        logger.info("Message history cleared")
