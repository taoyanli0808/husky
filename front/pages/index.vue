<template>
  <div class="home-container">
    <!-- 英雄区域 -->
    <section class="hero">
      <div class="hero-content">
        <h1>Husky测试平台</h1>
        <p>智能化测试管理解决方案，提升测试效率与质量</p>
        <div class="cta-buttons">
          <el-button type="primary" size="large">开始使用</el-button>
          <el-button size="large">了解更多</el-button>
        </div>
      </div>
    </section>

    <!-- 功能介绍区域 -->
    <section class="features">
      <div class="container">
        <h2>核心功能</h2>
        <div class="feature-cards">
          <el-card class="feature-card">
            <div class="icon-container">
              <img src="~/assets/require.png" alt="需求管理" class="feature-image">
            </div>
            <h3>需求管理</h3>
            <p>高效管理产品需求，确保测试覆盖全面</p>
          </el-card>

          <el-card class="feature-card">
            <div class="icon-container">
              <img src="~/assets/point.png" alt="测试点管理" class="feature-image">
            </div>
            <h3>测试点管理</h3>
            <p>系统化管理测试点，提高测试设计质量</p>
          </el-card>

          <el-card class="feature-card">
            <div class="icon-container">
              <img src="~/assets/testcase.png" alt="测试用例生成" class="feature-image">
            </div>
            <h3>测试用例生成</h3>
            <p>智能化生成测试用例，减少手动编写工作量</p>
          </el-card>

          <el-card class="feature-card">
            <div class="icon-container">
              <img src="~/assets/task.png" alt="任务管理" class="feature-image">
            </div>
            <h3>任务管理</h3>
            <p>跟踪测试任务进度，确保按时完成测试目标</p>
          </el-card>
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="workflow">
      <div class="container">
        <h2>使用流程</h2>
        <div class="steps">
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>上传需求文档</h3>
              <p>上传产品需求文档，系统自动解析关键信息</p>
            </div>
          </div>
          <div class="step-arrow"><i class="el-icon-arrow-right"></i></div>
          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>生成测试点</h3>
              <p>系统智能生成测试点，支持手动调整</p>
            </div>
          </div>
          <div class="step-arrow"><i class="el-icon-arrow-right"></i></div>
          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>生成测试用例</h3>
              <p>基于测试点自动生成详细测试用例</p>
            </div>
          </div>
          <div class="step-arrow"><i class="el-icon-arrow-right"></i></div>
          <div class="step-item">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3>执行测试任务</h3>
              <p>分配和跟踪测试任务，记录测试结果</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 优势展示 -->
    <section class="advantages">
      <div class="container">
        <h2>平台优势</h2>
        <div class="advantage-list">
          <div class="advantage-item">
            <img src="~/assets/advantage-item-1.png" alt="提高效率" class="advantage-image">
            <h3>提高效率</h3>
            <p>自动化生成测试用例，减少手动工作量</p>
          </div>
          <div class="advantage-item">
            <img src="~/assets/advantage-item-2.png" alt="提升质量" class="advantage-image">
            <h3>提升质量</h3>
            <p>系统化测试管理，确保测试覆盖全面</p>
          </div>
          <div class="advantage-item">
            <img src="~/assets/advantage-item-3.png" alt="团队协作" class="advantage-image">
            <h3>团队协作</h3>
            <p>支持多人协作，提高团队沟通效率</p>
          </div>
          <div class="advantage-item">
            <img src="~/assets/advantage-item-4.png" alt="数据驱动" class="advantage-image">
            <h3>数据驱动</h3>
            <p>提供测试数据分析，支持持续改进</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // 首页相关数据
    }
  },
  methods: {
    // 首页相关方法
  }
}
</script>

<style scoped>
.home-container {
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
}

/* 英雄区域样式 */
.hero {
  background: #fff;
  color: #304156;
  padding: 80px 0;
  text-align: center;
  border-bottom: 1px solid #e8e8e8;
}

.hero-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 42px;
  margin-bottom: 20px;
  font-weight: bold;
}

.hero p {
  font-size: 20px;
  margin-bottom: 30px;
  color: #597a96;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.el-button--primary {
  background-color: #304156;
  border-color: #304156;
}

.el-button--primary:hover {
  background-color: #1d2b3a;
  border-color: #1d2b3a;
}

.el-button {
  background-color: #fff;
  color: #304156;
  border-color: #dcdfe6;
}

/* 功能介绍区域样式 */
.features {
  padding: 80px 0;
  background-color: #fff;
}

.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 20px;
}

.features h2 {
  text-align: center;
  font-size: 32px;
  margin-bottom: 50px;
  color: #304156;
}

.feature-cards {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 25px;
  width: 100%;
  box-sizing: border-box;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  flex: 1;
  min-width: 220px;
  max-width: 280px;
  padding: 25px;
  text-align: center;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.icon-container {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background-color: #f0f7ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-image {
  width: 60px;
  height: 60px;
  object-fit: contain;
}

.icon-container i {
  font-size: 32px;
  color: #1890ff;
  display: none;
}

.feature-card h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #304156;
}

.feature-card p {
  color: #597a96;
  font-size: 14px;
}

/* 使用流程样式 */
.workflow {
  padding: 80px 0;
  background-color: #fff;
}

.workflow h2 {
  text-align: center;
  font-size: 32px;
  margin-bottom: 50px;
  color: #304156;
}

.steps {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 200px;
  text-align: center;
}

.step-number {
  width: 50px;
  height: 50px;
  background-color: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 15px;
}

.step-content h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: #304156;
}

.step-content p {
  color: #597a96;
  font-size: 14px;
}

.step-arrow {
  display: none;
  color: #1890ff;
  font-size: 24px;
}

@media (min-width: 768px) {
  .steps {
    flex-wrap: nowrap;
  }
  .step-arrow {
    display: flex;
    align-items: center;
  }
}

/* 优势展示样式 */
.advantages {
  padding: 80px 0;
  background-color: #fff;
  border-top: 1px solid #e8e8e8;
}

.advantages h2 {
  text-align: center;
  font-size: 32px;
  margin-bottom: 50px;
  color: #304156;
}

.advantage-list {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 25px;
  width: 100%;
  box-sizing: border-box;
  max-width: 1200px;
  margin: 0 auto;
}

.advantage-item {
  flex: 1;
  min-width: 220px;
  max-width: 280px;
  text-align: center;
  padding: 25px;
  background-color: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.advantage-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.advantage-image {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  object-fit: contain;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.advantage-image:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.advantage-item i {
  font-size: 40px;
  color: #1890ff;
  margin-bottom: 20px;
  display: none;
}

.advantage-item h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #304156;
}

.advantage-item p {
  color: #597a96;
  font-size: 14px;
}
</style>