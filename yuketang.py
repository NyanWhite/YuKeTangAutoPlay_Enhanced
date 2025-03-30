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
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from time import sleep
import random

class YuketangPlayer(threading.Thread):
    def __init__(self, course_url, cookie, headless=False):
        threading.Thread.__init__(self)
        self.course_url = course_url
        self.cookie = cookie
        self.IF_HEADLESS = headless
        self.driver = None
        self.IMPLICITLY_WAIT = 10
        self.IS_COMMOONUI = False
    
    def run(self):
        try:
            self._setup_driver()
            self._play_videos()
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
    
    def getAllvideos_notFinished(self, allClasses):
        self.driver.implicitly_wait(0.1)
        allVideos = []
        for thisClass in allClasses:
            if self.ifVideo(thisClass) and '已完成' not in thisClass.text:
                allVideos.append(thisClass)
        self.driver.implicitly_wait(self.IMPLICITLY_WAIT)
        return allVideos
    
    def get1video_notFinished(self, allClasses):
        for thisClass in allClasses:
            if self.ifVideo(thisClass) and '已完成' not in thisClass.text:
                return thisClass
        return None
    
    def change2speed2(self):
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
    
    def mute1video(self):
        if self.driver.execute_script('return video.muted;'):
            return
        voice = self.driver.find_element(By.TAG_NAME, 'xt-volumebutton')
        ActionChains(self.driver).move_to_element(voice).perform()
        ActionChains(self.driver).click().perform()
    
    def finish1video(self):
        if self.IS_COMMOONUI:
            scoreList = self.driver.find_element(By.ID, 'tab-student_school_report')
            scoreList.click()
            allClasses = self.driver.find_elements(By.CLASS_NAME, 'study-unit')
        else:
            allClasses = self.driver.find_elements(By.CLASS_NAME, 'leaf-detail')
        
        print(f'[{self.course_url}] 正在寻找未完成的视频，请耐心等待')
        allVideos = self.getAllvideos_notFinished(allClasses)
        if not allVideos:
            return False
        
        video = allVideos[0]
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
        
        self.mute1video()
        self.change2speed2()
        
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
    
    def _play_videos(self):
        while self.finish1video():
            self.driver.refresh()
        print(f'[{self.course_url}] 恭喜你！全部播放完毕')

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