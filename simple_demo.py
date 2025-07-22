#!/usr/bin/env python3
"""
AI爆款项目雷达 - 简化演示脚本
避免复杂依赖，展示核心功能
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

def create_demo_data():
    """创建演示数据"""
    return [
        {
            'name': 'awesome-ai-chatbot',
            'description': 'An advanced AI chatbot powered by large language models and natural language processing',
            'url': 'https://github.com/demo/awesome-ai-chatbot',
            'stars': 2500,
            'forks': 450,
            'language': 'Python',
            'author': 'ai-researcher',
            'tags': ['ai', 'chatbot', 'nlp', 'llm'],
            'source': 'github',
            'created_at': '2023-01-15T10:00:00Z',
            'updated_at': '2023-12-01T15:30:00Z'
        },
        {
            'name': 'ml-vision-toolkit',
            'description': 'A comprehensive computer vision toolkit for machine learning with deep learning models',
            'url': 'https://github.com/demo/ml-vision-toolkit',
            'stars': 1800,
            'forks': 320,
            'language': 'Python',
            'author': 'vision-lab',
            'tags': ['machine-learning', 'computer-vision', 'deep-learning'],
            'source': 'github',
            'created_at': '2023-03-20T14:00:00Z',
            'updated_at': '2023-11-28T09:15:00Z'
        },
        {
            'name': 'simple-web-app',
            'description': 'A simple web application for managing tasks and projects',
            'url': 'https://github.com/demo/simple-web-app',
            'stars': 45,
            'forks': 12,
            'language': 'JavaScript',
            'author': 'web-dev',
            'tags': ['web', 'app', 'productivity'],
            'source': 'github',
            'created_at': '2023-08-15T09:00:00Z',
            'updated_at': '2023-11-25T14:30:00Z'
        }
    ]


def test_basic_imports():
    """测试基础模块导入"""
    print("🔧 测试模块导入...")
    
    try:
        from utils.config import load_config
        print("✅ 配置模块导入成功")
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False
    
    try:
        from utils.data_cleaner import DataCleaner
        print("✅ 数据清洗模块导入成功")
    except Exception as e:
        print(f"❌ 数据清洗模块导入失败: {e}")
        return False
    
    return True


def test_data_cleaning():
    """测试数据清洗功能"""
    print("\n🧹 测试数据清洗...")
    
    try:
        from utils.config import load_config
        from utils.data_cleaner import DataCleaner
        
        # 加载配置
        config = load_config()
        
        # 创建数据清洗器
        cleaner = DataCleaner(config)
        
        # 创建测试数据
        demo_data = create_demo_data()
        
        # 执行清洗
        cleaned_data = cleaner.clean_and_deduplicate(demo_data)
        
        print(f"✅ 数据清洗成功: {len(demo_data)} -> {len(cleaned_data)} 项目")
        
        return cleaned_data
        
    except Exception as e:
        print(f"❌ 数据清洗失败: {e}")
        return []


def test_ai_classification():
    """测试AI分类功能（关键词模式）"""
    print("\n🤖 测试AI分类...")
    
    try:
        from utils.config import load_config
        from ai_analysis.classifier import AIProjectClassifier
        
        # 加载配置（不使用API）
        config = load_config()
        config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'  # 强制使用关键词模式
        
        # 创建分类器
        classifier = AIProjectClassifier(config)
        
        # 测试数据
        demo_data = create_demo_data()
        
        ai_projects = []
        for project in demo_data:
            # 使用关键词分类
            result = classifier._classify_by_keywords(project)
            
            if result['is_ai_related']:
                project['ai_classification'] = result
                ai_projects.append(project)
                print(f"   ✅ {project['name']} - AI相关 (置信度: {result['confidence_score']:.2f})")
            else:
                print(f"   ❌ {project['name']} - 非AI项目")
        
        print(f"✅ AI分类完成: 发现 {len(ai_projects)} 个AI项目")
        return ai_projects
        
    except Exception as e:
        print(f"❌ AI分类失败: {e}")
        return []


def generate_simple_report(projects):
    """生成简单的文本报告"""
    print("\n📝 生成简单报告...")
    
    try:
        # 创建输出目录
        output_dir = Path("output/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成报告内容
        today = datetime.now().strftime("%Y-%m-%d")
        report_content = f"""# AI项目趋势报告 - {today}

## 概览
- 总项目数: {len(projects)}
- AI项目数: {len([p for p in projects if p.get('ai_classification', {}).get('is_ai_related', False)])}
- 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## AI项目列表

"""
        
        ai_projects = [p for p in projects if p.get('ai_classification', {}).get('is_ai_related', False)]
        
        for i, project in enumerate(ai_projects, 1):
            classification = project.get('ai_classification', {})
            confidence = classification.get('confidence_score', 0)
            
            report_content += f"""### {i}. {project['name']}

- **描述**: {project['description']}
- **URL**: {project['url']}
- **星标数**: {project['stars']}
- **编程语言**: {project['language']}
- **AI置信度**: {confidence:.2f}
- **标签**: {', '.join(project['tags'])}

---

"""
        
        # 保存报告
        report_path = output_dir / f"simple-demo-report-{today}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 报告生成成功: {report_path}")
        
        # 也保存JSON格式
        json_path = output_dir / f"simple-demo-data-{today}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据保存成功: {json_path}")
        
        return str(report_path)
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        return None


def main():
    """主函数"""
    print("🚀 AI爆款项目雷达 - 简化演示")
    print("=" * 40)
    print("这个演示展示核心功能，不依赖复杂的可视化库")
    print()
    
    # 1. 测试基础导入
    if not test_basic_imports():
        print("\n❌ 基础模块导入失败，请检查安装")
        return
    
    # 2. 测试数据清洗
    cleaned_data = test_data_cleaning()
    if not cleaned_data:
        print("\n❌ 数据清洗失败")
        return
    
    # 3. 测试AI分类
    ai_projects = test_ai_classification()
    
    # 4. 将AI分类结果合并到清洗数据中
    for project in cleaned_data:
        for ai_project in ai_projects:
            if project['name'] == ai_project['name']:
                project['ai_classification'] = ai_project['ai_classification']
                break

    # 5. 生成报告
    report_path = generate_simple_report(cleaned_data)
    
    # 5. 显示结果
    print("\n📋 演示结果")
    print("=" * 30)
    print(f"原始项目数: {len(create_demo_data())}")
    print(f"清洗后项目数: {len(cleaned_data)}")
    print(f"AI项目数: {len(ai_projects)}")
    
    if ai_projects:
        print("\n🏆 发现的AI项目:")
        for i, project in enumerate(ai_projects, 1):
            classification = project.get('ai_classification', {})
            confidence = classification.get('confidence_score', 0)
            print(f"   {i}. {project['name']} (置信度: {confidence:.2f})")
    
    if report_path:
        print(f"\n📄 报告文件: {report_path}")
    
    print("\n🎉 简化演示完成！")
    print("\n💡 下一步:")
    print("1. 设置OpenAI API密钥获得更好的AI分析")
    print("2. 安装完整依赖运行完整版本: python demo.py")
    print("3. 执行真实爬取: python main.py --mode daily")


if __name__ == "__main__":
    main()
