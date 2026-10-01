from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Message:
    sender: int
    receiver: int
    kind: str
    interval: Tuple[int, int]
    additional_cost: int
    priority: int


class Negotiator:
    def __init__(self) -> None:
        self.messages: List[Message] = []

    def request_repair(self, sender: int, receiver: int, interval: Tuple[int, int], additional_cost: int, priority: int) -> bool:
        self.messages.append(Message(sender, receiver, "REPAIR_REQUEST", interval, additional_cost, priority))
        accepted = additional_cost <= 30 or priority >= 5
        self.messages.append(Message(receiver, sender, "ACCEPT" if accepted else "REJECT", interval, additional_cost, priority))
        return accepted
