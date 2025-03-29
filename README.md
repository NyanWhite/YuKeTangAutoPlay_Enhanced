# YuKeTangAutoPlay_Enhanced
Based https://github.com/LetMeFly666/YuketangAutoPlayer/ 并进行改进
请使用上方的原项目地址查看配置方法 本Repo只展示对其进行改进的部分所需要的配置项

---

##  改进了什么东西呢？

- [x] 外置刷课地址与登录使用的Cooke
- [x] 去除ChromeWebDriver的PATH项 现在仅需放在相同目录即可
- [ ] 并行刷课（多课程同时
- [x] 获取ChromeWebDriver并下载
  不完全实现 还是建议走原repo的教程

- [x] ~~更优质的睡眠~~

不会Code 基于LLM帮助修改而来 让我们感谢.jpg

---

## Python环境配置

```python
pip install selenium requests urllib3 tqdm
```

如果已经有WebDriver在当前目录下的话后三者就不用装了（

---

### 配置方法

仅需修改其中的config.json 填入指向的课程地址和Cookie即可
Cookie也可不填 在尝试访问时会跳出二维码供扫描 但是忘记扫了的话会被退出（未来也许会修正

不会写的话可参考原repo 此处相当于将敏感信息分离

```json
{
    "COURSE_URL": "此处是需要刷的地址",
    "COOKIE": "填入Cookie 可为空"
}
```

