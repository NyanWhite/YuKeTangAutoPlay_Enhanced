'''
Author: LetMeFly
Date: 2023-09-12 20:49:21
Modifier:NyanWhite
Description: 开源于https://github.com/LetMeFly666/YuketangAutoPlayer 欢迎issue、PR
后续改进版 https://github.com/NyanWhite/YuketangAutoPlay_Enhanced
感谢支持w
'''
import os
import json 
import threading
import queue
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from time import sleep
import random

class VideoThread(threading.Thread):
    """单个视频线程类"""
    def __init__(self, video_queue, course_url, cookie, headless, thread_id):
        threading.Thread.__init__(self)
        self.video_queue = video_queue
        self.course_url = course_url
        self.cookie = cookie
        self.headless = headless
        self.thread_id = thread_id
        self.driver = None
        self.IMPLICITLY_WAIT = 10
        self.IS_COMMOONUI = False
    
    def run(self):
        try:
            self._setup_driver()
            while not self.video_queue.empty():
                try:
                    video = self.video_queue.get_nowait()
                    self._play_video(video)
                    self.video_queue.task_done()
                except queue.Empty:
                    break
        finally:
            if self.driver:
                self.driver.quit()
    
    def _setup_driver(self):
        """设置浏览器驱动"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_dir, 'chromedriver.exe' if os.name == 'nt' else 'chromedriver')
        
        option = webdriver.ChromeOptions()
        if self.headless:
            option.add_argument('--headless')
        
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=option)
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.IMPLICITLY_WAIT)
        
        homePageURL = 'https://' + self.course_url.split('https://')[1].split('/')[0] + '/'
        if 'www.yuketang.cn' in homePageURL:
            self.IS_COMMOONUI = True
        
        self.driver.get(homePageURL)
        self.setCookie({'sessionid': self.cookie})
        print(f"[线程{self.thread_id}] 登录完成，准备播放视频")
    
    def setCookie(self, cookies):
        self.driver.delete_all_cookies()
        for name, value in cookies.items():
            self.driver.add_cookie({'name': name, 'value': value, 'path': '/'})
    
    def _play_video(self, video_element):
        """播放单个视频"""
        try:
            # 在新标签页打开视频
            video_url = video_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            self.driver.execute_script(f"window.open('{video_url}');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            print(f"[线程{self.thread_id}] 正在播放视频: {video_url}")
            WebDriverWait(self.driver, 10).until(lambda x: self.driver.execute_script('video = document.querySelector("video"); return video;'))
            
            # 设置视频播放逻辑
            self.driver.execute_script('''
                videoPlay = setInterval(function() {
                    if (video.paused) { video.play(); }
                }, 200);
                setTimeout(() => clearInterval(videoPlay), 5000);
                
                addFinishMark = function() {
                    finished = document.createElement("span");
                    finished.setAttribute("id", "LetMeFly_Finished");
                    document.body.appendChild(finished);
                };
                
                lastDuration = 0;
                setInterval(() => {
                    nowDuration = video.currentTime;
                    if (nowDuration < lastDuration) { addFinishMark(); }
                    lastDuration = nowDuration;
                }, 200);
                
                video.addEventListener("pause", () => { video.play() });
            ''')
            
            # 静音和倍速设置
            self._mute_video()
            self._change_speed()
            
            # 等待视频播放完成
            while True:
                if self.driver.execute_script('return document.querySelector("#LetMeFly_Finished");'):
                    print(f"[线程{self.thread_id}] 视频播放完成")
                    sleep(5)
                    break
                else:
                    sleep(3)
        except Exception as e:
            print(f"[线程{self.thread_id}] 播放视频出错: {str(e)}")
        finally:
            # 关闭当前标签页并切换回主窗口
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
    
    def _mute_video(self):
        """静音视频"""
        try:
            if self.driver.execute_script('return video.muted;'):
                return
            voice = self.driver.find_element(By.TAG_NAME, 'xt-volumebutton')
            ActionChains(self.driver).move_to_element(voice).click().perform()
        except:
            pass
    
    def _change_speed(self):
        """设置2倍速"""
        try:
            speedbutton = self.driver.find_element(By.TAG_NAME, 'xt-speedbutton')
            ActionChains(self.driver).move_to_element(speedbutton).perform()
            ul = speedbutton.find_element(By.TAG_NAME, 'ul')
            lis = ul.find_elements(By.TAG_NAME, 'li')
            li_speed2 = lis[0]
            ActionChains(self.driver).move_to_element(li_speed2).click().perform()
        except:
            pass

class YuketangPlayer(threading.Thread):
    def __init__(self, course_url, cookie, headless=False, multi_thread=False, max_threads=3):
        threading.Thread.__init__(self)
        self.course_url = course_url
        self.cookie = cookie
        self.IF_HEADLESS = headless
        self.MULTI_THREAD = multi_thread  # 是否启用单课程多线程
        self.MAX_THREADS = max_threads    # 单课程最大线程数
        self.driver = None
        self.IMPLICITLY_WAIT = 10
        self.IS_COMMOONUI = False
    
    def run(self):
        try:
            self._setup_driver()
            if self.MULTI_THREAD:
                self._play_videos_parallel()
            else:
                self._play_videos_sequential()
        finally:
            if self.driver:
                self.driver.quit()
    
    def _setup_driver(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_dir, 'chromedriver.exe' if os.name == 'nt' else 'chromedriver')
        
        option = webdriver.ChromeOptions()
        if self.IF_HEADLESS:
            option.add_argument('--headless')
        
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=option)
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.IMPLICITLY_WAIT)
        
        homePageURL = 'https://' + self.course_url.split('https://')[1].split('/')[0] + '/'
        if 'www.yuketang.cn' in homePageURL:
            self.IS_COMMOONUI = True
        
        self.driver.get(homePageURL)
        self.setCookie({'sessionid': self.cookie})
        self.driver.get(self.course_url)
        sleep(3)
        
        if 'pro/portal/home' in self.driver.current_url:
            print(f'[{self.course_url}] cookie失效或设置有误，请重设cookie或选择每次扫码登录')
            self.driver.get(homePageURL)
            self.driver.find_element(By.CLASS_NAME, 'login-btn').click()
            print(f"[{self.course_url}] 请扫码登录")
            while 'courselist' not in self.driver.current_url:
                sleep(0.5)
            print(f'[{self.course_url}] 登录成功')
            self.driver.get(self.course_url)
    
    def setCookie(self, cookies):
        self.driver.delete_all_cookies()
        for name, value in cookies.items():
            self.driver.add_cookie({'name': name, 'value': value, 'path': '/'})
    
    def ifVideo(self, div):
        for i in div.find_elements(By.TAG_NAME, 'i'):
            i_class = i.get_attribute('class')
            if 'icon--suo' in i_class:
                return False
        try:
            i = div.find_element(By.TAG_NAME, 'i')
        except:
            return False
        i_class = i.get_attribute('class')
        return 'icon--shipin' in i_class
    
    def getAllvideos_notFinished(self):
        """获取所有未完成的视频元素"""
        if self.IS_COMMOONUI:
            scoreList = self.driver.find_element(By.ID, 'tab-student_school_report')
            scoreList.click()
            allClasses = self.driver.find_elements(By.CLASS_NAME, 'study-unit')
        else:
            allClasses = self.driver.find_elements(By.CLASS_NAME, 'leaf-detail')
        
        print(f'[{self.course_url}] 正在寻找未完成的视频，请耐心等待')
        self.driver.implicitly_wait(0.1)
        allVideos = []
        for thisClass in allClasses:
            if self.ifVideo(thisClass) and '已完成' not in thisClass.text:
                allVideos.append(thisClass)
        self.driver.implicitly_wait(self.IMPLICITLY_WAIT)
        return allVideos
    
    def _play_videos_sequential(self):
        """顺序播放视频（原逻辑）"""
        while self._finish_one_video():
            self.driver.refresh()
        print(f'[{self.course_url}] 恭喜你！全部播放完毕')
    
    def _play_videos_parallel(self):
        """并行播放视频（新功能）"""
        # 获取所有未完成的视频
        all_videos = self.getAllvideos_notFinished()
        if not all_videos:
            print(f"[{self.course_url}] 没有找到未完成的视频")
            return
        
        print(f"[{self.course_url}] 找到 {len(all_videos)} 个未完成视频，开始多线程播放")
        
        # 创建视频队列
        video_queue = queue.Queue()
        for video in all_videos:
            video_queue.put(video)
        
        # 创建并启动视频线程
        threads = []
        for i in range(min(self.MAX_THREADS, len(all_videos))):
            thread = VideoThread(
                video_queue=video_queue,
                course_url=self.course_url,
                cookie=self.cookie,
                headless=self.IF_HEADLESS,
                thread_id=i+1
            )
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        print(f"[{self.course_url}] 所有视频播放完成！")
    
    def _finish_one_video(self):
        """完成一个视频（原逻辑）"""
        all_videos = self.getAllvideos_notFinished()
        if not all_videos:
            return False
        
        video = all_videos[0]
        self.driver.execute_script('arguments[0].scrollIntoView(false);', video)
        if self.IS_COMMOONUI:
            span = video.find_element(By.TAG_NAME, 'span')
            span.click()
        else:
            video.click()
        
        print(f'[{self.course_url}] 正在播放')
        self.driver.switch_to.window(self.driver.window_handles[-1])
        WebDriverWait(self.driver, 10).until(lambda x: self.driver.execute_script('video = document.querySelector("video"); return video;'))
        
        self.driver.execute_script('''
            videoPlay = setInterval(function() {
                if (video.paused) { video.play(); }
            }, 200);
            setTimeout(() => clearInterval(videoPlay), 5000);
            
            addFinishMark = function() {
                finished = document.createElement("span");
                finished.setAttribute("id", "LetMeFly_Finished");
                document.body.appendChild(finished);
            };
            
            lastDuration = 0;
            setInterval(() => {
                nowDuration = video.currentTime;
                if (nowDuration < lastDuration) { addFinishMark(); }
                lastDuration = nowDuration;
            }, 200);
            
            video.addEventListener("pause", () => { video.play() });
        ''')
        
        self._mute_video()
        self._change_speed()
        
        while True:
            if self.driver.execute_script('return document.querySelector("#LetMeFly_Finished");'):
                print(f'[{self.course_url}] finished, wait 5s')
                sleep(5)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                return True
            else:
                print(f'[{self.course_url}] 正在播放视频 | 随机数: {random.random()}')
                sleep(3)
        return False
    
    def _mute_video(self):
        """静音视频"""
        if self.driver.execute_script('return video.muted;'):
            return
        voice = self.driver.find_element(By.TAG_NAME, 'xt-volumebutton')
        ActionChains(self.driver).move_to_element(voice).perform()
        ActionChains(self.driver).click().perform()
    
    def _change_speed(self):
        """设置2倍速"""
        speedbutton = self.driver.find_element(By.TAG_NAME, 'xt-speedbutton')
        ActionChains(self.driver).move_to_element(speedbutton).perform()
        ul = speedbutton.find_element(By.TAG_NAME, 'ul')
        lis = ul.find_elements(By.TAG_NAME, 'li')
        li_speed2 = lis[0]
        diffY = speedbutton.location['y'] - li_speed2.location['y']
        for i in range(diffY // 10):
            ActionChains(self.driver).move_by_offset(0, -10).perform()
            sleep(0.5)
        sleep(0.8)
        ActionChains(self.driver).click().perform()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：未找到配置文件 {config_path}")
        exit(1)
    except json.JSONDecodeError:
        print(f"错误：配置文件 {config_path} 格式不正确")
        exit(1)