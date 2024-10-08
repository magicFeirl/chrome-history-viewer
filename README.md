**前置条件**

每个 Google 账号每天有一定的免费的 Colab T4 GPU 使用时间，利用 Chrome 的用户功能添加了多个不同账号的浏览器用户。

**需求**

免费的 GPU 最多可以运行 ~3.5h，之后每天能恢复 1h，而训练一个 SDXL LoRA 至少 2h，所以某些时候一个账户用完得等到第三天才可能继续用来训练 LoRA。需求是避免打开这些正在冷却的账户。一个简单的方法是打开用户之后 ctrl + h 查找历史记录上次打开训练 notebook 的时间，该方法的问题在于不够方便，而且可能有遗漏。

**思路**

批量读取 Chrome 用户的浏览记录，关键字查找指定的 URL 并获取上次打开的时间。浏览记录保存在 Chrome data 文件夹的 History SQLite 中，除了浏览记录还需要获取浏览器的用户名，在同目录的 Pereferenece JSON 中。

后端：按上面给出的思路即可，主要是文件读取和 SQLite 查询
前端：展示必要字段，通过接口调用后端打开浏览器


**运行**

Windows 下点击 run.bat 会自动打开前端网页和后端；或者手动打开 html/index.html 和运行 `python backend/app.py`，项目根目录下的 main.py 用于导出 csv


**Screenshot**

![screenshot](./docs/1.png)