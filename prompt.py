"""Prompt设计模块"""

from typing import List, Dict


class PromptBuilder:
    """Prompt构建器"""
    
    @staticmethod
    def build_analysis_prompt(turn_id: int, 
                             user_input: str,
                             llm_response: str,
                             history: List[Dict[str, str]]) -> str:
        """
        构建分析Prompt
        
        Args:
            turn_id: 当前轮次ID
            user_input: 用户输入
            llm_response: LLM回复
            history: 历史对话列表，每个元素包含 {"role": "user/assistant", "content": "..."}
        
        Returns:
            完整的分析Prompt
        """
        history_text = "\n".join([
            f"[轮次 {i+1}] {item['role']}: {item['content']}"
            for i, item in enumerate(history)
        ])
        
        prompt = f"""你是一个LLM记忆分析专家。请分析以下对话中LLM的记忆使用情况。

## 分析规则
1. **只能基于给定的历史对话判断**，不要假设任何未提供的信息
2. **严格区分**：
   - 明确使用的历史信息
   - 应该使用但遗漏的关键信息
   - 基于不存在上下文生成的内容（幻觉）

## 历史对话
{history_text}

## 当前轮次分析
**轮次 {turn_id}**
用户输入: {user_input}
LLM回复: {llm_response}

## 分析任务
请以JSON格式输出分析结果：

{{
  "used_memories": [
    {{
      "memory_id": 0,
      "content": "引用的历史信息片段",
      "reference_text": "LLM回复中引用该信息的文本片段",
      "relevance": 0.9
    }}
  ],
  "missed_memories": [
    {{
      "memory_id": 1,
      "content": "应该引用但遗漏的历史信息",
      "importance": 0.8,
      "reason": "为什么这个信息很重要"
    }}
  ],
  "hallucinations": [
    {{
      "type": "fabricated_memory|forgotten_context|wrong_reference",
      "description": "幻觉描述",
      "evidence": "LLM回复中的证据片段",
      "severity": 0.7,
      "suggested_correction": "建议的修正"
    }}
  ]
}}

## 幻觉类型说明
- **fabricated_memory**: LLM声称存在但实际不存在的历史信息
- **forgotten_context**: LLM遗漏了应该记住的关键上下文
- **wrong_reference**: LLM错误地引用了历史信息

请仔细分析，确保：
1. 所有引用的记忆都有对应的历史对话依据
2. 遗漏的记忆确实是关键且相关的
3. 幻觉判断有明确的证据支持
"""
        return prompt
    
    @staticmethod
    def build_memory_extraction_prompt(turn_id: int,
                                      user_input: str,
                                      llm_response: str) -> str:
        """
        构建记忆提取Prompt
        
        Args:
            turn_id: 当前轮次ID
            user_input: 用户输入
            llm_response: LLM回复
        
        Returns:
            记忆提取Prompt
        """
        prompt = f"""从以下对话轮次中提取应该被记住的关键信息。

**轮次 {turn_id}**
用户输入: {user_input}
LLM回复: {llm_response}

请以JSON格式输出应该记住的信息：

{{
  "memories": [
    {{
      "content": "记忆内容",
      "importance": 0.8,
      "category": "fact|preference|context|instruction"
    }}
  ]
}}

## 记忆类别
- **fact**: 事实信息（如姓名、日期、地点等）
- **preference**: 用户偏好（如喜欢的颜色、风格等）
- **context**: 上下文信息（如当前任务、状态等）
- **instruction**: 指令或要求

只提取重要且可能在后续对话中使用的信息。
"""
        return prompt
