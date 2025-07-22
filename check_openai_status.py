#!/usr/bin/env python3
"""
OpenAI API状态检查脚本
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI


async def check_api_status():
    """检查OpenAI API状态"""
    print("🔍 OpenAI API状态检查")
    print("=" * 40)
    
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY环境变量")
        return False
    
    print(f"✅ API密钥已设置: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # 创建客户端
        client = AsyncOpenAI(api_key=api_key)
        
        print("\n🔧 测试API连接...")
        
        # 测试简单的API调用
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, this is a test. Please respond with 'API working'."}
            ],
            max_tokens=10
        )
        
        print("✅ API调用成功！")
        print(f"响应: {response.choices[0].message.content}")
        
        return True
        
    except openai.RateLimitError as e:
        print(f"❌ 速率限制错误: {e}")
        print("💡 可能原因:")
        print("   - 请求过于频繁")
        print("   - 达到每分钟请求限制")
        print("   - 建议等待一段时间后重试")
        return False
        
    except openai.AuthenticationError as e:
        print(f"❌ 认证错误: {e}")
        print("💡 可能原因:")
        print("   - API密钥无效")
        print("   - API密钥已过期")
        print("   - 请检查密钥是否正确")
        return False
        
    except openai.PermissionDeniedError as e:
        print(f"❌ 权限错误: {e}")
        print("💡 可能原因:")
        print("   - 账户没有访问该模型的权限")
        print("   - 需要升级账户计划")
        return False
        
    except openai.BadRequestError as e:
        print(f"❌ 请求错误: {e}")
        print("💡 可能原因:")
        print("   - 请求参数有误")
        print("   - 模型名称错误")
        return False
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ API调用失败: {error_str}")
        
        if "insufficient_quota" in error_str:
            print("\n💳 配额不足问题:")
            print("   - 您的OpenAI账户余额不足")
            print("   - 需要充值或升级计划")
            print("   - 免费账户有使用限制")
            print("\n🔗 解决方案:")
            print("   1. 访问 https://platform.openai.com/account/billing")
            print("   2. 检查账户余额和使用情况")
            print("   3. 添加付费方式或充值")
            print("   4. 或者使用关键词分析模式（无需API）")
            
        elif "quota" in error_str:
            print("\n📊 配额相关问题:")
            print("   - 可能是免费配额已用完")
            print("   - 或者达到了计费限制")
            print("   - 检查账户设置中的使用限制")
            
        return False


async def check_account_info():
    """检查账户信息"""
    print("\n📊 尝试获取账户信息...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return
    
    try:
        # 注意：OpenAI API v1 不再提供账户余额查询接口
        # 这里只能通过尝试调用来判断状态
        print("ℹ️  OpenAI API v1 不提供余额查询接口")
        print("   请访问 https://platform.openai.com/account/usage 查看使用情况")
        print("   请访问 https://platform.openai.com/account/billing 查看账单信息")
        
    except Exception as e:
        print(f"⚠️  无法获取账户信息: {e}")


def print_solutions():
    """打印解决方案"""
    print("\n💡 解决方案:")
    print("=" * 40)
    
    print("🔄 如果遇到配额问题:")
    print("   1. 检查账户余额: https://platform.openai.com/account/billing")
    print("   2. 查看使用情况: https://platform.openai.com/account/usage")
    print("   3. 添加付费方式或充值")
    print("   4. 检查使用限制设置")
    
    print("\n🆓 免费替代方案:")
    print("   1. 使用关键词分析模式（推荐）:")
    print("      python3 run_no_api.py")
    print("   2. 清空API密钥使用本地分析:")
    print("      # 在 .env 文件中注释掉 OPENAI_API_KEY")
    print("   3. 使用其他免费AI服务")
    
    print("\n⚙️  配置建议:")
    print("   1. 降低API调用频率")
    print("   2. 减少max_tokens参数")
    print("   3. 使用更便宜的模型（如gpt-3.5-turbo）")
    print("   4. 批量处理减少API调用次数")


async def main():
    """主函数"""
    success = await check_api_status()
    
    if not success:
        await check_account_info()
        print_solutions()
    else:
        print("\n🎉 API状态正常，可以正常使用！")
        print("💡 建议:")
        print("   - 监控API使用量避免超出配额")
        print("   - 设置合理的使用限制")
        print("   - 考虑使用缓存减少重复调用")


if __name__ == "__main__":
    asyncio.run(main())
