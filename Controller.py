'''
Author: LetMeFly
Date: 2023-09-12 20:49:21
Modifier:NyanWhite
Description: 开源于https://github.com/LetMeFly666/YuketangAutoPlayer 欢迎issue、PR
后续改进版 https://github.com/NyanWhite/YuketangAutoPlay_Enhanced
感谢支持w
'''
import os
import threading
import time
from yuketang import YuketangPlayer, load_config

def main():
    # 加载配置
    config = load_config()
    settings = config.get('settings', {})
    courses = config.get('courses', [])
    
    max_concurrent = settings.get('max_concurrent', 3)
    headless = settings.get('headless', True)
    
    print(f"配置加载完成，最大并发数: {max_concurrent}, 无头模式: {headless}")
    print(f"共找到 {len(courses)} 个课程")
    
    # 创建并启动线程
    active_threads = []
    
    for course in courses:
        # 等待有空闲线程槽位
        while len(active_threads) >= max_concurrent:
            # 移除已完成的线程
            active_threads = [t for t in active_threads if t.is_alive()]
            if len(active_threads) >= max_concurrent:
                print(f"当前活跃线程数: {len(active_threads)}，等待空闲槽位...")
                time.sleep(5)
        
        # 启动新线程
        print(f"正在启动课程: {course['url']}")
        player = YuketangPlayer(course['url'], course['cookie'], headless=headless)
        player.start()
        active_threads.append(player)
        time.sleep(1)  # 避免同时启动造成资源竞争
    
    # 等待所有线程完成
    print("所有课程已启动，等待完成...")
    while active_threads:
        active_threads = [t for t in active_threads if t.is_alive()]
        if active_threads:
            print(f"剩余活跃课程: {len(active_threads)}")
            time.sleep(10)
    
    print("所有课程已完成！")

if __name__ == '__main__':
    main()
