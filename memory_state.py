"""记忆状态建模模块"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime


@dataclass
class MemoryItem:
    """单个记忆项"""
    turn_id: int
    content: str
    importance: float  # 0.0-1.0
    category: str  # "fact", "preference", "context", "instruction"
    referenced_by: Set[int] = field(default_factory=set)  # 被哪些轮次引用


@dataclass
class TurnAnalysis:
    """单轮对话分析结果"""
    turn_id: int
    user_input: str
    llm_response: str
    
    # 使用的历史信息
    used_memories: List[int] = field(default_factory=list)  # 引用的记忆项ID
    
    # 遗漏的关键信息
    missed_memories: List[int] = field(default_factory=list)
    
    # 幻觉检测
    hallucinations: List['Hallucination'] = field(default_factory=list)
    
    # 记忆项引用详情
    memory_references: Dict[int, str] = field(default_factory=dict)  # {memory_id: "引用片段"}


@dataclass
class MemoryState:
    """整体记忆状态"""
    turns: List[TurnAnalysis] = field(default_factory=list)
    memories: List[MemoryItem] = field(default_factory=list)
    
    def add_memory(self, turn_id: int, content: str, importance: float, category: str) -> int:
        """添加新的记忆项，返回记忆ID"""
        memory_id = len(self.memories)
        memory = MemoryItem(
            turn_id=turn_id,
            content=content,
            importance=importance,
            category=category
        )
        self.memories.append(memory)
        return memory_id
    
    def get_memory_by_id(self, memory_id: int) -> Optional[MemoryItem]:
        """根据ID获取记忆项"""
        if 0 <= memory_id < len(self.memories):
            return self.memories[memory_id]
        return None
    
    def get_memories_by_turn(self, turn_id: int) -> List[MemoryItem]:
        """获取某轮对话产生的所有记忆"""
        return [m for m in self.memories if m.turn_id == turn_id]
