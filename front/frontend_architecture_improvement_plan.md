# 前端架构完善方案

基于Nuxt.js框架，针对当前husky项目前端架构的不完善之处，制定以下完善方案：

## 1. 目录结构优化

当前前端目录只有`pages`和`plugins`，需要添加Nuxt.js标准目录结构：

```
front/
├── assets/         # 静态资源
├── components/     # 公共组件
├── layouts/        # 布局组件
├── middleware/     # 中间件
├── pages/          # 页面组件（已有）
├── plugins/        # 插件（已有）
├── static/         # 静态文件
├── store/          # Vuex状态管理
└── utils/          # 工具函数
```

## 2. 状态管理实现

创建Vuex状态管理，用于管理全局状态，如用户信息、任务状态等。

## 3. 公共组件提取

从现有页面中提取公共组件，如表格、分页、按钮组等，提高代码复用率。

## 4. 布局组件实现

创建统一的布局组件，包含导航栏、侧边栏等公共元素。

## 5. API服务封装

创建统一的API服务层，封装请求方法和错误处理。

## 6. 路由优化

虽然Nuxt.js会自动生成路由，但可以通过页面组件的命名和目录结构优化路由。

## 7. 中间件添加

添加必要的中间件，如身份验证、日志记录等。

## 8. 样式统一

创建全局样式文件，统一页面风格。

## 具体实现步骤

### 第一步：创建必要目录

```bash
mkdir -p front/assets front/components front/layouts front/middleware front/static front/store front/utils
```

### 第二步：实现状态管理

创建store/index.js及相关模块文件。

### 第三步：创建布局组件

创建layouts/default.vue作为默认布局。

### 第四步：封装API服务

创建utils/request.js封装Axios请求。

### 第五步：提取公共组件

从现有页面提取公共组件到components目录。

### 第六步：更新页面组件

使用新创建的布局和组件更新现有页面。