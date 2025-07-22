"""
性能测试
"""

import pytest
import time
import asyncio
from unittest.mock import patch
from utils.data_cleaner import DataCleaner
from ai_analysis.classifier import AIProjectClassifier


class TestPerformance:
    """性能测试类"""
    
    def generate_large_dataset(self, size=1000):
        """生成大型测试数据集"""
        projects = []
        for i in range(size):
            projects.append({
                'name': f'project-{i}',
                'description': f'This is test project {i} for artificial intelligence and machine learning',
                'url': f'https://github.com/user/project-{i}',
                'stars': i * 10,
                'forks': i * 2,
                'language': 'Python' if i % 2 == 0 else 'JavaScript',
                'author': f'user-{i}',
                'tags': ['ai', 'ml', 'test'],
                'source': 'github',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-12-01T00:00:00Z'
            })
        return projects
    
    def test_data_cleaning_performance(self, test_config):
        """测试数据清洗性能"""
        cleaner = DataCleaner(test_config)
        
        # 测试不同大小的数据集
        sizes = [100, 500, 1000]
        
        for size in sizes:
            projects = self.generate_large_dataset(size)
            
            start_time = time.time()
            cleaned = cleaner.clean_and_deduplicate(projects)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            print(f"清洗 {size} 个项目耗时: {processing_time:.2f}秒")
            
            # 性能断言：每个项目处理时间不应超过10ms
            assert processing_time / size < 0.01, f"处理速度过慢: {processing_time/size:.4f}秒/项目"
            
            # 验证结果正确性
            assert len(cleaned) <= size
            assert all('cleaned_at' in project for project in cleaned)
    
    @pytest.mark.asyncio
    async def test_ai_classification_performance(self, test_config):
        """测试AI分类性能"""
        # 使用关键词分类（不需要API调用）
        test_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        classifier = AIProjectClassifier(test_config)
        
        # 测试批量分类性能
        sizes = [50, 100, 200]
        
        for size in sizes:
            projects = self.generate_large_dataset(size)
            
            start_time = time.time()
            results = await classifier.batch_classify(projects)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            print(f"分类 {size} 个项目耗时: {processing_time:.2f}秒")
            
            # 性能断言：每个项目分类时间不应超过50ms（关键词分类）
            assert processing_time / size < 0.05, f"分类速度过慢: {processing_time/size:.4f}秒/项目"
            
            # 验证结果正确性
            assert len(results) == size
            assert all('is_ai_related' in result for result in results)
    
    def test_memory_usage(self, test_config):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 处理大量数据
        cleaner = DataCleaner(test_config)
        large_dataset = self.generate_large_dataset(5000)
        
        cleaned = cleaner.clean_and_deduplicate(large_dataset)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"内存使用增加: {memory_increase:.2f}MB")
        
        # 内存使用不应该过度增长（小于100MB）
        assert memory_increase < 100, f"内存使用过多: {memory_increase:.2f}MB"
        
        # 清理数据，检查内存是否释放
        del large_dataset
        del cleaned
        
        # 强制垃圾回收
        import gc
        gc.collect()
    
    def test_concurrent_processing(self, test_config):
        """测试并发处理性能"""
        import concurrent.futures
        import threading
        
        cleaner = DataCleaner(test_config)
        
        def process_batch(batch_id):
            """处理一批数据"""
            projects = self.generate_large_dataset(100)
            return cleaner.clean_and_deduplicate(projects)
        
        # 测试并发处理
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_batch, i) for i in range(4)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"并发处理4批数据耗时: {processing_time:.2f}秒")
        
        # 验证结果
        assert len(results) == 4
        assert all(len(result) <= 100 for result in results)
        
        # 并发处理应该比串行处理快
        # 这里只是简单验证能够并发执行
        assert processing_time < 10  # 应该在10秒内完成
    
    @pytest.mark.asyncio
    async def test_async_performance(self, test_config):
        """测试异步处理性能"""
        test_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        classifier = AIProjectClassifier(test_config)
        
        projects = self.generate_large_dataset(100)
        
        # 测试串行处理
        start_time = time.time()
        serial_results = []
        for project in projects[:10]:  # 只测试前10个
            result = await classifier.classify(project)
            serial_results.append(result)
        serial_time = time.time() - start_time
        
        # 测试并发处理
        start_time = time.time()
        concurrent_results = await classifier.batch_classify(projects[:10])
        concurrent_time = time.time() - start_time
        
        print(f"串行处理10个项目耗时: {serial_time:.2f}秒")
        print(f"并发处理10个项目耗时: {concurrent_time:.2f}秒")
        
        # 并发处理应该更快（或至少不慢太多）
        assert concurrent_time <= serial_time * 1.5  # 允许一些开销
        
        # 验证结果一致性
        assert len(serial_results) == len(concurrent_results)
    
    def test_large_file_processing(self, test_config, temp_dir):
        """测试大文件处理性能"""
        from utils.storage import DataStorage
        
        storage = DataStorage(test_config)
        
        # 生成大量数据
        large_dataset = self.generate_large_dataset(2000)
        
        # 测试保存性能
        start_time = time.time()
        storage.save_daily_data(large_dataset, '2023-12-01')
        save_time = time.time() - start_time
        
        print(f"保存2000个项目耗时: {save_time:.2f}秒")
        
        # 测试加载性能
        start_time = time.time()
        loaded_data = storage.get_projects_by_date('2023-12-01')
        load_time = time.time() - start_time
        
        print(f"加载2000个项目耗时: {load_time:.2f}秒")
        
        # 性能断言
        assert save_time < 10, f"保存速度过慢: {save_time:.2f}秒"
        assert load_time < 5, f"加载速度过慢: {load_time:.2f}秒"
        
        # 验证数据完整性
        assert len(loaded_data) == len(large_dataset)
    
    def test_chart_generation_performance(self, test_config):
        """测试图表生成性能"""
        from visualization.chart_generator import ChartGenerator
        
        chart_generator = ChartGenerator(test_config)
        
        # 生成测试数据
        projects = self.generate_large_dataset(500)
        
        # 添加必要的分析结果
        for project in projects:
            project.update({
                'ai_classification': {'is_ai_related': True, 'ai_categories': ['ML']},
                'keywords': {'keywords': ['ai', 'ml', 'python']},
                'summary': {'summary': 'Test summary'}
            })
        
        # 测试图表生成性能
        start_time = time.time()
        charts = chart_generator.generate_daily_charts(projects)
        generation_time = time.time() - start_time
        
        print(f"生成图表耗时: {generation_time:.2f}秒")
        
        # 性能断言：图表生成应该在30秒内完成
        assert generation_time < 30, f"图表生成速度过慢: {generation_time:.2f}秒"
        
        # 验证图表生成成功
        assert isinstance(charts, dict)
        assert len(charts) > 0
    
    def test_report_generation_performance(self, test_config):
        """测试报告生成性能"""
        from visualization.report_generator import ReportGenerator
        
        test_config['api']['openai']['api_key'] = '${OPENAI_API_KEY}'
        report_generator = ReportGenerator(test_config)
        
        # 生成测试数据
        projects = self.generate_large_dataset(200)
        
        # 添加必要的分析结果
        for project in projects:
            project.update({
                'ai_classification': {'is_ai_related': True, 'ai_categories': ['ML']},
                'keywords': {'keywords': ['ai', 'ml', 'python']},
                'summary': {'summary': 'Test summary', 'highlights': [], 'use_cases': []}
            })
        
        # 测试报告生成性能
        async def test_report():
            start_time = time.time()
            report = await report_generator.generate_daily_report(projects, {})
            generation_time = time.time() - start_time
            
            print(f"生成报告耗时: {generation_time:.2f}秒")
            
            # 性能断言：报告生成应该在20秒内完成
            assert generation_time < 20, f"报告生成速度过慢: {generation_time:.2f}秒"
            
            # 验证报告生成成功
            assert 'html' in report
            assert 'markdown' in report
            assert len(report['html']) > 1000
        
        # 运行异步测试
        asyncio.run(test_report())
