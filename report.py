"""报告生成模块"""

from typing import List
from datetime import datetime
from .memory_state import MemoryState, TurnAnalysis
from .hallucination import HallucinationType


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, memory_state: MemoryState):
        self.memory_state = memory_state
    
    def generate_markdown_report(self) -> str:
        """生成Markdown格式的时间线报告"""
        lines = []
        
        # 标题
        lines.append("# LLM记忆分析报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 执行摘要
        lines.append("## 📊 执行摘要")
        lines.append("")
        total_turns = len(self.memory_state.turns)
        total_memories = len(self.memory_state.memories)
        total_hallucinations = sum(len(t.hallucinations) for t in self.memory_state.turns)
        
        lines.append(f"- **总轮次数**: {total_turns}")
        lines.append(f"- **总记忆项**: {total_memories}")
        lines.append(f"- **幻觉总数**: {total_hallucinations}")
        lines.append("")
        
        # 记忆概览
        if self.memory_state.memories:
            lines.append("### 记忆项概览")
            lines.append("")
            for i, mem in enumerate(self.memory_state.memories):
                importance_emoji = "🔴" if mem.importance > 0.8 else "🟡" if mem.importance > 0.5 else "🟢"
                lines.append(f"{i}. {importance_emoji} **[{mem.category}]** {mem.content} (重要性: {mem.importance:.2f})")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 时间线分析
        lines.append("## ⏱️ 时间线分析")
        lines.append("")
        
        for turn in self.memory_state.turns:
            lines.append(f"### 轮次 {turn.turn_id}")
            lines.append("")
            
            # 用户输入
            lines.append("**👤 用户输入:**")
            lines.append(f"> {turn.user_input}")
            lines.append("")
            
            # LLM回复
            lines.append("**🤖 LLM回复:**")
            lines.append(f"> {turn.llm_response}")
            lines.append("")
            
            # 使用的记忆
            if turn.used_memories:
                lines.append("#### ✅ 使用的历史信息")
                lines.append("")
                for mem_id in turn.used_memories:
                    mem = self.memory_state.get_memory_by_id(mem_id)
                    if mem:
                        ref_text = turn.memory_references.get(mem_id, "")
                        lines.append(f"- **记忆 #{mem_id}** [{mem.category}]: {mem.content}")
                        if ref_text:
                            lines.append(f"  - 引用片段: `{ref_text[:100]}...`")
                lines.append("")
            else:
                lines.append("#### ⚠️ 未使用任何历史信息")
                lines.append("")
            
            # 遗漏的记忆
            if turn.missed_memories:
                lines.append("#### ❌ 遗漏的关键信息")
                lines.append("")
                for mem_id in turn.missed_memories:
                    mem = self.memory_state.get_memory_by_id(mem_id)
                    if mem:
                        importance_emoji = "🔴" if mem.importance > 0.8 else "🟡"
                        lines.append(f"- {importance_emoji} **记忆 #{mem_id}** [{mem.category}]: {mem.content}")
                        lines.append(f"  - 重要性: {mem.importance:.2f}")
                lines.append("")
            
            # 幻觉检测
            if turn.hallucinations:
                lines.append("#### 🚨 幻觉检测")
                lines.append("")
                for hall in turn.hallucinations:
                    type_emoji = {
                        HallucinationType.FABRICATED_MEMORY: "🔴",
                        HallucinationType.FORGOTTEN_CONTEXT: "🟡",
                        HallucinationType.WRONG_REFERENCE: "🟠"
                    }.get(hall.type, "⚪")
                    
                    type_name = {
                        HallucinationType.FABRICATED_MEMORY: "编造的记忆",
                        HallucinationType.FORGOTTEN_CONTEXT: "遗忘的上下文",
                        HallucinationType.WRONG_REFERENCE: "错误的引用"
                    }.get(hall.type, str(hall.type.value))
                    
                    lines.append(f"- {type_emoji} **{type_name}**")
                    lines.append(f"  - 描述: {hall.description}")
                    lines.append(f"  - 证据: `{hall.evidence}`")
                    lines.append(f"  - 严重程度: {hall.severity:.2f}")
                    if hall.suggested_correction:
                        lines.append(f"  - 建议修正: {hall.suggested_correction}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # 统计总结
        lines.append("## 📈 统计总结")
        lines.append("")
        
        # 记忆使用统计
        memory_usage = {}
        for turn in self.memory_state.turns:
            for mem_id in turn.used_memories:
                memory_usage[mem_id] = memory_usage.get(mem_id, 0) + 1
        
        if memory_usage:
            lines.append("### 记忆使用频率")
            lines.append("")
            sorted_usage = sorted(memory_usage.items(), key=lambda x: x[1], reverse=True)
            for mem_id, count in sorted_usage[:10]:  # 显示前10个
                mem = self.memory_state.get_memory_by_id(mem_id)
                if mem:
                    lines.append(f"- 记忆 #{mem_id}: {count} 次 - {mem.content[:50]}...")
            lines.append("")
        
        # 幻觉统计
        hallucination_by_type = {}
        for turn in self.memory_state.turns:
            for hall in turn.hallucinations:
                hall_type = hall.type.value
                hallucination_by_type[hall_type] = hallucination_by_type.get(hall_type, 0) + 1
        
        if hallucination_by_type:
            lines.append("### 幻觉类型分布")
            lines.append("")
            type_names = {
                "fabricated_memory": "编造的记忆",
                "forgotten_context": "遗忘的上下文",
                "wrong_reference": "错误的引用"
            }
            for hall_type, count in hallucination_by_type.items():
                lines.append(f"- {type_names.get(hall_type, hall_type)}: {count} 次")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_report(self, filepath: str):
        """保存报告到文件"""
        report = self.generate_markdown_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
