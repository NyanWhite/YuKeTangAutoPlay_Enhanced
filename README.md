# YuKeTangAutoPlay_Enhanced
Based https://github.com/LetMeFly666/YuketangAutoPlayer/ 并进行改进
请使用上方的原项目地址查看配置方法 本Repo只展示对其进行改进的部分所需要的配置项

---

##  改进了什么东西呢？

- [x] 外置无头模式设定 刷课地址与登录使用的Cookie

- [x] 去除ChromeWebDriver的PATH项 现在仅需放在相同目录即可

- [x] 多线程刷课（支持自定线程数）

  *但不能用在同一个课程上 这会导致所有行为都只指向同一个视频*

- [x] 多账号刷课进行
  
  不是哥们可以这样？ 关于这条请看下方的config.json配置
  
- [x] 获取ChromeWebDriver并下载
  不完全实现 还是建议走原repo的教程

- [x] ~~更优质的睡眠~~

不会Code 基于LLM帮助修改而来 让我们感谢.jpg

---

由于被改的莫名其妙的所以现在只要运行Controller.py即可 但yuketang.py还能不能用得上暂且未知（）
先放着

---

## Python环境配置

```python
pip install selenium requests urllib3 tqdm
```

如果已经有WebDriver在当前目录下的话后三者就不用装了（

---

### 配置方法

Cookie请看原repo进行配置 其他的根据这个repo即可

```json
{
    "settings": {
      "max_concurrent": 此处是最大线程数(也就是同时进行的课程种类数量_纯数字即可),
      "headless": 无头模式的启用与否_正常运行的话就可以开启了(false/true)
    },
    "courses": [
      {
        "url": "课程种类1的链接",
        "cookie": "Cookie1"
      },
      {
        "url": "课程种类2的链接",
        "cookie": "Cookie2"
      },
      {
        "url": "课程种类3的链接",
        "cookie": "Cookie3"
      },
      {
        "url": "课程种类4的链接",
        "cookie": "Cookie4"
      },
      {
       如上 并进行略微的修改（如果需要大于4的话）
      }
    ]
  }
```

Notice:这里的Cookie1 2 3 4都可以是相同的 也就是可以以相同或不同的账号进行多个课程的自动进行

---

本人不对这个奇异玩意作任何解释说明 反正能跑就行（）
its works fine on my pc()
