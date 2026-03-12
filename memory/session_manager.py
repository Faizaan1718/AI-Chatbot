from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


Role = Literal["user", "assistant"]


@dataclass
class Turn:
    role: Role
    content: str


@dataclass
class Session:
    turns: List[Turn] = field(default_factory=list)


class SessionManager:
    def __init__(self, max_turns: int = 10) -> None:
        self.max_turns = max_turns
        self._sessions: Dict[str, Session] = {}

    def get_context(self, session_id: str) -> List[Turn]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.turns[-self.max_turns :]

    def append_turn(self, session_id: str, role: Role, content: str) -> None:
        session = self._sessions.setdefault(session_id, Session())
        session.turns.append(Turn(role=role, content=content))
        if len(session.turns) > self.max_turns * 2:
            session.turns = session.turns[-self.max_turns * 2 :]

    def clear_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]

