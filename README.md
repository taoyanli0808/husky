# Husky

基于大模型的开源测试平台(LLM-Driven Intelligent Testing Platform)

## 项目概述
Husky是一个智能化测试平台，利用大语言模型(LLM)的能力来自动化和优化软件测试流程。平台提供需求管理、测试用例生成、任务跟踪等功能，帮助团队提高测试效率和质量。

详细架构设计请参考 [ARCHITECTURE.md](ARCHITECTURE.md)，设计原则请参考 [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)。

## 项目优势
1. **智能化**：利用大模型自动生成测试用例，减少人工编写工作量
2. **自动化**：支持测试任务的自动分配和执行跟踪
3. **集成化**：整合需求管理、测试用例、执行跟踪于一体
4. **可视化**：直观展示测试进度和质量指标
5. **可扩展**：模块化设计，易于扩展新功能

## 截图示例
### 需求管理界面
![需求管理界面](docs/screenshots/requirements.png)

### 测试用例生成界面
![测试用例生成界面](docs/screenshots/testcase-generation.png)

### 任务状态跟踪界面
![任务状态跟踪界面](docs/screenshots/task-tracking.png)

## 核心功能
1. **需求管理**：导入和管理需求文档，支持从文档自动提取关键信息
2. **测试用例生成**：基于需求自动生成测试用例，支持多种测试类型
3. **任务状态管理**：跟踪测试任务的进度和状态
4. **知识库**：存储和管理测试相关知识，支持智能检索
5. **可视化**：提供测试结果和进度的可视化展示

## 技术栈
### 前端
- Nuxt.js (Vue.js框架)
- Element UI (UI组件库)
- Axios (HTTP客户端)

### 后端
- Flask (Python Web框架)
- MySQL (数据库)
- Redis (缓存)

### 部署
- Docker
- Nginx

## 项目结构
```
husky/
├── .dockerignore
├── .gitignore
├── ARCHITECTURE.md
├── DESIGN_PRINCIPLES.md
├── Dockerfile
├── LICENSE
├── README.md
├── TODO.list
├── app.py                 # Flask应用入口
├── docs/                  # 文档
├── front/                 # 前端代码
│   ├── assets/            # 静态资源
│   ├── components/        # 组件
│   ├── layouts/           # 布局
│   ├── pages/             # 页面
│   ├── plugins/           # 插件
│   └── store/             # 状态管理
├── husky/                 # 后端核心代码
│   ├── api/               # API接口
│   ├── config.py          # 配置
│   ├── models/            # 数据模型
│   ├── repositories/      # 数据访问
│   └── services/          # 业务逻辑
├── logs/                  # 日志
├── nginx.conf             # Nginx配置
├── nuxt.config.js         # Nuxt配置
├── package.json           # 前端依赖
├── requirements.txt       # 后端依赖
├── run.sh                 # 启动脚本
├── sql/                   # 数据库脚本
└── static/                # 静态文件
```

## 安装与部署
### 本地开发环境
#### 前置条件
- Node.js 16+
- Python 3.7+
- MySQL
- Redis

#### 步骤
1. 克隆仓库
```bash
git clone https://github.com/yourusername/husky.git
cd husky
```

2. 安装前端依赖
```bash
cd front
npm install
```

3. 安装后端依赖
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

4. 配置数据库
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE husky;"

# 导入初始数据
mysql -u root -p husky < sql/requirements.sql
mysql -u root -p husky < sql/tasks.sql
mysql -u root -p husky < sql/testcases.sql
```

5. 启动服务
```bash
# 启动前端
cd front
npm run dev

# 启动后端
cd ..
./run.sh start
```

### Docker部署
1. 构建镜像
```bash
docker build -t husky-app .
```

2. 运行容器
```bash
docker run -p 5000:5000 -p 3000:3000 husky-app
```

## 使用教程
### 快速开始
1. 访问前端页面: http://localhost:3000
2. 使用默认账号登录: admin/admin
3. 在"需求管理"页面导入或创建需求
4. 选择需求，点击"生成测试用例"按钮
5. 在"任务管理"页面跟踪测试进度

### 详细教程
请参考 [使用文档](docs/user_guide.md) 获取详细的操作指南。

## 未来规划
1. 支持更多类型的测试用例生成（单元测试、API测试等）
2. 集成自动化测试执行引擎
3. 增强AI辅助测试分析功能
4. 添加团队协作功能
5. 开发移动端适配版本

## 贡献指南
1. Fork仓库
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 许可证
本项目采用MIT许可证。详情请见LICENSE文件。

## 联系方式
如有问题或建议，请联系: taoyanli0808@126.com
