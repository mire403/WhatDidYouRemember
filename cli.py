"""命令行接口模块"""

import argparse
import json
import os
import sys
from pathlib import Path
from .analyzer import LLMMemoryAnalyzer
from .report import ReportGenerator


def load_dialogue(filepath: str) -> dict:
    """加载对话JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"错误: 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="WhatDidYouRemember - LLM记忆分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s examples/dialogue.json
  %(prog)s examples/dialogue.json --output report.md
  %(prog)s examples/dialogue.json --llm-api openai --api-key YOUR_KEY
        """
    )
    
    parser.add_argument(
        "dialogue_file",
        help="对话JSON文件路径"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="memory_report.md",
        help="输出报告文件路径 (默认: memory_report.md)"
    )
    
    parser.add_argument(
        "--llm-api",
        choices=["openai", "anthropic", "local"],
        help="使用的LLM API (默认: 使用模拟分析)"
    )
    
    parser.add_argument(
        "--api-key",
        help="LLM API密钥"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="使用的模型名称 (默认: gpt-4)"
    )
    
    args = parser.parse_args()
    
    # 加载对话数据
    print(f"📖 加载对话文件: {args.dialogue_file}")
    dialogue_data = load_dialogue(args.dialogue_file)
    
    # 初始化LLM客户端（如果需要）
    llm_client = None
    if args.llm_api:
        llm_client = create_llm_client(args.llm_api, args.api_key, args.model)
        if not llm_client:
            print("⚠️  警告: LLM客户端初始化失败，使用模拟分析", file=sys.stderr)
    
    # 创建分析器
    print("🔍 开始分析对话...")
    analyzer = LLMMemoryAnalyzer(llm_client=llm_client)
    
    # 执行分析
    memory_state = analyzer.analyze_dialogue(dialogue_data)
    
    # 生成报告
    print("📝 生成报告...")
    report_generator = ReportGenerator(memory_state)
    report_generator.save_report(args.output)
    
    print(f"✅ 分析完成！报告已保存到: {args.output}")
    
    # 打印简要统计
    total_turns = len(memory_state.turns)
    total_memories = len(memory_state.memories)
    total_hallucinations = sum(len(t.hallucinations) for t in memory_state.turns)
    
    print(f"\n📊 统计信息:")
    print(f"  - 总轮次数: {total_turns}")
    print(f"  - 总记忆项: {total_memories}")
    print(f"  - 幻觉总数: {total_hallucinations}")


def create_llm_client(api_type: str, api_key: str = None, model: str = "gpt-4"):
    """创建LLM客户端"""
    if api_type == "openai":
        try:
            import openai
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("错误: 需要提供OpenAI API密钥", file=sys.stderr)
                return None
            
            class OpenAIClient:
                def __init__(self, api_key, model):
                    openai.api_key = api_key
                    self.model = model
                
                def call(self, prompt):
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    return response.choices[0].message.content
            
            return OpenAIClient(api_key, model)
        except ImportError:
            print("错误: 需要安装openai库: pip install openai", file=sys.stderr)
            return None
    
    elif api_type == "anthropic":
        try:
            import anthropic
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("错误: 需要提供Anthropic API密钥", file=sys.stderr)
                return None
            
            class AnthropicClient:
                def __init__(self, api_key, model):
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.model = model
                
                def call(self, prompt):
                    message = self.client.messages.create(
                        model=self.model,
                        max_tokens=4096,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return message.content[0].text
            
            return AnthropicClient(api_key, model)
        except ImportError:
            print("错误: 需要安装anthropic库: pip install anthropic", file=sys.stderr)
            return None
    
    elif api_type == "local":
        # 本地模型客户端示例（需要根据实际情况实现）
        print("警告: 本地模型客户端需要自定义实现", file=sys.stderr)
        return None
    
    return None


if __name__ == "__main__":
    main()
