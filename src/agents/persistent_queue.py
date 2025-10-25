import json
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import hashlib
from src.utils.logger import default_logger as logger

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"

@dataclass
class PersistentMessage:
    id: str
    topic: str
    payload: Dict[str, Any]
    priority: int
    sender: str
    recipient: Optional[str]
    idempotency_key: str
    status: str = MessageStatus.PENDING.value
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = ""
    processed_at: Optional[str] = None
    error_message: Optional[str] = None

class PersistentMessageQueue:
    def __init__(self, db_path: str = "data/message_queue.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"PersistentMessageQueue initialized: {db_path}")

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            payload TEXT NOT NULL,
            priority INTEGER NOT NULL,
            sender TEXT NOT NULL,
            recipient TEXT,
            idempotency_key TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            created_at TEXT NOT NULL,
            processed_at TEXT,
            error_message TEXT
        )
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_status ON messages(status)
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_priority ON messages(priority DESC, created_at ASC)
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_idempotency ON messages(idempotency_key)
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
        ''')

        conn.commit()
        conn.close()

    def enqueue(self, topic: str, payload: Dict[str, Any], sender: str,
                recipient: Optional[str] = None, priority: int = 1,
                idempotency_key: Optional[str] = None) -> Optional[str]:
        if idempotency_key is None:
            idempotency_key = self._generate_idempotency_key(topic, payload, sender)

        if self._message_exists(idempotency_key):
            logger.info(f"Message already exists (idempotent): {idempotency_key}")
            return None

        message_id = hashlib.sha256(
            f"{topic}{sender}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            INSERT INTO messages (
                id, topic, payload, priority, sender, recipient,
                idempotency_key, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                topic,
                json.dumps(payload),
                priority,
                sender,
                recipient,
                idempotency_key,
                MessageStatus.PENDING.value,
                datetime.now().isoformat()
            ))

            self._log_event(cursor, message_id, "ENQUEUED", "Message added to queue")

            conn.commit()
            logger.info(f"Message enqueued: {message_id} (topic: {topic})")
            return message_id

        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate idempotency key: {idempotency_key}")
            return None
        except Exception as e:
            logger.error(f"Error enqueueing message: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def dequeue(self, limit: int = 1) -> List[PersistentMessage]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT * FROM messages
            WHERE status = ? AND retry_count < max_retries
            ORDER BY priority DESC, created_at ASC
            LIMIT ?
            ''', (MessageStatus.PENDING.value, limit))

            rows = cursor.fetchall()
            messages = []

            for row in rows:
                message = self._row_to_message(row)
                messages.append(message)

                cursor.execute('''
                UPDATE messages
                SET status = ?, processed_at = ?
                WHERE id = ?
                ''', (MessageStatus.PROCESSING.value, datetime.now().isoformat(), message.id))

                self._log_event(cursor, message.id, "PROCESSING", "Message dequeued for processing")

            conn.commit()
            return messages

        except Exception as e:
            logger.error(f"Error dequeuing messages: {e}")
            conn.rollback()
            return []
        finally:
            conn.close()

    def mark_completed(self, message_id: str):
        self._update_status(message_id, MessageStatus.COMPLETED, "Processing completed successfully")

    def mark_failed(self, message_id: str, error_message: str):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT retry_count, max_retries FROM messages WHERE id = ?
            ''', (message_id,))

            row = cursor.fetchone()
            if not row:
                return

            retry_count, max_retries = row

            if retry_count + 1 >= max_retries:
                cursor.execute('''
                UPDATE messages
                SET status = ?, error_message = ?, retry_count = retry_count + 1
                WHERE id = ?
                ''', (MessageStatus.DEAD_LETTER.value, error_message, message_id))

                self._log_event(cursor, message_id, "DEAD_LETTER",
                              f"Max retries reached. Error: {error_message}")
                logger.warning(f"Message moved to dead letter: {message_id}")

            else:
                cursor.execute('''
                UPDATE messages
                SET status = ?, error_message = ?, retry_count = retry_count + 1
                WHERE id = ?
                ''', (MessageStatus.PENDING.value, error_message, message_id))

                self._log_event(cursor, message_id, "RETRY",
                              f"Retry {retry_count + 1}/{max_retries}. Error: {error_message}")
                logger.info(f"Message retry queued: {message_id} (attempt {retry_count + 1})")

            conn.commit()

        except Exception as e:
            logger.error(f"Error marking message as failed: {e}")
            conn.rollback()
        finally:
            conn.close()

    def replay_messages(self, topic: Optional[str] = None,
                       from_timestamp: Optional[str] = None) -> List[PersistentMessage]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM messages WHERE status = ?"
            params = [MessageStatus.COMPLETED.value]

            if topic:
                query += " AND topic = ?"
                params.append(topic)

            if from_timestamp:
                query += " AND created_at >= ?"
                params.append(from_timestamp)

            query += " ORDER BY created_at ASC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            messages = [self._row_to_message(row) for row in rows]
            logger.info(f"Replaying {len(messages)} messages")

            return messages

        except Exception as e:
            logger.error(f"Error replaying messages: {e}")
            return []
        finally:
            conn.close()

    def get_dead_letter_messages(self) -> List[PersistentMessage]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT * FROM messages WHERE status = ?
            ORDER BY created_at DESC
            ''', (MessageStatus.DEAD_LETTER.value,))

            rows = cursor.fetchall()
            return [self._row_to_message(row) for row in rows]

        except Exception as e:
            logger.error(f"Error fetching dead letter messages: {e}")
            return []
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            stats = {}

            for status in MessageStatus:
                cursor.execute('''
                SELECT COUNT(*) FROM messages WHERE status = ?
                ''', (status.value,))
                count = cursor.fetchone()[0]
                stats[status.value] = count

            cursor.execute('SELECT COUNT(*) FROM messages')
            stats['total'] = cursor.fetchone()[0]

            cursor.execute('''
            SELECT AVG(retry_count) FROM messages WHERE status = ?
            ''', (MessageStatus.COMPLETED.value,))
            avg_retries = cursor.fetchone()[0] or 0.0
            stats['avg_retries'] = float(avg_retries)

            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close()

    def _message_exists(self, idempotency_key: str) -> bool:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT COUNT(*) FROM messages WHERE idempotency_key = ?
            ''', (idempotency_key,))

            count = cursor.fetchone()[0]
            return count > 0

        finally:
            conn.close()

    def _generate_idempotency_key(self, topic: str, payload: Dict[str, Any], sender: str) -> str:
        content = f"{topic}:{sender}:{json.dumps(payload, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _update_status(self, message_id: str, status: MessageStatus, log_message: str):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            UPDATE messages
            SET status = ?, processed_at = ?
            WHERE id = ?
            ''', (status.value, datetime.now().isoformat(), message_id))

            self._log_event(cursor, message_id, status.value.upper(), log_message)

            conn.commit()
            logger.info(f"Message status updated: {message_id} -> {status.value}")

        except Exception as e:
            logger.error(f"Error updating status: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _log_event(self, cursor, message_id: str, event_type: str, details: str):
        cursor.execute('''
        INSERT INTO message_log (message_id, event_type, timestamp, details)
        VALUES (?, ?, ?, ?)
        ''', (message_id, event_type, datetime.now().isoformat(), details))

    def _row_to_message(self, row) -> PersistentMessage:
        return PersistentMessage(
            id=row[0],
            topic=row[1],
            payload=json.loads(row[2]),
            priority=row[3],
            sender=row[4],
            recipient=row[5],
            idempotency_key=row[6],
            status=row[7],
            retry_count=row[8],
            max_retries=row[9],
            created_at=row[10],
            processed_at=row[11],
            error_message=row[12]
        )

    def purge_old_messages(self, days: int = 30):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cutoff_date = datetime.now().isoformat()[:10]

            cursor.execute('''
            DELETE FROM messages
            WHERE status = ? AND DATE(processed_at) < DATE(?, '-' || ? || ' days')
            ''', (MessageStatus.COMPLETED.value, cutoff_date, days))

            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Purged {deleted_count} old messages (older than {days} days)")
            return deleted_count

        except Exception as e:
            logger.error(f"Error purging messages: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
