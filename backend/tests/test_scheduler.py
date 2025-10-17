"""
任务调度器测试
"""
import pytest
import asyncio
import time
from datetime import datetime
from backend.app.utils.scheduler import TaskScheduler


@pytest.fixture
def scheduler():
    """创建调度器实例"""
    scheduler = TaskScheduler()
    yield scheduler
    # 清理
    scheduler.shutdown(wait=False)


# 测试任务计数器
task_counter = {'count': 0}


def sync_test_task():
    """同步测试任务"""
    task_counter['count'] += 1
    print(f"同步任务执行: {task_counter['count']}")


async def async_test_task():
    """异步测试任务"""
    task_counter['count'] += 1
    print(f"异步任务执行: {task_counter['count']}")
    await asyncio.sleep(0.1)


class TestTaskScheduler:
    """任务调度器测试类"""
    
    def test_scheduler_start_stop(self, scheduler):
        """测试启动和停止调度器"""
        # 启动
        scheduler.start()
        assert scheduler.scheduler.running is True
        
        # 停止
        scheduler.shutdown(wait=False)
        assert scheduler.scheduler.running is False
    
    def test_add_interval_task(self, scheduler):
        """测试添加间隔任务"""
        scheduler.start()
        
        # 重置计数器
        task_counter['count'] = 0
        
        # 添加每秒执行的任务
        job = scheduler.add_interval_task(
            'test_interval',
            sync_test_task,
            seconds=1
        )
        
        assert job is not None
        assert 'test_interval' in scheduler.tasks
        
        # 等待任务执行几次
        time.sleep(3.5)
        
        # 应该执行了3-4次
        assert task_counter['count'] >= 3
        assert task_counter['count'] <= 4
    
    def test_add_daily_task(self, scheduler):
        """测试添加每日任务"""
        scheduler.start()
        
        # 获取当前时间的下一分钟
        now = datetime.now()
        next_minute = (now.minute + 1) % 60
        next_hour = now.hour if next_minute > now.minute else (now.hour + 1) % 24
        
        # 添加任务（设置为下一分钟执行）
        job = scheduler.add_daily_task(
            'test_daily',
            sync_test_task,
            hour=next_hour,
            minute=next_minute
        )
        
        assert job is not None
        assert 'test_daily' in scheduler.tasks
        
        # 获取任务信息
        task_info = scheduler.get_task_info('test_daily')
        assert task_info is not None
        assert task_info['id'] == 'test_daily'
    
    def test_remove_task(self, scheduler):
        """测试移除任务"""
        scheduler.start()
        
        # 添加任务
        scheduler.add_interval_task('test_remove', sync_test_task, seconds=1)
        assert 'test_remove' in scheduler.tasks
        
        # 移除任务
        result = scheduler.remove_task('test_remove')
        assert result is True
        assert 'test_remove' not in scheduler.tasks
        
        # 再次移除（应该返回False）
        result = scheduler.remove_task('test_remove')
        assert result is False
    
    def test_pause_resume_task(self, scheduler):
        """测试暂停和恢复任务"""
        scheduler.start()
        task_counter['count'] = 0
        
        # 添加任务
        scheduler.add_interval_task('test_pause', sync_test_task, seconds=1)
        
        # 等待执行几次
        time.sleep(2.5)
        count_before_pause = task_counter['count']
        assert count_before_pause >= 2
        
        # 暂停任务
        scheduler.pause_task('test_pause')
        
        # 等待一段时间
        time.sleep(2)
        
        # 计数不应该增加（或最多增加1次，因为暂停前可能已经开始执行）
        count_after_pause = task_counter['count']
        assert count_after_pause - count_before_pause <= 1
        
        # 恢复任务
        scheduler.resume_task('test_pause')
        
        # 再等待
        time.sleep(2.5)
        
        # 计数应该继续增加
        count_after_resume = task_counter['count']
        assert count_after_resume > count_after_pause
    
    def test_get_task_info(self, scheduler):
        """测试获取任务信息"""
        scheduler.start()
        
        # 添加任务
        scheduler.add_interval_task('test_info', sync_test_task, seconds=10)
        
        # 获取信息
        info = scheduler.get_task_info('test_info')
        
        assert info is not None
        assert info['id'] == 'test_info'
        assert info['name'] == 'test_info'
        assert info['next_run_time'] is not None
        assert 'interval' in info['trigger'].lower()
    
    def test_get_all_tasks(self, scheduler):
        """测试获取所有任务"""
        scheduler.start()
        
        # 添加多个任务
        scheduler.add_interval_task('task1', sync_test_task, seconds=10)
        scheduler.add_interval_task('task2', sync_test_task, seconds=20)
        scheduler.add_interval_task('task3', sync_test_task, seconds=30)
        
        # 获取所有任务
        all_tasks = scheduler.get_all_tasks()
        
        assert len(all_tasks) == 3
        
        task_ids = [task['id'] for task in all_tasks]
        assert 'task1' in task_ids
        assert 'task2' in task_ids
        assert 'task3' in task_ids
    
    def test_execute_now(self, scheduler):
        """测试立即执行任务"""
        scheduler.start()
        task_counter['count'] = 0
        
        # 添加一个长间隔任务（不会自动执行）
        scheduler.add_interval_task('test_execute', sync_test_task, hours=1)
        
        # 应该还没执行
        time.sleep(1)
        assert task_counter['count'] == 0
        
        # 立即执行
        result = scheduler.execute_now('test_execute')
        assert result is True
        
        # 等待执行
        time.sleep(2)
        
        # 应该已执行
        assert task_counter['count'] >= 1
    
    def test_task_with_args(self, scheduler):
        """测试带参数的任务"""
        scheduler.start()
        
        result = {'value': None}
        
        def task_with_args(a, b, c=None):
            result['value'] = f"{a}-{b}-{c}"
        
        # 添加带参数的任务
        scheduler.add_interval_task(
            'test_args',
            task_with_args,
            seconds=1,
            args=('arg1', 'arg2'),
            kwargs={'c': 'arg3'}
        )
        
        # 等待执行
        time.sleep(2)
        
        # 验证参数传递
        assert result['value'] == 'arg1-arg2-arg3'
    
    def test_task_replace_existing(self, scheduler):
        """测试替换已存在的任务"""
        scheduler.start()
        task_counter['count'] = 0
        
        # 添加任务（1秒间隔）
        scheduler.add_interval_task('test_replace', sync_test_task, seconds=1)
        
        time.sleep(2.5)
        count_before = task_counter['count']
        assert count_before >= 2
        
        # 替换任务（10秒间隔）
        scheduler.add_interval_task('test_replace', sync_test_task, seconds=10)
        
        # 等待原来的间隔时间
        time.sleep(2)
        
        # 计数不应该增加太多（因为间隔变长了）
        count_after = task_counter['count']
        assert count_after - count_before <= 1
    
    @pytest.mark.asyncio
    async def test_async_task(self, scheduler):
        """测试异步任务"""
        scheduler.start()
        task_counter['count'] = 0
        
        # 添加异步任务
        scheduler.add_interval_task('test_async', async_test_task, seconds=1)
        
        # 等待执行
        await asyncio.sleep(3.5)
        
        # 应该执行了3-4次
        assert task_counter['count'] >= 3
        assert task_counter['count'] <= 4
    
    def test_max_instances(self, scheduler):
        """测试任务不会并发执行（max_instances=1）"""
        scheduler.start()
        
        execution_times = []
        
        async def slow_task():
            """慢速任务（模拟长时间运行）"""
            execution_times.append(time.time())
            await asyncio.sleep(2)  # 执行需要2秒
        
        # 添加每秒执行的慢速任务
        scheduler.add_interval_task('test_max_instances', slow_task, seconds=1)
        
        # 等待足够长的时间
        time.sleep(5)
        
        # 验证任务没有并发执行
        # 由于每次执行需要2秒，实际执行次数应该少于5次
        assert len(execution_times) <= 3
        
        # 验证执行间隔至少2秒（因为任务执行需要2秒）
        if len(execution_times) >= 2:
            for i in range(1, len(execution_times)):
                interval = execution_times[i] - execution_times[i-1]
                assert interval >= 1.9  # 允许小误差


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
