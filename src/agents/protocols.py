from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import uuid

class ProtocolType(Enum):
    CONTRACT_NET = "contract_net"
    NEGOTIATION = "negotiation"
    AGREEMENT = "agreement"
    REQUEST_RESPONSE = "request_response"
    BROADCAST = "broadcast"

class ConversationState(Enum):
    INITIATED = "initiated"
    PROPOSAL_SENT = "proposal_sent"
    BIDDING = "bidding"
    EVALUATING = "evaluating"
    COMMITTED = "committed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"

@dataclass
class MessageSchema:
    schema_version: str = "1.0.0"
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: Optional[str] = None
    protocol: ProtocolType = ProtocolType.REQUEST_RESPONSE
    performative: str = "inform"
    sender: str = ""
    receiver: Optional[str] = None
    reply_to: Optional[str] = None
    reply_by: Optional[datetime] = None
    content: Dict[str, Any] = field(default_factory=dict)
    ontology: str = "bank-text-analysis"
    language: str = "json"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['protocol'] = self.protocol.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.reply_by:
            data['reply_by'] = self.reply_by.isoformat()
        return data

class Performative(Enum):
    INFORM = "inform"
    REQUEST = "request"
    QUERY = "query"
    PROPOSE = "propose"
    ACCEPT_PROPOSAL = "accept-proposal"
    REJECT_PROPOSAL = "reject-proposal"
    CONFIRM = "confirm"
    DISCONFIRM = "disconfirm"
    AGREE = "agree"
    REFUSE = "refuse"
    CANCEL = "cancel"
    CALL_FOR_PROPOSAL = "cfp"
    BID = "bid"
    AWARD = "award"
    COMMIT = "commit"
    ABORT = "abort"

@dataclass
class ContractNetProtocol:
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: ConversationState = ConversationState.INITIATED
    initiator: str = ""
    task_description: Dict[str, Any] = field(default_factory=dict)
    bids: List[Dict[str, Any]] = field(default_factory=list)
    selected_bidder: Optional[str] = None
    deadline: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

    def call_for_proposals(self, task: Dict[str, Any], deadline: datetime) -> MessageSchema:
        self.task_description = task
        self.deadline = deadline
        self.state = ConversationState.BIDDING

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.CONTRACT_NET,
            performative=Performative.CALL_FOR_PROPOSAL.value,
            sender=self.initiator,
            receiver=None,
            reply_by=deadline,
            content={
                "task": task,
                "evaluation_criteria": {
                    "cost": "minimize",
                    "quality": "maximize",
                    "time": "minimize"
                }
            }
        )

    def submit_bid(self, bidder: str, cost: float, quality_score: float,
                   estimated_time: float, capabilities: Dict[str, Any]) -> MessageSchema:
        bid = {
            "bidder": bidder,
            "cost": cost,
            "quality_score": quality_score,
            "estimated_time": estimated_time,
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
        self.bids.append(bid)

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.CONTRACT_NET,
            performative=Performative.BID.value,
            sender=bidder,
            receiver=self.initiator,
            content=bid
        )

    def evaluate_bids(self, weights: Dict[str, float] = None) -> str:
        if not self.bids:
            return None

        if weights is None:
            weights = {"cost": 0.3, "quality_score": 0.5, "estimated_time": 0.2}

        best_bid = None
        best_score = -float('inf')

        for bid in self.bids:
            score = (
                -bid['cost'] * weights['cost'] +
                bid['quality_score'] * weights['quality_score'] +
                -bid['estimated_time'] * weights['estimated_time']
            )

            if score > best_score:
                best_score = score
                best_bid = bid

        self.selected_bidder = best_bid['bidder'] if best_bid else None
        self.state = ConversationState.EVALUATING
        return self.selected_bidder

    def award_contract(self) -> MessageSchema:
        if not self.selected_bidder:
            raise ValueError("No bidder selected")

        self.state = ConversationState.COMMITTED

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.CONTRACT_NET,
            performative=Performative.AWARD.value,
            sender=self.initiator,
            receiver=self.selected_bidder,
            content={
                "task": self.task_description,
                "awarded_to": self.selected_bidder
            }
        )

    def complete(self, result: Dict[str, Any]) -> MessageSchema:
        self.result = result
        self.state = ConversationState.COMPLETED

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.CONTRACT_NET,
            performative=Performative.INFORM.value,
            sender=self.selected_bidder,
            receiver=self.initiator,
            content={"result": result, "status": "completed"}
        )

    def abort(self, reason: str) -> MessageSchema:
        self.state = ConversationState.ABORTED

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.CONTRACT_NET,
            performative=Performative.ABORT.value,
            sender=self.initiator,
            content={"reason": reason}
        )

@dataclass
class NegotiationProtocol:
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: ConversationState = ConversationState.INITIATED
    participants: List[str] = field(default_factory=list)
    proposals: List[Dict[str, Any]] = field(default_factory=list)
    agreements: List[Dict[str, Any]] = field(default_factory=list)
    max_rounds: int = 5
    current_round: int = 0

    def propose(self, proposer: str, proposal: Dict[str, Any]) -> MessageSchema:
        self.proposals.append({
            "proposer": proposer,
            "proposal": proposal,
            "round": self.current_round,
            "timestamp": datetime.now().isoformat()
        })

        self.state = ConversationState.PROPOSAL_SENT

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.NEGOTIATION,
            performative=Performative.PROPOSE.value,
            sender=proposer,
            content=proposal
        )

    def accept(self, acceptor: str, proposal_id: str) -> MessageSchema:
        self.agreements.append({
            "acceptor": acceptor,
            "proposal_id": proposal_id,
            "timestamp": datetime.now().isoformat()
        })

        if len(self.agreements) >= len(self.participants) - 1:
            self.state = ConversationState.COMMITTED

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.NEGOTIATION,
            performative=Performative.ACCEPT_PROPOSAL.value,
            sender=acceptor,
            content={"proposal_id": proposal_id}
        )

    def reject(self, rejector: str, proposal_id: str, reason: str) -> MessageSchema:
        self.current_round += 1

        if self.current_round >= self.max_rounds:
            self.state = ConversationState.FAILED

        return MessageSchema(
            conversation_id=self.conversation_id,
            protocol=ProtocolType.NEGOTIATION,
            performative=Performative.REJECT_PROPOSAL.value,
            sender=rejector,
            content={
                "proposal_id": proposal_id,
                "reason": reason,
                "counter_proposal_allowed": self.current_round < self.max_rounds
            }
        )

    def is_agreement_reached(self) -> bool:
        return self.state == ConversationState.COMMITTED

    def get_agreement(self) -> Optional[Dict[str, Any]]:
        if not self.is_agreement_reached():
            return None

        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "final_proposal": self.proposals[-1] if self.proposals else None,
            "agreements": self.agreements,
            "rounds": self.current_round
        }

class ProtocolManager:
    def __init__(self):
        self.active_conversations: Dict[str, Any] = {}

    def start_contract_net(self, initiator: str, task: Dict[str, Any],
                          deadline: datetime) -> ContractNetProtocol:
        protocol = ContractNetProtocol(initiator=initiator)
        cfp_msg = protocol.call_for_proposals(task, deadline)
        self.active_conversations[protocol.conversation_id] = protocol
        return protocol

    def start_negotiation(self, participants: List[str]) -> NegotiationProtocol:
        protocol = NegotiationProtocol(participants=participants)
        self.active_conversations[protocol.conversation_id] = protocol
        return protocol

    def get_conversation(self, conversation_id: str) -> Optional[Any]:
        return self.active_conversations.get(conversation_id)

    def end_conversation(self, conversation_id: str):
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]

    def get_active_conversations(self) -> List[Dict[str, Any]]:
        return [
            {
                "conversation_id": conv_id,
                "type": type(protocol).__name__,
                "state": protocol.state.value
            }
            for conv_id, protocol in self.active_conversations.items()
        ]
