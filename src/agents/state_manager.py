import json
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib
from src.utils.logger import default_logger as logger

@dataclass
class AgentState:
    agent_id: str
    state_data: Dict[str, Any]
    version: int
    timestamp: str
    checksum: str

class StateManager:
    def __init__(self, db_path: str = "data/agent_states.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"StateManager initialized: {db_path}")

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_states (
            agent_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            state_data TEXT NOT NULL,
            checksum TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            PRIMARY KEY (agent_id, version)
        )
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_agent_latest ON agent_states(agent_id, version DESC)
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS state_transitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            from_version INTEGER,
            to_version INTEGER NOT NULL,
            transition_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT
        )
        ''')

        conn.commit()
        conn.close()

    def save_state(self, agent_id: str, state_data: Dict[str, Any]) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT MAX(version) FROM agent_states WHERE agent_id = ?
            ''', (agent_id,))

            result = cursor.fetchone()
            current_version = (result[0] or 0) + 1

            state_json = json.dumps(state_data, sort_keys=True)
            checksum = hashlib.sha256(state_json.encode()).hexdigest()
            timestamp = datetime.now().isoformat()

            cursor.execute('''
            INSERT INTO agent_states (agent_id, version, state_data, checksum, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (agent_id, current_version, state_json, checksum, timestamp))

            cursor.execute('''
            INSERT INTO state_transitions (agent_id, from_version, to_version, transition_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (agent_id, current_version - 1 if current_version > 1 else None,
                  current_version, "SAVE", timestamp))

            conn.commit()
            logger.info(f"State saved for {agent_id} (version {current_version})")

            return current_version

        except Exception as e:
            logger.error(f"Error saving state: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def load_state(self, agent_id: str, version: Optional[int] = None) -> Optional[AgentState]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            if version is None:
                cursor.execute('''
                SELECT * FROM agent_states
                WHERE agent_id = ?
                ORDER BY version DESC
                LIMIT 1
                ''', (agent_id,))
            else:
                cursor.execute('''
                SELECT * FROM agent_states
                WHERE agent_id = ? AND version = ?
                ''', (agent_id, version))

            row = cursor.fetchone()

            if not row:
                return None

            state_data = json.loads(row[2])

            state = AgentState(
                agent_id=row[0],
                version=row[1],
                state_data=state_data,
                checksum=row[3],
                timestamp=row[4]
            )

            logger.info(f"State loaded for {agent_id} (version {state.version})")
            return state

        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return None
        finally:
            conn.close()

    def restore_state(self, agent_id: str, version: int) -> Optional[AgentState]:
        state = self.load_state(agent_id, version)

        if state:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            try:
                cursor.execute('''
                INSERT INTO state_transitions (agent_id, from_version, to_version, transition_type, timestamp)
                VALUES (?, (SELECT MAX(version) FROM agent_states WHERE agent_id = ?), ?, ?, ?)
                ''', (agent_id, agent_id, version, "RESTORE", datetime.now().isoformat()))

                conn.commit()
                logger.info(f"State restored for {agent_id} to version {version}")

            except Exception as e:
                logger.error(f"Error logging restore transition: {e}")
                conn.rollback()
            finally:
                conn.close()

        return state

    def create_snapshot(self, agent_ids: List[str], snapshot_name: str) -> str:
        snapshot_id = hashlib.sha256(
            f"{snapshot_name}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        snapshot_data = {
            "snapshot_id": snapshot_id,
            "snapshot_name": snapshot_name,
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }

        for agent_id in agent_ids:
            state = self.load_state(agent_id)
            if state:
                snapshot_data["agents"][agent_id] = {
                    "version": state.version,
                    "state_data": state.state_data,
                    "checksum": state.checksum
                }

        snapshot_file = self.db_path.parent / f"snapshot_{snapshot_id}.json"
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot_data, f, indent=2)

        logger.info(f"Snapshot created: {snapshot_id} ({len(snapshot_data['agents'])} agents)")
        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        snapshot_file = self.db_path.parent / f"snapshot_{snapshot_id}.json"

        if not snapshot_file.exists():
            logger.error(f"Snapshot not found: {snapshot_id}")
            return {"success": False, "error": "Snapshot not found"}

        with open(snapshot_file, 'r') as f:
            snapshot_data = json.load(f)

        results = {}

        for agent_id, agent_data in snapshot_data["agents"].items():
            try:
                self.save_state(agent_id, agent_data["state_data"])
                results[agent_id] = {"success": True}
            except Exception as e:
                results[agent_id] = {"success": False, "error": str(e)}

        logger.info(f"Snapshot restored: {snapshot_id}")
        return {
            "success": True,
            "snapshot_id": snapshot_id,
            "results": results
        }

    def get_state_history(self, agent_id: str, limit: int = 10) -> List[AgentState]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('''
            SELECT * FROM agent_states
            WHERE agent_id = ?
            ORDER BY version DESC
            LIMIT ?
            ''', (agent_id, limit))

            rows = cursor.fetchall()

            states = []
            for row in rows:
                state = AgentState(
                    agent_id=row[0],
                    version=row[1],
                    state_data=json.loads(row[2]),
                    checksum=row[3],
                    timestamp=row[4]
                )
                states.append(state)

            return states

        except Exception as e:
            logger.error(f"Error fetching state history: {e}")
            return []
        finally:
            conn.close()

    def verify_state_integrity(self, agent_id: str, version: int) -> bool:
        state = self.load_state(agent_id, version)

        if not state:
            return False

        state_json = json.dumps(state.state_data, sort_keys=True)
        computed_checksum = hashlib.sha256(state_json.encode()).hexdigest()

        is_valid = computed_checksum == state.checksum

        if not is_valid:
            logger.warning(f"State integrity check failed for {agent_id} version {version}")

        return is_valid

    def get_statistics(self) -> Dict[str, Any]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COUNT(DISTINCT agent_id) FROM agent_states')
            total_agents = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM agent_states')
            total_states = cursor.fetchone()[0]

            cursor.execute('''
            SELECT agent_id, MAX(version) as latest_version
            FROM agent_states
            GROUP BY agent_id
            ''')

            agent_versions = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute('''
            SELECT COUNT(*) FROM state_transitions WHERE transition_type = 'RESTORE'
            ''')
            total_restores = cursor.fetchone()[0]

            return {
                "total_agents": total_agents,
                "total_states": total_states,
                "agent_versions": agent_versions,
                "total_restores": total_restores
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close()
