# ChatGLM3 Discord Database Bot

一个基于 ChatGLM3 的 Discord 机器人，支持中文自然语言查询数据库。该机器人可以连接到您的 MySQL 数据库，并通过中文问题查询订单、产品、用户等信息。

## 功能特性

- 🤖 **AI 驱动**: 使用 ChatGLM3 模型进行自然语言处理
- 🗄️ **数据库集成**: 直接连接到 MySQL 数据库进行查询
- 🇨🇳 **中文支持**: 完全支持中文自然语言查询
- 🔒 **只读访问**: 仅支持查询操作，保护数据安全
- 📊 **丰富查询**: 支持订单、产品、用户、统计等多种查询类型
- 🚀 **易于使用**: 直接在 Discord 中发送中文问题即可

## 支持的查询类型

### 订单查询

- 按订单号查询: "搜索订单号 12345"
- 按客户名查询: "查找客户张三的订单"
- 按状态查询: "查询已发货状态的订单"
- 最近订单: "显示最近 10 个订单"
- 日期范围查询: "查询 2024 年 1 月的订单"

### 产品查询

- 按 SKU 查询: "搜索产品 SKU ABC123"
- 按名称查询: "查找产品名称包含 xxx 的产品"
- 按分类查询: "显示 mizuki 分类的产品"
- 库存查询: "查看库存不足的产品"

### 用户查询

- 按用户名查询: "搜索用户 admin"
- 按姓名查询: "查找用户张三"

### 统计信息

- 订单统计: "查看订单统计信息"
- 产品统计: "显示产品库存统计"
- 收入统计: "查看总收入统计"

### 系统信息

- 数据库健康检查: "检查数据库状态"
- MyACG 账户信息: "显示 MyACG 账户"

## 安装和配置

### 1. 环境要求

- Python 3.8+
- MySQL 数据库
- Discord Bot Token
- ChatGLM3 模型文件

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd PackingElf_chatbot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 下载 ChatGLM3 模型

```bash
# 创建模型目录
mkdir models

# 下载模型文件 (需要手动下载)
# 从 https://huggingface.co/mradermacher/chatglm3-6b-gguf 下载
# chatglm3-6b.Q4_K_M.gguf 文件到 models/ 目录
```

### 4. 配置环境变量

创建 `.env` 文件:

```env
# Discord Bot Token (必需)
DISCORD_TOKEN=your_discord_bot_token_here

# 数据库配置 (可选，可通过命令设置)
DB_HOST=192.168.1.100
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Meridian0723
DB_NAME=MyACG_data

# AI模型配置 (可选)
MODEL_PATH=models/chatglm3-6b.Q4_K_M.gguf
MAX_TOKENS=2048
TEMPERATURE=0.7

# Bot配置 (可选)
COMMAND_PREFIX=!
MAX_RESULTS=50
```

### 5. 数据库配置

机器人会自动尝试连接到数据库。如果连接失败，可以使用以下命令手动连接:

```
!connect 192.168.1.100
```

## 🚀 快速启动 (Windows)

### 方法 1: 使用批处理文件 (推荐)

1. **首次安装**: 运行 `setup.bat` 进行环境设置
2. **启动机器人**: 双击 `start_bot.bat` 启动机器人
3. **快速启动**: 如果已配置完成，可直接运行 `run_bot.bat`

### 方法 2: 手动启动

```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动机器人
python run.py
```

## 📁 批处理文件说明

- **`setup.bat`**: 首次安装脚本，自动创建虚拟环境并安装依赖
- **`start_bot.bat`**: 完整启动脚本，包含环境检查和错误处理
- **`run_bot.bat`**: 简单启动脚本，适用于已配置的环境

## 使用方法

### 1. 启动机器人

```bash
python run.py
```

### 2. 基本命令

- `!help` - 显示帮助信息
- `!connect <数据库IP>` - 连接到数据库
- `!status` - 检查系统状态
- `!health` - 检查数据库健康状态

### 3. 查询示例

直接在 Discord 中发送中文问题:

```
搜索订单号12345
查找客户张三的订单
显示最近10个订单
查询已发货状态的订单
搜索产品SKU ABC123
显示mizuki分类的产品
查看订单统计信息
显示产品库存统计
```

## 数据库结构

机器人支持以下数据库表:

### Orders (订单表)

- `id` - 订单 ID
- `external_order_id` - 外部订单号
- `invoice` - 发票号
- `customer_name` - 客户姓名
- `status` - 订单状态
- `total` - 订单总额
- `shipping_cost` - 运费
- `order_date` - 订单日期
- `created_at` - 创建时间

### Products (产品表)

- `id` - 产品 ID
- `sku` - 产品 SKU
- `name` - 产品名称
- `price` - 价格
- `stock_quantity` - 库存数量
- `category` - 产品分类
- `is_active` - 是否激活

### Users (用户表)

- `id` - 用户 ID
- `name` - 用户姓名
- `username` - 用户名
- `is_active` - 是否激活

### MyACGAccounts (MyACG 账户表)

- `id` - 账户 ID
- `name` - 账户名称
- `username` - 用户名
- `is_default` - 是否默认账户

## 项目结构

```
PackingElf_chatbot/
├── src/
│   ├── bot.py              # 主机器人文件
│   ├── ai_model.py         # AI模型管理
│   ├── database_reader.py  # 数据库读取服务
│   ├── query_handler.py    # 查询处理器
│   └── config.py           # 配置文件
├── target_database/        # 目标数据库代码
├── models/                 # AI模型文件
├── requirements.txt        # 依赖包
├── run.py                 # 启动脚本
└── README.md              # 说明文档
```

## 故障排除

### 常见问题

1. **数据库连接失败**

   - 检查数据库是否运行
   - 确认 IP 地址和端口正确
   - 验证用户名和密码

2. **AI 模型加载失败**

   - 确认模型文件存在
   - 检查模型文件路径
   - 验证模型文件完整性

3. **Discord Bot 无法启动**
   - 检查 DISCORD_TOKEN 是否正确
   - 确认 Bot 有正确的权限
   - 验证网络连接

### 日志文件

机器人运行时会生成 `bot.log` 日志文件，包含详细的运行信息。

## 开发说明

### 添加新的查询类型

1. 在 `query_handler.py` 中添加新的处理方法
2. 在 `_determine_query_type` 中添加关键词识别
3. 在 `database_reader.py` 中添加相应的数据库查询方法

### 自定义响应格式

修改 `query_handler.py` 中的 `format_response` 方法来自定义响应格式。

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。
