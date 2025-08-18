# Husky测试平台 - 前端架构文档

## 架构概述

本项目采用Nuxt.js框架构建，遵循Vue.js的最佳实践，实现了一个完整的测试平台前端架构。架构采用模块化设计，包含状态管理、路由、布局、组件和API服务等部分。

## 技术栈

- Nuxt.js 2.x
- Vue.js 2.x
- Vuex (状态管理)
- Element UI (UI组件库)
- Axios (HTTP请求)

## 目录结构

```
front/
├── assets/         # 静态资源(图片、样式等)
├── components/     # 公共组件
├── layouts/        # 布局组件
├── middleware/     # 中间件
├── pages/          # 页面组件
├── plugins/        # 插件
├── static/         # 静态文件
├── store/          # Vuex状态管理
└── utils/          # 工具函数
```

## 状态管理

使用Vuex进行状态管理，按功能模块划分：

- `task`: 任务相关状态
- `requirement`: 需求相关状态
- `point`: 测试点相关状态
- `testcase`: 测试用例相关状态

### 使用示例

```javascript
// 在组件中使用
import { mapState, mapActions } from 'vuex'

export default {
  computed: {
    ...mapState('task', ['taskList', 'loading'])
  },
  methods: {
    ...mapActions('task', ['fetchTaskList'])
  },
  mounted() {
    this.fetchTaskList()
  }
}
```

## API服务

API服务封装在`utils/request.js`中，提供统一的请求接口和错误处理。

### 使用示例

```javascript
import { request } from '@/utils/request'

// 发送GET请求
request.get('/api/v1/task/list', { page: 1, size: 10 })
  .then(res => {
    console.log(res)
  })
  .catch(err => {
    console.error(err)
  })

// 发送POST请求
request.post('/api/v1/task/create', { name: '测试任务' })
  .then(res => {
    console.log(res)
  })
  .catch(err => {
    console.error(err)
  })
```

## 布局组件

默认布局组件`layouts/default.vue`包含导航栏、侧边栏和页脚，所有页面默认使用此布局。

## 开发指南

### 安装依赖

```bash
cd front
npm install
```

### 开发模式运行

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 启动生产服务器

```bash
npm run start
```

## 组件规范

1. 公共组件放在`components/`目录下
2. 组件命名采用大驼峰命名法，如`TableComponent.vue`
3. 组件应具有单一职责
4. 复杂组件应拆分为更小的组件

## 代码规范

1. 使用ESLint进行代码检查
2. 代码风格遵循Vue.js官方指南
3. 提交代码前应运行`npm run lint`进行检查

## 后续优化方向

1. 引入单元测试和E2E测试
2. 优化构建性能
3. 实现组件懒加载
4. 添加国际化支持
5. 优化移动端适配