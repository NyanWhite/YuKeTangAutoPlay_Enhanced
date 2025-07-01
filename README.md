YuKeTangAutoPlay_Enhanced

Based https://github.com/LetMeFly666/YuketangAutoPlayer/ 并进行改进
请使用上方的原项目地址查看配置方法 本Repo只展示对其进行改进的部分所需要的配置项

---

##  改进了什么东西呢？

- [x] 外置无头模式设定 刷课地址与登录使用的Cookie
- [x] 去除ChromeWebDriver的PATH项 现在仅需放在相同目录即可
- [x] 多线程刷课（支持自定线程数）
- [x] （进阶功能）单门课程多线程进行
- [x] 多账号刷课进行
- [x] 获取ChromeWebDriver并下载
  不完全实现 还是建议走原repo的教程
- [x] ~~更优质的睡眠~~
- [x] ChromeDriver的下载器
- [ ] 将部分功能以服务器形式于本地网络开放 以支持远程执行
- [ ] ~~以最大倍速~~

不会Code 基于LLM帮助修改而来 让我们感谢.jpg

---

ParallelAccount用于多账号刷课或是单账号多课程并行

ParallelVideo用于单账号单课程并行 此为实验性 但似乎包含ParallelAccount已有存在功能

***日常使用请选择ParallelAccount***

---

# 环境配置

## 这个是py库的

```python
pip install selenium
```

---

## ChromeDriverInstaller

**下载稳定版**：

```
.\chromedriver-installer.ps1
```

*也可右键以Powershell形式启动 效果是一样的*

**交互式选择版本**：

```
.\chromedriver-installer.ps1 -Version interactive
```

**直接下载测试版**：

```
.\chromedriver-installer.ps1 -Version <type>
```

<Type>中为可更改选项 包含stable bate dev canary

选择符合你的chrome分支的版本下载 在对应的版本后方会显示版本号 可与chrome的版本信息对比

差异过大的话你的chrome很有可能并未更新或是分支错误 单应该会有符合的

默认为stable


---

### 配置方法

Cookie提取请看原repo进行配置 其他的根据这个repo即可

```json
{
    "settings": {
      "max_concurrent": 1114514
//此处是最大线程数(也就是同时进行的课程种类数量_纯数字即可)
//没有上限 最低为1 单个进行目前看来是600-700MB+ 取决于你的电脑水平
//并且注意 视频会放入缓存 请确保你的电脑的%temp%所在分区空间足够
      "headless": true,
//bool值 用于是否显示挂课的窗口 如果确认没问题的话可以将此项打开
      "multi_thread_per_course": true,
//多线程刷单课程开关 本功能和下方功能均为实验性功能 并只用于ParallelVideo.py
//如开启这个请将max_concurrent设置为1以防止不能预料的事情发生
    "threads_per_course": 3
//多线程刷单课程线程数 即为开启数量 与上方max_concurrent的功能是一致的
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
          //如上 并进行略微的修改（如果需要大于4的话）
      }
    ]
  }
```

Notice:这里的Cookie1 2 3 4都可以是相同的 也就是可以以相同或不同的账号进行多个课程的自动进行
