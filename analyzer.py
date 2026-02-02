"""主分析逻辑模块"""

import json
import re
from typing import List, Dict, Optional
from .memory_state import MemoryState, TurnAnalysis, MemoryItem
from .hallucination import Hallucination, HallucinationType, HallucinationDetector
from .prompt import PromptBuilder


class LLMMemoryAnalyzer:
    """LLM记忆分析器"""
    
    def __init__(self, llm_client=None):
        """
        初始化分析器
        
        Args:
            llm_client: LLM客户端，需要实现call方法
                        如果为None，将使用模拟分析（用于测试）
        """
        self.llm_client = llm_client
        self.prompt_builder = PromptBuilder()
        self.hallucination_detector = HallucinationDetector()
        self.memory_state = MemoryState()
    
    def analyze_dialogue(self, dialogue_data: Dict) -> MemoryState:
        """
        分析整个对话
        
        Args:
            dialogue_data: 对话数据，格式：
                {
                    "turns": [
                        {"role": "user", "content": "..."},
                        {"role": "assistant", "content": "..."},
                        ...
                    ]
                }
        
        Returns:
            MemoryState对象，包含完整的分析结果
        """
        turns = dialogue_data.get("turns", [])
        history = []
        
        # 按轮次分析（每两轮为一组：user + assistant）
        for i in range(0, len(turns), 2):
            if i + 1 >= len(turns):
                break
            
            user_turn = turns[i]
            assistant_turn = turns[i + 1]
            
            if user_turn.get("role") != "user" or assistant_turn.get("role") != "assistant":
                continue
            
            turn_id = i // 2 + 1
            user_input = user_turn.get("content", "")
            llm_response = assistant_turn.get("content", "")
            
            # 提取当前轮次的记忆
            memories = self._extract_memories(turn_id, user_input, llm_response)
            memory_ids = []
            for mem in memories:
                mem_id = self.memory_state.add_memory(
                    turn_id=turn_id,
                    content=mem["content"],
                    importance=mem["importance"],
                    category=mem["category"]
                )
                memory_ids.append(mem_id)
            
            # 分析当前轮次
            analysis = self._analyze_turn(
                turn_id=turn_id,
                user_input=user_input,
                llm_response=llm_response,
                history=history.copy()
            )
            
            self.memory_state.turns.append(analysis)
            
            # 更新历史
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": llm_response})
        
        return self.memory_state
    
    def _extract_memories(self, turn_id: int, user_input: str, llm_response: str) -> List[Dict]:
        """提取记忆"""
        if self.llm_client:
            prompt = self.prompt_builder.build_memory_extraction_prompt(
                turn_id, user_input, llm_response
            )
            response = self.llm_client.call(prompt)
            try:
                result = json.loads(response)
                return result.get("memories", [])
            except:
                return []
        else:
            # 模拟提取（用于测试）
            return self._simulate_memory_extraction(user_input, llm_response)
    
    def _simulate_memory_extraction(self, user_input: str, llm_response: str) -> List[Dict]:
        """模拟记忆提取（用于测试）"""
        memories = []
        
        # 提取姓名
        import re
        name_patterns = [
            r"我叫([\u4e00-\u9fa5]+)",
            r"我是([\u4e00-\u9fa5]+)",
            r"我的名字是([\u4e00-\u9fa5]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, user_input)
            if match:
                name = match.group(1)
                memories.append({
                    "content": f"用户姓名: {name}",
                    "importance": 0.9,
                    "category": "fact"
                })
                break
        
        # 提取地点信息
        location_patterns = [
            r"我来自([\u4e00-\u9fa5]+)",
            r"我在([\u4e00-\u9fa5]+)",
            r"我是([\u4e00-\u9fa5]+)人"
        ]
        for pattern in location_patterns:
            match = re.search(pattern, user_input)
            if match:
                location = match.group(1)
                memories.append({
                    "content": f"用户来自: {location}",
                    "importance": 0.9,
                    "category": "fact"
                })
                break
        
        # 提取偏好信息
        if "喜欢" in user_input or "爱好" in user_input or "兴趣" in user_input:
            # 提取"喜欢"后面的内容
            like_match = re.search(r"喜欢([^，。！？]+)", user_input)
            if like_match:
                preference = like_match.group(1).strip()
                memories.append({
                    "content": user_input,
                    "importance": 0.7,
                    "category": "preference"
                })
        
        return memories
    
    def _analyze_turn(self, turn_id: int, user_input: str, 
                     llm_response: str, history: List[Dict]) -> TurnAnalysis:
        """分析单轮对话"""
        if self.llm_client:
            prompt = self.prompt_builder.build_analysis_prompt(
                turn_id, user_input, llm_response, history
            )
            response = self.llm_client.call(prompt)
            try:
                result = json.loads(response)
                return self._parse_analysis_result(turn_id, user_input, llm_response, result)
            except Exception as e:
                print(f"分析轮次 {turn_id} 时出错: {e}")
                return TurnAnalysis(turn_id=turn_id, user_input=user_input, llm_response=llm_response)
        else:
            # 模拟分析（用于测试）
            return self._simulate_analysis(turn_id, user_input, llm_response, history)
    
    def _parse_analysis_result(self, turn_id: int, user_input: str, 
                              llm_response: str, result: Dict) -> TurnAnalysis:
        """解析分析结果"""
        analysis = TurnAnalysis(
            turn_id=turn_id,
            user_input=user_input,
            llm_response=llm_response
        )
        
        # 解析使用的记忆
        for mem in result.get("used_memories", []):
            mem_id = mem.get("memory_id")
            if mem_id is not None:
                analysis.used_memories.append(mem_id)
                analysis.memory_references[mem_id] = mem.get("reference_text", "")
        
        # 解析遗漏的记忆
        for mem in result.get("missed_memories", []):
            mem_id = mem.get("memory_id")
            if mem_id is not None:
                analysis.missed_memories.append(mem_id)
        
        # 解析幻觉
        for hall in result.get("hallucinations", []):
            hall_type_str = hall.get("type", "")
            try:
                hall_type = HallucinationType(hall_type_str)
            except:
                continue
            
            hallucination = Hallucination(
                type=hall_type,
                turn_id=turn_id,
                description=hall.get("description", ""),
                evidence=hall.get("evidence", ""),
                severity=hall.get("severity", 0.5),
                suggested_correction=hall.get("suggested_correction")
            )
            analysis.hallucinations.append(hallucination)
        
        return analysis
    
    def _simulate_analysis(self, turn_id: int, user_input: str,
                          llm_response: str, history: List[Dict]) -> TurnAnalysis:
        """模拟分析（用于测试）"""
        analysis = TurnAnalysis(
            turn_id=turn_id,
            user_input=user_input,
            llm_response=llm_response
        )
        
        # 简单的启发式规则
        available_memories = [m.content for m in self.memory_state.memories]
        
        # 检查是否使用了历史信息
        for i, mem in enumerate(self.memory_state.memories):
            # 提取记忆中的关键信息
            mem_keywords = self._extract_keywords(mem.content)
            response_lower = llm_response.lower()
            
            # 检查是否引用了记忆
            if any(kw in response_lower for kw in mem_keywords if len(kw) > 2):
                analysis.used_memories.append(i)
                # 找到引用片段
                for kw in mem_keywords:
                    if kw in response_lower and len(kw) > 2:
                        idx = response_lower.find(kw)
                        if idx != -1:
                            start = max(0, idx - 20)
                            end = min(len(llm_response), idx + len(kw) + 20)
                            analysis.memory_references[i] = llm_response[start:end]
                            break
        
        # 检查遗漏的关键记忆
        for i, mem in enumerate(self.memory_state.memories):
            if mem.importance > 0.7 and i not in analysis.used_memories:
                # 检查是否应该被使用（用户询问相关话题）
                mem_keywords = self._extract_keywords(mem.content)
                user_lower = user_input.lower()
                if any(kw in user_lower for kw in mem_keywords if len(kw) > 2):
                    analysis.missed_memories.append(i)
        
        # 检测错误引用类型的幻觉
        # 检查LLM是否给出了与记忆不符的答案
        for i, mem in enumerate(self.memory_state.memories):
            if mem.category == "fact" and mem.importance > 0.7:
                mem_keywords = self._extract_keywords(mem.content)
                user_lower = user_input.lower()
                response_lower = llm_response.lower()
                
                # 如果用户询问相关话题，但LLM给出了错误答案
                if any(kw in user_lower for kw in ["来自", "城市", "哪里", "哪"]):
                    # 检查记忆中的城市名
                    if "北京" in mem.content:
                        if "上海" in response_lower or "广州" in response_lower or "深圳" in response_lower:
                            # 检测到错误引用
                            from .hallucination import Hallucination
                            analysis.hallucinations.append(Hallucination(
                                type=HallucinationType.WRONG_REFERENCE,
                                turn_id=turn_id,
                                description=f"LLM错误地声称用户来自其他城市，但实际记忆是{mem.content}",
                                evidence=llm_response,
                                severity=0.9,
                                suggested_correction=f"应该回答: {mem.content}"
                            ))
        
        # 检测其他类型的幻觉
        hallucinations = self.hallucination_detector.detect(
            turn_id=turn_id,
            llm_response=llm_response,
            available_memories=available_memories,
            used_memories=analysis.used_memories,
            missed_memories=analysis.missed_memories
        )
        analysis.hallucinations.extend(hallucinations)
        
        return analysis
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本中的关键词"""
        # 简单的关键词提取
        keywords = []
        # 提取中文（2-4字）
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        keywords.extend(chinese_words)
        # 提取英文单词
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        keywords.extend([w.lower() for w in english_words])
        return keywords
