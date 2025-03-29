import requests
import re
import os
import zipfile
import shutil
import warnings
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json
from datetime import datetime
import hashlib

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# 版本缓存文件路径
CACHE_FILE = "chromedriver_versions_cache.json"

def get_chrome_version():
    """获取本地Chrome浏览器的完整版本号"""
    # 方法1: 通过注册表获取
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        return version  # 返回完整版本号
    except:
        pass
    
    # 方法2: 通过命令行获取
    try:
        import subprocess
        result = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        version = re.search(r'version\s+REG_SZ\s+([\d.]+)', result.stdout)
        if version:
            return version.group(1)
    except:
        pass
    
    # 方法3: 通过浏览器UA获取
    try:
        from selenium import webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)
        version = driver.capabilities['browserVersion']
        driver.quit()
        return version
    except:
        return None

def create_requests_session():
    """创建带重试机制的requests session"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

def load_version_cache():
    """加载版本缓存"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_version_cache(cache):
    """保存版本缓存"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_version_mapping(session):
    """获取版本映射关系"""
    cache = load_version_cache()
    cache_key = "version_mapping"
    
    # 检查缓存是否有效（1天内）
    if cache_key in cache:
        last_updated = datetime.strptime(cache[cache_key]["timestamp"], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_updated).days < 1:
            return cache[cache_key]["data"]
    
    # 从多个源获取版本映射
    sources = [
        "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json",
        "https://registry.npmmirror.com/-/binary/chromedriver/versions.json"
    ]
    
    for url in sources:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 标准化数据结构
                if "versions" in data:  # GitHub格式
                    mapping = {v["version"].split('.')[0]: v["version"] for v in data["versions"]}
                else:  # 镜像源格式
                    mapping = {k.split('.')[0]: k for k in data.keys()}
                
                # 更新缓存
                cache[cache_key] = {
                    "data": mapping,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_version_cache(cache)
                return mapping
        except:
            continue
    
    return cache.get(cache_key, {}).get("data", {})

def get_download_url(chrome_version, session):
    """获取精确的下载URL"""
    # 获取主版本号
    major_version = chrome_version.split('.')[0]
    
    # 获取版本映射
    version_mapping = get_version_mapping(session)
    exact_version = version_mapping.get(major_version)
    
    if not exact_version:
        print(f"无法找到Chrome {chrome_version} 对应的精确版本")
        return None
    
    print(f"找到匹配的精确版本: {exact_version}")
    
    # 尝试多个下载源
    sources = [
        f"https://googlechromelabs.github.io/chrome-for-testing/downloads/{exact_version}/chromedriver-win64.zip",
        f"https://registry.npmmirror.com/-/binary/chromedriver/{exact_version}/chromedriver_win32.zip",
        f"https://chromedriver.storage.googleapis.com/{exact_version}/chromedriver_win32.zip"
    ]
    
    for url in sources:
        try:
            # 检查URL是否有效
            head_resp = session.head(url, timeout=5)
            if head_resp.status_code == 200:
                return url
        except:
            continue
    
    return None

def download_file(url, filename, session):
    """下载文件到本地"""
    try:
        print(f"正在从 {url} 下载...")
        response = session.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 计算文件哈希值用于校验
        hasher = hashlib.sha256()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    hasher.update(chunk)
        
        print(f"下载完成，文件SHA256: {hasher.hexdigest()}")
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def unzip_file(zip_path, extract_to):
    """解压zip文件到指定目录"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 查找chromedriver.exe
            exe_files = [f for f in zip_ref.namelist() if f.endswith('chromedriver.exe') or f.endswith('.exe')]
            if not exe_files:
                raise ValueError("压缩包中未找到可执行文件")
            
            file_in_zip = exe_files[0]
            
            # 解压到临时目录
            temp_dir = os.path.join(extract_to, f"temp_chromedriver_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            os.makedirs(temp_dir, exist_ok=True)
            zip_ref.extractall(temp_dir)
            
            # 移动文件到目标目录
            src_file = os.path.join(temp_dir, file_in_zip)
            dst_file = os.path.join(extract_to, os.path.basename(file_in_zip))
            
            # 如果目标文件已存在，先删除
            if os.path.exists(dst_file):
                os.remove(dst_file)
            
            shutil.move(src_file, extract_to)
            
            # 删除临时目录
            shutil.rmtree(temp_dir)
            
            print(f"文件已解压到: {dst_file}")
            return dst_file
    except Exception as e:
        print(f"解压失败: {str(e)}")
        return None

def download_matching_chromedriver():
    """下载与本地Chrome匹配的ChromeDriver"""
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("无法确定Chrome版本，将尝试下载最新稳定版")
        chrome_version = "LATEST"
    
    print(f"检测到Chrome版本: {chrome_version}")
    
    session = create_requests_session()
    
    # 获取下载URL
    download_url = get_download_url(chrome_version, session)
    
    if not download_url:
        print("\n无法获取下载链接，请尝试以下手动解决方案:")
        print(f"1. 访问 https://chromedriver.chromium.org/downloads")
        print(f"2. 查找与您的Chrome版本 {chrome_version} 匹配的ChromeDriver")
        print("3. 下载适用于Windows的版本")
        print("4. 将下载的chromedriver.exe放在当前目录的上一级目录中")
        return
    
    # 下载文件
    zip_filename = f"chromedriver_{chrome_version.replace('.', '_')}.zip"
    if download_file(download_url, zip_filename, session):
        # 解压到上一级目录
        parent_dir = os.path.dirname(os.path.abspath(os.getcwd()))
        extracted_file = unzip_file(zip_filename, parent_dir)
        
        if extracted_file:
            print(f"\nChromeDriver已成功安装到: {extracted_file}")
            # 删除zip文件
            os.remove(zip_filename)
            
            # 验证文件是否可执行
            try:
                subprocess.run([extracted_file, "--version"], check=True)
                print("ChromeDriver验证成功")
            except:
                print("警告: ChromeDriver验证失败，可能不兼容")
        else:
            print("\n解压失败，请手动解压:")
            print(f"1. 解压 {zip_filename} 到任意目录")
            print("2. 将解压出的chromedriver.exe放在当前目录的上一级目录中")
    else:
        print("\n下载失败，请尝试以下解决方案:")
        print("1. 检查网络连接")
        print("2. 尝试使用VPN或代理")
        print(f"3. 手动下载: {download_url}")

if __name__ == "__main__":
    download_matching_chromedriver()