<div align="center">

# 🧠 WhatDidYouRemember

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

**一个强大的LLM记忆分析工具，帮你洞察AI对话中的记忆机制** 🔍

[功能特性](#-核心功能) • [快速开始](#-快速开始) • [使用示例](#-使用示例) • [技术架构](#-技术架构) • [贡献指南](#-贡献指南)

</div>

---

## 📖 项目简介

**WhatDidYouRemember** 是一个专为**大模型可解释性研究**设计的记忆分析工具。在多轮对话场景中，我们经常遇到这样的问题：

- 🤔 **LLM到底记住了什么？** - 它在回答时使用了哪些历史信息？
- ❌ **LLM忘记了什么？** - 哪些关键信息被遗漏了？
- 🚨 **LLM是否出现记忆幻觉？** - 它是否基于不存在的上下文生成了内容？

这个工具通过**系统化的分析流程**，为每一轮对话生成详细的记忆使用报告，帮助研究人员和开发者：

- 📊 **量化评估** LLM的记忆能力
- 🔬 **深度分析** 记忆失效的根本原因
- 🎯 **优化改进** 提示词和上下文管理策略
- 📈 **追踪监控** 长期对话中的记忆衰减模式

### 🎯 应用场景

- **🧪 模型评估**: 评估不同LLM模型的记忆能力差异
- **🔧 系统优化**: 识别记忆瓶颈，优化RAG系统设计
- **📚 学术研究**: 研究长上下文记忆机制和幻觉问题
- **🛡️ 质量保证**: 在生产环境中监控对话质量
- **📖 教育训练**: 帮助开发者理解LLM的记忆行为

---

## ✨ 核心功能

### 1. 🧩 智能记忆提取

自动从对话中提取关键记忆项，包括：
- **事实信息** (Fact): 姓名、日期、地点等结构化信息
- **用户偏好** (Preference): 喜好、习惯、风格等个性化信息
- **上下文信息** (Context): 任务状态、当前目标等动态信息
- **指令要求** (Instruction): 明确的规则和约束

**代码示例**：

```python
from WhatDidYouRemember import LLMMemoryAnalyzer

analyzer = LLMMemoryAnalyzer()
dialogue_data = {
    "turns": [
        {"role": "user", "content": "我叫张三，来自北京"},
        {"role": "assistant", "content": "你好张三！很高兴认识你。"}
    ]
}

memory_state = analyzer.analyze_dialogue(dialogue_data)
# 自动提取记忆: "用户姓名: 张三" (重要性: 0.9)
# 自动提取记忆: "用户来自: 北京" (重要性: 0.9)
```

**深度解析**：

记忆提取采用**多层次分析策略**：
1. **模式匹配**: 使用正则表达式识别常见的信息模式（如"我叫XXX"）
2. **语义理解**: 通过LLM API进行深度语义分析（可选）
3. **重要性评分**: 根据信息类型和上下文计算重要性（0.0-1.0）
4. **分类标记**: 自动分类为fact/preference/context/instruction

### 2. 🔍 记忆使用追踪

精确追踪每轮对话中LLM对历史信息的引用情况：

- ✅ **使用的记忆**: 明确标注引用了哪些历史信息
- 📝 **引用片段**: 展示LLM回复中具体引用该信息的文本
- 📊 **相关性评分**: 评估记忆使用的相关性程度

**代码示例**：

```python
# 分析结果示例
turn_analysis = memory_state.turns[2]  # 第3轮对话

print(f"使用的记忆ID: {turn_analysis.used_memories}")
# 输出: [0, 2]  # 使用了记忆项0和2

for mem_id in turn_analysis.used_memories:
    mem = memory_state.get_memory_by_id(mem_id)
    ref_text = turn_analysis.memory_references[mem_id]
    print(f"记忆 #{mem_id}: {mem.content}")
    print(f"引用片段: {ref_text}")
```

**深度解析**：

记忆追踪算法采用**模糊匹配 + 语义分析**的混合策略：

```python
def _simulate_analysis(self, turn_id, user_input, llm_response, history):
    """模拟分析的核心逻辑"""
    # 1. 关键词提取
    mem_keywords = self._extract_keywords(mem.content)
    # 提取中文词汇和英文单词
    
    # 2. 模糊匹配
    if any(kw in response_lower for kw in mem_keywords):
        analysis.used_memories.append(mem_id)
        # 记录引用位置和上下文
    
    # 3. 遗漏检测
    if mem.importance > 0.7 and mem_id not in used_memories:
        # 检查用户输入是否涉及该记忆
        if any(kw in user_input.lower() for kw in mem_keywords):
            analysis.missed_memories.append(mem_id)
```

### 3. ⚠️ 遗漏检测

识别LLM应该使用但遗漏的关键信息：

- 🔴 **高重要性遗漏**: 重要性 > 0.8 的关键信息被遗漏
- 🟡 **中等重要性遗漏**: 重要性 0.5-0.8 的信息被遗漏
- 📋 **遗漏原因分析**: 分析为什么该信息应该被使用

**示例场景**：

```json
{
  "turn_id": 5,
  "user_input": "我之前告诉过你我的名字，你还记得吗？",
  "llm_response": "抱歉，让我回忆一下...你之前提到过你的名字吗？",
  "missed_memories": [0],  // 记忆项0: "用户姓名: 张三"
  "hallucinations": [
    {
      "type": "forgotten_context",
      "description": "遗漏了关键记忆项 #0",
      "severity": 0.7
    }
  ]
}
```

### 4. 🚨 幻觉检测

检测三种类型的记忆幻觉：

#### 🔴 Fabricated Memory (编造的记忆)

LLM声称存在但实际不存在的历史信息。

```python
# 检测逻辑示例
if "上海" in llm_response and "北京" in memory.content:
    hallucination = Hallucination(
        type=HallucinationType.WRONG_REFERENCE,
        description="LLM错误地声称用户来自上海，但实际记忆是北京",
        evidence=llm_response,
        severity=0.9
    )
```

#### 🟡 Forgotten Context (遗忘的上下文)

LLM遗漏了应该记住的关键上下文信息。

```python
# 检测逻辑
for mem_id in missed_memories:
    if memory.importance > 0.7:
        hallucinations.append(Hallucination(
            type=HallucinationType.FORGOTTEN_CONTEXT,
            description=f"遗漏了关键记忆项 #{mem_id}",
            evidence=f"记忆项: {memory.content}",
            severity=0.7
        ))
```

#### 🟠 Wrong Reference (错误的引用)

LLM错误地引用了历史信息，导致事实错误。

**检测算法**：

```python
# 错误引用检测的核心逻辑
def detect_wrong_reference(self, turn_id, user_input, llm_response, memories):
    """检测错误引用"""
    # 1. 识别用户询问的话题
    if any(kw in user_input for kw in ["来自", "城市", "哪里"]):
        # 2. 查找相关记忆
        location_memory = find_location_memory(memories)
        
        # 3. 检查LLM回答是否与记忆一致
        if location_memory and "北京" in location_memory.content:
            if "上海" in llm_response or "广州" in llm_response:
                # 检测到错误引用！
                return Hallucination(
                    type=HallucinationType.WRONG_REFERENCE,
                    description="LLM错误地声称用户来自其他城市",
                    evidence=llm_response,
                    severity=0.9,
                    suggested_correction=f"应该回答: {location_memory.content}"
                )
```

### 5. 📊 时间线报告生成

生成详细的Markdown格式分析报告，包含：

- 📈 **执行摘要**: 总体统计信息（总轮次、记忆项、幻觉数）
- 📋 **记忆项概览**: 所有记忆项及其重要性评分
- ⏱️ **时间线分析**: 每轮对话的详细分析
- 📊 **统计总结**: 记忆使用频率、幻觉类型分布

**报告结构**：

```markdown
# LLM记忆分析报告

## 📊 执行摘要
- 总轮次数: 5
- 总记忆项: 3
- 幻觉总数: 2

## ⏱️ 时间线分析

### 轮次 1
**👤 用户输入:** ...
**🤖 LLM回复:** ...
#### ✅ 使用的历史信息
- 记忆 #0 [fact]: 用户姓名: 张三
  - 引用片段: `你好张三！很高兴认识你...`
#### 🚨 幻觉检测
- 🔴 错误的引用
  - 描述: LLM错误地声称用户来自上海
  - 严重程度: 0.90
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/WhatDidYouRemember.git
cd WhatDidYouRemember

# 安装依赖（核心功能无需外部依赖）
pip install -r requirements.txt

# 可选：安装开发版本
pip install -e .
```

### 基本使用

```bash
# 使用模拟分析（快速测试）
python -m WhatDidYouRemember.cli examples/dialogue.json

# 指定输出文件
python -m WhatDidYouRemember.cli examples/dialogue.json -o my_report.md

# 使用真实LLM API（更准确的分析）
python -m WhatDidYouRemember.cli examples/dialogue.json \
    --llm-api openai \
    --api-key YOUR_API_KEY \
    --model gpt-4
```

### Python API使用

```python
from WhatDidYouRemember import LLMMemoryAnalyzer, ReportGenerator
import json

# 1. 加载对话数据
with open('examples/dialogue.json', 'r', encoding='utf-8') as f:
    dialogue_data = json.load(f)

# 2. 创建分析器（不使用LLM API，使用模拟分析）
analyzer = LLMMemoryAnalyzer()

# 3. 执行分析
memory_state = analyzer.analyze_dialogue(dialogue_data)

# 4. 生成报告
report_generator = ReportGenerator(memory_state)
report = report_generator.generate_markdown_report()

# 5. 保存报告
with open('report.md', 'w', encoding='utf-8') as f:
    f.write(report)

# 6. 访问分析结果
for turn in memory_state.turns:
    print(f"轮次 {turn.turn_id}:")
    print(f"  使用的记忆: {turn.used_memories}")
    print(f"  遗漏的记忆: {turn.missed_memories}")
    print(f"  幻觉数量: {len(turn.hallucinations)}")
```

---

## 💻 使用示例

### 示例1: 分析对话记忆

**输入对话** (`examples/dialogue.json`):

```json
{
  "turns": [
    {"role": "user", "content": "你好，我叫张三，我来自北京。"},
    {"role": "assistant", "content": "你好张三！很高兴认识你。北京是个很棒的城市。"},
    {"role": "user", "content": "你还记得我的名字吗？"},
    {"role": "assistant", "content": "当然记得！你叫张三，来自北京。"}
  ]
}
```

**分析结果**：

```
轮次 1:
  ✅ 使用的记忆: [0, 2]  # 姓名和地点
  ❌ 遗漏的记忆: []
  🚨 幻觉数量: 0

轮次 2:
  ✅ 使用的记忆: [0, 2]  # 正确回忆
  ❌ 遗漏的记忆: []
  🚨 幻觉数量: 0
```

### 示例2: 检测记忆幻觉

**对话场景**：

```json
{
  "turns": [
    {"role": "user", "content": "我来自哪个城市？"},
    {"role": "assistant", "content": "你之前提到过你来自上海，对吗？"}
  ]
}
```

**检测结果**：

```python
hallucinations = [
    Hallucination(
        type=HallucinationType.WRONG_REFERENCE,
        description="LLM错误地声称用户来自上海，但实际记忆是北京",
        evidence="你之前提到过你来自上海，对吗？",
        severity=0.9,
        suggested_correction="应该回答: 你来自北京"
    )
]
```

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│              (命令行参数解析和用户交互)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              LLMMemoryAnalyzer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ PromptBuilder│  │MemoryExtractor│ │TurnAnalyzer  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│MemoryState  │ │Hallucination│ │ReportGen    │
│  - Memories │ │  Detector   │ │  - Markdown │
│  - Turns    │ │  - Types    │ │  - Stats    │
└─────────────┘ └─────────────┘ └─────────────┘
```

### 核心模块详解

#### 1. `analyzer.py` - 主分析引擎

**核心类**: `LLMMemoryAnalyzer`

```python
class LLMMemoryAnalyzer:
    """LLM记忆分析器 - 核心分析引擎"""
    
    def __init__(self, llm_client=None):
        """
        初始化分析器
        
        设计模式: Strategy Pattern
        - llm_client=None: 使用基于规则的模拟分析（快速）
        - llm_client=LLMClient: 使用真实LLM API（准确）
        """
        self.llm_client = llm_client
        self.prompt_builder = PromptBuilder()
        self.hallucination_detector = HallucinationDetector()
        self.memory_state = MemoryState()
    
    def analyze_dialogue(self, dialogue_data: Dict) -> MemoryState:
        """
        分析整个对话的主流程
        
        算法流程:
        1. 遍历对话轮次（user + assistant配对）
        2. 提取每轮的记忆项
        3. 分析每轮的记忆使用情况
        4. 检测遗漏和幻觉
        5. 累积构建记忆状态
        """
        # 实现细节见源码
```

**关键方法解析**：

```python
def _extract_memories(self, turn_id, user_input, llm_response):
    """
    记忆提取策略
    
    支持两种模式:
    1. LLM模式: 使用PromptBuilder构建prompt，调用LLM API
    2. 规则模式: 使用正则表达式和启发式规则
    """
    if self.llm_client:
        # LLM模式：更准确但需要API调用
        prompt = self.prompt_builder.build_memory_extraction_prompt(...)
        response = self.llm_client.call(prompt)
        return json.loads(response)["memories"]
    else:
        # 规则模式：快速但可能不够准确
        return self._simulate_memory_extraction(user_input, llm_response)
```

#### 2. `memory_state.py` - 记忆状态建模

**数据结构设计**：

```python
@dataclass
class MemoryItem:
    """单个记忆项的数据结构"""
    turn_id: int              # 产生该记忆的轮次
    content: str              # 记忆内容
    importance: float         # 重要性评分 (0.0-1.0)
    category: str            # 类别: fact/preference/context/instruction
    referenced_by: Set[int]  # 被哪些轮次引用（用于统计）

@dataclass
class TurnAnalysis:
    """单轮对话的分析结果"""
    turn_id: int
    user_input: str
    llm_response: str
    used_memories: List[int]           # 使用的记忆ID列表
    missed_memories: List[int]          # 遗漏的记忆ID列表
    hallucinations: List[Hallucination] # 幻觉列表
    memory_references: Dict[int, str]    # 记忆引用详情
```

**设计理念**：

- **不可变性**: 使用`@dataclass`确保数据结构清晰
- **可追溯性**: 每个记忆项记录产生轮次和引用轮次
- **可扩展性**: 支持添加新的记忆属性和分析维度

#### 3. `hallucination.py` - 幻觉检测引擎

**幻觉类型系统**：

```python
class HallucinationType(Enum):
    """幻觉类型枚举 - 基于研究分类"""
    FABRICATED_MEMORY = "fabricated_memory"    # 编造的记忆
    FORGOTTEN_CONTEXT = "forgotten_context"     # 遗忘的上下文
    WRONG_REFERENCE = "wrong_reference"        # 错误的引用

@dataclass
class Hallucination:
    """幻觉检测结果"""
    type: HallucinationType
    turn_id: int
    description: str              # 人类可读的描述
    evidence: str                 # 证据片段
    severity: float              # 严重程度 (0.0-1.0)
    suggested_correction: str    # 建议的修正（可选）
```

**检测算法**：

```python
class HallucinationDetector:
    """幻觉检测器 - 多策略检测"""
    
    def detect(self, turn_id, llm_response, 
               available_memories, used_memories, missed_memories):
        """
        多策略幻觉检测
        
        策略1: 遗漏检测
        - 如果高重要性记忆未被使用，标记为遗忘
        
        策略2: 错误引用检测（在analyzer中实现）
        - 对比LLM回答与记忆内容
        - 检测事实性错误
        
        策略3: 编造记忆检测（需要LLM API）
        - 检查LLM是否引用了不存在的历史信息
        """
        hallucinations = []
        
        # 策略1: 检测遗漏
        for mem_id in missed_memories:
            if mem_id < len(available_memories):
                hallucinations.append(Hallucination(
                    type=HallucinationType.FORGOTTEN_CONTEXT,
                    turn_id=turn_id,
                    description=f"遗漏了关键记忆项 #{mem_id}",
                    evidence=available_memories[mem_id],
                    severity=0.7
                ))
        
        return hallucinations
```

#### 4. `prompt.py` - Prompt工程

**Prompt设计原则**：

1. **明确性**: 明确告诉模型分析任务和规则
2. **结构化**: 使用JSON格式输出，便于解析
3. **示例驱动**: 提供清晰的示例和说明
4. **约束性**: 强调只能基于给定历史判断

**示例Prompt**：

```python
def build_analysis_prompt(self, turn_id, user_input, llm_response, history):
    """
    构建分析Prompt
    
    Prompt结构:
    1. 角色定义: "你是一个LLM记忆分析专家"
    2. 规则说明: 明确分析规则和约束
    3. 历史对话: 提供完整的历史上下文
    4. 当前轮次: 需要分析的对话轮次
    5. 输出格式: JSON格式的结构化输出
    6. 类型说明: 详细的幻觉类型说明
    """
    prompt = f"""你是一个LLM记忆分析专家。请分析以下对话中LLM的记忆使用情况。

## 分析规则
1. **只能基于给定的历史对话判断**，不要假设任何未提供的信息
2. **严格区分**：
   - 明确使用的历史信息
   - 应该使用但遗漏的关键信息
   - 基于不存在上下文生成的内容（幻觉）

## 历史对话
{format_history(history)}

## 当前轮次分析
**轮次 {turn_id}**
用户输入: {user_input}
LLM回复: {llm_response}

## 分析任务
请以JSON格式输出分析结果...
"""
    return prompt
```

#### 5. `report.py` - 报告生成器

**报告生成流程**：

```python
class ReportGenerator:
    """报告生成器 - 模板化报告生成"""
    
    def generate_markdown_report(self) -> str:
        """
        生成Markdown报告
        
        报告结构:
        1. 标题和元信息
        2. 执行摘要（统计信息）
        3. 记忆项概览
        4. 时间线分析（每轮详细分析）
        5. 统计总结（使用频率、幻觉分布）
        """
        lines = []
        
        # 1. 生成标题
        lines.append("# LLM记忆分析报告")
        
        # 2. 生成摘要
        lines.append(self._generate_summary())
        
        # 3. 生成时间线
        for turn in self.memory_state.turns:
            lines.append(self._generate_turn_section(turn))
        
        # 4. 生成统计
        lines.append(self._generate_statistics())
        
        return "\n".join(lines)
```

**报告特性**：

- 📊 **可视化**: 使用emoji和表格增强可读性
- 📈 **统计**: 提供记忆使用频率和幻觉分布统计
- 🔍 **详细**: 每轮对话的完整分析，包括引用片段
- 📝 **可追溯**: 清晰的记忆ID引用，便于追踪

---

## 📁 项目结构

```
WhatDidYouRemember/
├── WhatDidYouRemember/          # 主包目录
│   ├── __init__.py             # 包初始化
│   ├── analyzer.py             # 🔧 主分析逻辑
│   ├── memory_state.py         # 📦 记忆状态建模
│   ├── hallucination.py        # 🚨 幻觉检测
│   ├── prompt.py               # 💬 Prompt设计
│   ├── report.py               # 📊 报告生成
│   └── cli.py                  # 🖥️  命令行接口
├── examples/                    # 示例文件
│   └── dialogue.json           # 示例对话数据
├── tests/                       # 测试文件（可选）
│   └── test_analyzer.py
├── docs/                        # 文档（可选）
│   └── api.md
├── README.md                    # 📖 项目文档
├── requirements.txt             # 📋 依赖列表
├── setup.py                     # ⚙️  安装配置
└── example_report.md            # 📄 示例报告
```

---

## 🔧 高级用法

### 自定义LLM客户端

```python
class CustomLLMClient:
    """自定义LLM客户端接口"""
    
    def call(self, prompt: str) -> str:
        """
        调用LLM API
        
        Args:
            prompt: 输入的prompt
        
        Returns:
            LLM的回复（JSON格式字符串）
        """
        # 实现你的LLM调用逻辑
        response = your_llm_api_call(prompt)
        return response

# 使用自定义客户端
analyzer = LLMMemoryAnalyzer(llm_client=CustomLLMClient())
```

### 扩展幻觉检测

```python
from WhatDidYouRemember.hallucination import HallucinationDetector, HallucinationType

class CustomHallucinationDetector(HallucinationDetector):
    """扩展的幻觉检测器"""
    
    def detect_custom_pattern(self, llm_response, memories):
        """自定义检测模式"""
        hallucinations = []
        
        # 添加你的检测逻辑
        if self._detect_contradiction(llm_response, memories):
            hallucinations.append(Hallucination(
                type=HallucinationType.WRONG_REFERENCE,
                description="检测到矛盾",
                evidence=llm_response,
                severity=0.8
            ))
        
        return hallucinations
```

### 批量分析

```python
import glob
from pathlib import Path

analyzer = LLMMemoryAnalyzer()

# 批量分析多个对话文件
dialogue_files = glob.glob("dialogues/*.json")
results = []

for file_path in dialogue_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        dialogue_data = json.load(f)
    
    memory_state = analyzer.analyze_dialogue(dialogue_data)
    
    # 生成报告
    report_generator = ReportGenerator(memory_state)
    output_path = f"reports/{Path(file_path).stem}_report.md"
    report_generator.save_report(output_path)
    
    results.append({
        "file": file_path,
        "turns": len(memory_state.turns),
        "memories": len(memory_state.memories),
        "hallucinations": sum(len(t.hallucinations) for t in memory_state.turns)
    })

# 汇总统计
print("批量分析结果:")
for result in results:
    print(f"{result['file']}: {result['hallucinations']} 个幻觉")
```

---

## 🧪 测试

```bash
# 运行测试（如果存在）
python -m pytest tests/

# 测试示例对话
python -m WhatDidYouRemember.cli examples/dialogue.json -o test_report.md
```

---

## 📊 性能考虑

### 分析速度

- **模拟模式**: ~0.1秒/轮次（基于规则）
- **LLM API模式**: ~2-5秒/轮次（取决于API响应时间）

### 内存占用

- **小型对话** (<10轮): ~1MB
- **中型对话** (10-50轮): ~5MB
- **大型对话** (>50轮): ~20MB+

### 优化建议

1. **批量处理**: 对于大量对话，使用批量分析模式
2. **缓存机制**: 缓存LLM API响应（如果支持）
3. **并行处理**: 多线程处理多个对话文件

---

## 🤝 贡献指南

我们欢迎各种形式的贡献！🎉

### 贡献方式

1. **🐛 报告Bug**: 在Issues中报告问题
2. **💡 提出功能**: 分享你的想法和建议
3. **📝 改进文档**: 帮助完善文档
4. **💻 提交代码**: Fork项目，提交Pull Request

### 开发流程

```bash
# 1. Fork项目
# 2. 克隆你的fork
git clone https://github.com/yourusername/WhatDidYouRemember.git

# 3. 创建功能分支
git checkout -b feature/your-feature

# 4. 进行开发
# ... 编写代码 ...

# 5. 提交更改
git commit -m "Add: 新功能描述"

# 6. 推送到你的fork
git push origin feature/your-feature

# 7. 创建Pull Request
```

### 代码规范

- 遵循PEP 8 Python代码规范
- 添加适当的类型注解
- 编写清晰的文档字符串
- 添加单元测试（如果可能）

---

## 📚 相关资源

### 学术论文

- [Long Context Memory in LLMs](https://example.com) - 长上下文记忆研究
- [Hallucination Detection Methods](https://example.com) - 幻觉检测方法

### 相关项目

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用框架
- [LlamaIndex](https://github.com/run-llama/llama_index) - 数据框架

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和研究人员！

特别感谢：
- 🤖 OpenAI、Anthropic等LLM提供商
- 📚 开源社区的支持和反馈
- 🧪 所有测试用户

---

## 👤 作者 (Author)

**Haoze Zheng**

*   🎓 **School**: Xinjiang University (XJU)
*   📧 **Email**: zhenghaoze@stu.xju.edu.cn
*   🐱 **GitHub**: [mire403](https://github.com/mire403)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

<sub>Made by Haoze Zheng. 2026 WhatDidYouRemember.</sub>

</div>



