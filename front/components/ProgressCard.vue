<template>
  <el-card class="progress-card" v-if="activeTask">
    <div class="progress-header">
      <h3>需求分析进度</h3>
    </div>
    
    <el-steps 
      :active="progressActive" 
      align-center
      finish-status="success"
      :process-status="progressStatus"
    >
      <el-step 
        title="需求分块处理" 
        :description="progressSteps[0].desc"
      />
      <el-step 
        title="功能点提取" 
        :description="progressSteps[1].desc"
      />
      <el-step 
        title="测试点生成" 
        :description="progressSteps[2].desc"
      />
      <el-step 
        title="分析完成" 
        :description="progressSteps[3].desc"
      />
    </el-steps>
    
    <div class="progress-details">
      <div class="progress-message">
        <el-tag :type="progressTagType">{{ taskStatusText }}</el-tag>
        <span style="margin-left: 10px;">{{ taskMessage }}</span>
      </div>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'ProgressCard',
  props: {
    taskId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      // 任务进度相关数据
      activeTask: null,
      taskProgress: 0,
      taskStatus: '',
      taskMessage: '',
      progressSteps: [
        { desc: '等待开始' },
        { desc: '等待开始' },
        { desc: '等待开始' },
        { desc: '等待开始' }
      ],
      progressInterval: null
    }
  },
  computed: {
    progressActive() {
      if (this.taskProgress >= 100) return 4;
      if (this.taskProgress >= 90) return 2;
      if (this.taskProgress >= 30) return 1;
      return 0;
    },
    progressStatus() {
      if (this.taskStatus === 'failed') return 'exception';
      if (this.taskStatus === 'completed') return 'success';
      return 'process';
    },
    progressTagType() {
      switch (this.taskStatus) {
        case 'pending': return 'info';
        case 'processing': return '';
        case 'completed': return 'success';
        case 'failed': return 'danger';
        default: return 'info';
      }
    },
    taskStatusText() {
      switch (this.taskStatus) {
        case 'pending': return '等待中';
        case 'processing': return '处理中';
        case 'completed': return '已完成';
        case 'failed': return '失败';
        default: return '未知状态';
      }
    }
  },
  created() {
    // 检查任务状态
    this.checkTaskStatus()
  },
  beforeUnmount() {
    // 清除定时器
    if (this.progressInterval) {
      clearInterval(this.progressInterval)
    }
  },
  methods: {
    // 检查任务状态
    async checkTaskStatus() {
      try {
        const res = await this.$axios.get('/api/v1/task/search', {
          params: { task_id: this.taskId }
        })
        
        if (res.data.code === 0) {
          const tasks = res.data.data.list
          if (tasks && tasks.length > 0) {
            const taskData = tasks[0]
            this.activeTask = taskData.task_id // 始终设置activeTask
            this.taskProgress = taskData.progress
            this.taskStatus = taskData.status
            this.taskMessage = taskData.message
            
            this.updateProgressSteps(taskData)
            
            // 如果任务未完成，开始监控
            if (taskData.status !== 'completed' && taskData.status !== 'failed') {
              this.startProgressMonitoring(this.activeTask)
            }
          } else {
            console.error('未找到任务数据')
          }
        }
      } catch (error) {
        console.error('检查任务状态失败:', error)
        // 即使API调用失败，也显示步骤条（使用默认状态）
        this.activeTask = this.taskId
      }
    },
    
    // 开始监控任务进度
    startProgressMonitoring(task_id) {
      this.updateTaskProgress(task_id)
      
      // 每5秒刷新一次状态
      this.progressInterval = setInterval(() => {
        this.updateTaskProgress(task_id)
      }, 5000)
    },
    
    // 更新任务进度
    async updateTaskProgress(task_id) {
      try {
        const res = await this.$axios.get('/api/v1/task/search', {
          params: { task_id }
        })
        
        if (res.data.code === 0) {
          const tasks = res.data.data.list
          if (tasks && tasks.length > 0) {
            const taskData = tasks[0]
            this.taskProgress = taskData.progress
            this.taskStatus = taskData.status
            this.taskMessage = taskData.message
            
            // 更新步骤描述
            this.updateProgressSteps(taskData)
            
            // 如果任务完成或失败，停止轮询
            if (['completed', 'failed'].includes(taskData.status)) {
              clearInterval(this.progressInterval)
              this.progressInterval = null
            }
          } else {
            console.error('未找到任务数据')
          }
        }
      } catch (error) {
        console.error('更新任务进度失败:', error)
      }
    },
    
    // 更新步骤描述
    updateProgressSteps(taskData) {
      this.progressSteps = [
        {
          desc: taskData.progress >= 30 ? '已完成' : 
               (taskData.status === 'processing' && taskData.progress < 30 ? '处理中...' : '等待开始')
        },
        {
          desc: taskData.progress >= 90 ? '已完成' : 
               (taskData.status === 'processing' && taskData.progress >= 30 && taskData.progress < 90 ? '处理中...' : '等待开始')
        },
        {
          desc: taskData.progress >= 100 ? '已完成' : 
               (taskData.status === 'processing' && taskData.progress >= 90 && taskData.progress < 100 ? '处理中...' : '等待开始')
        },
        {
          desc: taskData.status === 'completed' ? '分析完成' : 
               (taskData.status === 'failed' ? '分析失败' : '等待完成')
        }
      ]
    }
  }
}
</script>

<style scoped>
.progress-card {
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-details {
  margin-top: 20px;
}

.progress-message {
  margin-top: 15px;
  display: flex;
  align-items: center;
}
</style>