<template>
  <div class="points-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <!-- 进度卡片 -->
        <ProgressCard :taskId="taskId" :requireId="requireId"/>
      </el-col>
      <el-col :span="24">
        <!-- 测试点表格 -->
        <PointsTable :taskId="taskId" :requireId="requireId" :requireName="requireName"/>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import ProgressCard from '@/components/ProgressCard.vue'
import PointsTable from '@/components/PointsTable.vue'

export default {
  name: 'PointsPage',
  components: {
    ProgressCard,
    PointsTable
  },
  data() {
    return {
      taskId: '',
      requireId: '',
      requireName: ''
    }
  },
  created() {
    // 从URL参数中获取任务ID和需求ID
    this.taskId = this.$route.query.task_id || ''
    this.requireId = this.$route.query.require_id || ''
    this.requireName = this.$route.query.require_name || ''
  },
  watch: {
    '$route': function(newRoute) {
      // 监听路由变化，更新任务ID和需求ID
      this.taskId = newRoute.query.task_id || ''
      this.requireId = newRoute.query.require_id || ''
      this.requireName = newRoute.query.require_name || ''
    }
  }
}
</script>

<style scoped>
.points-page {
  padding: 20px;
}
</style>