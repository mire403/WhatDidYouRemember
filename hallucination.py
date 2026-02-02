"""幻觉检测模块"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class HallucinationType(Enum):
    """幻觉类型"""
    FABRICATED_MEMORY = "fabricated_memory"  # 编造的记忆
    FORGOTTEN_CONTEXT = "forgotten_context"  # 遗忘的上下文
    WRONG_REFERENCE = "wrong_reference"  # 错误的引用


@dataclass
class Hallucination:
    """幻觉检测结果"""
    type: HallucinationType
    turn_id: int
    description: str
    evidence: str  # 证据片段
    severity: float  # 0.0-1.0，严重程度
    suggested_correction: Optional[str] = None


class HallucinationDetector:
    """幻觉检测器"""
    
    def __init__(self):
        self.hallucination_types = {
            HallucinationType.FABRICATED_MEMORY: "模型声称存在但实际不存在的历史信息",
            HallucinationType.FORGOTTEN_CONTEXT: "模型遗漏了应该记住的关键上下文",
            HallucinationType.WRONG_REFERENCE: "模型错误地引用了历史信息"
        }
    
    def detect(self, turn_id: int, llm_response: str, 
               available_memories: List[str],
               used_memories: List[int],
               missed_memories: List[int]) -> List[Hallucination]:
        """
        检测幻觉
        
        Args:
            turn_id: 当前轮次ID
            llm_response: LLM的回复
            available_memories: 可用的历史记忆列表
            used_memories: 已使用的记忆ID列表
            missed_memories: 遗漏的记忆ID列表
        
        Returns:
            检测到的幻觉列表
        """
        hallucinations = []
        
        # 检测遗漏的关键上下文
        if missed_memories:
            for memory_id in missed_memories:
                hallucinations.append(Hallucination(
                    type=HallucinationType.FORGOTTEN_CONTEXT,
                    turn_id=turn_id,
                    description=f"遗漏了关键记忆项 #{memory_id}",
                    evidence=f"记忆项: {available_memories[memory_id] if memory_id < len(available_memories) else 'N/A'}",
                    severity=0.7
                ))
        
        return hallucinations
