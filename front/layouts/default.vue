<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="logo">
        <img src="~/assets/logo.png" alt="Husky Logo">
        <nuxt-link to="/" class="logo-link">
          <span>Husky测试平台</span>
        </nuxt-link>
      </div>
      <nav class="nav">
        <ul>
          <li><nuxt-link to="/requirement">需求管理</nuxt-link></li>
          <li><nuxt-link to="/task">任务管理</nuxt-link></li>
          <li><nuxt-link to="/knowledge">知识管理</nuxt-link></li>
        </ul>
      </nav>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <nuxt />
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <p>© 2023 Husky测试平台. 保留所有权利.</p>
    </footer>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  data() {
    return {
      // 可以在这里定义布局相关的数据
    }
  },
  computed: {
    ...mapState({
      // 可以映射全局状态
    })
  },
  methods: {
    // 可以定义布局相关的方法
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  height: 60px;
  background-color: #304156;
  color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 100%;
  box-sizing: border-box;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
}

.logo img {
  width: 40px;
  height: 40px;
  margin-right: 10px;
}

.logo span {
  font-size: 18px;
  font-weight: bold;
}

.logo-link {
  color: #fff;
  text-decoration: none;
}

.logo-link:hover {
  color: #409EFF;
}

.nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav li {
  margin: 0 15px;
}

.nav a {
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
}

.nav a:hover {
  color: #409EFF;
}

.user-info {
  display: flex;
  align-items: center;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #fff;
}

.footer {
  padding: 20px;
  text-align: center;
  background-color: #fff;
  border-top: 1px solid #eee;
}
</style>