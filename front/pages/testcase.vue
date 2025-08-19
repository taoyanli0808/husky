<template>
  <div class="testcases-container">
    <!-- 用例生成进度卡片 -->
    <el-card class="progress-card" v-if="task_id">
      <div class="progress-header">
        <h3>测试用例生成进度</h3>
      </div>
      
      <el-steps 
        :active="progressActive" 
        align-center
        finish-status="success"
        :process-status="progressStatus"
      >
        <el-step 
          title="测试点分析" 
          :description="progressSteps[0].desc"
        />
        <el-step 
          title="用例设计" 
          :description="progressSteps[1].desc"
        />
        <el-step 
          title="优先级排序" 
          :description="progressSteps[2].desc"
        />
        <el-step 
          title="生成完成" 
          :description="progressSteps[3].desc"
        />
      </el-steps>
      
      <div class="progress-details">
        <div class="progress-message">
          <el-tag :type="progressTagType">{{ taskStatusText }}</el-tag>
          <span style="margin-left: 10px;">{{ task_message }}</span>
        </div>
      </div>
    </el-card>

    <el-card class="result-card" shadow="never" v-if="testcases.length > 0">
      <div slot="header" class="result-header">
        <span>测试用例列表</span>
        <div class="view-switcher">
          <el-radio-group v-model="viewMode" size="small">
            <el-radio label="table">表格视图</el-radio>
            <el-radio label="mindmap">脑图视图</el-radio>
          </el-radio-group>
        </div>
        <span style="float: right; font-size: 12px; color: #909399">
          共 {{ testcases.length }} 条
        </span>
      </div>

      <!-- 表格视图 -->
      <test-case-table 
        v-if="viewMode === 'table'"
        :testcases="testcases"
        :loading="loading"
      />

      <!-- 脑图视图 -->
      <test-case-mindmap 
        v-else
        :testcases="testcases"
      />
    </el-card>
  </div>
</template>

<script>
import TestCaseTable from '@/components/TestCaseTable.vue'
import TestCaseMindmap from '@/components/TestCaseMindmap.vue'

export default {
  components: {
    TestCaseTable,
    TestCaseMindmap
  },
  data() {
    return {
      task_id: "",
      require_id: "",
      task_status: null,
      task_message: "",
      testcases: [],
      loading: false,
      pollingInterval: null,
      progressSteps: [
        { desc: "等待开始", completed: false },
        { desc: "等待开始", completed: false },
        { desc: "等待开始", completed: false },
        { desc: "等待开始", completed: false }
      ],
      viewMode: 'table' // 'table' 或 'mindmap'
    };
  },
  computed: {
    progressActive() {
      if (!this.task_status) return 0;
      if (this.task_status.progress >= 100) return 4;
      if (this.task_status.progress >= 70) return 3;
      if (this.task_status.progress >= 30) return 2;
      return 1;
    },
    progressStatus() {
      if (this.task_status?.status === "failed") return "exception";
      if (this.task_status?.status === "completed") return "success";
      return "process";
    },
    progressTagType() {
      switch (this.task_status?.status) {
        case "pending": return "info";
        case "processing": return "";
        case "completed": return "success";
        case "failed": return "danger";
        default: return "info";
      }
    },
    taskStatusText() {
      switch (this.task_status?.status) {
        case "pending": return "等待中";
        case "processing": return "处理中";
        case "completed": return "已完成";
        case "failed": return "失败";
        default: return "未知状态";
      }
    }
  },
  created() {
    // 从URL参数中获取task_id和require_id
    const query = this.$route.query;
    if (query.task_id) {
      this.task_id = query.task_id;
      this.startPolling(this.task_id);
    }
    if (query.require_id) {
      this.require_id = query.require_id;
    }
  },
  methods: {
    updateProgressSteps(taskData) {
      this.progressSteps = [
        { 
          desc: taskData.progress >= 30 ? "已完成" : 
               (taskData.status === "processing" && taskData.progress < 30 ? "处理中..." : "等待开始") 
        },
        { 
          desc: taskData.progress >= 70 ? "已完成" : 
               (taskData.status === "processing" && taskData.progress >= 30 && taskData.progress < 70 ? "处理中..." : "等待开始") 
        },
        { 
          desc: taskData.progress >= 100 ? "已完成" : 
               (taskData.status === "processing" && taskData.progress >= 70 && taskData.progress < 100 ? "处理中..." : "等待开始") 
        },
        { 
          desc: taskData.status === "completed" ? "生成完成" : 
               (taskData.status === "failed" ? "生成失败" : "等待完成") 
        }
      ];
    },

    async checkTaskStatus(task_id) {
      try {
        const response = await this.$axios.get("/api/v1/task/search", {
          params: { task_id },
        });

        if (response.data.code === 0 && response.data.data.list && response.data.data.list.length > 0) {
          const taskData = response.data.data.list[0];
          this.task_status = taskData;
          this.task_message = taskData.message || "";
          this.updateProgressSteps(taskData);
          
          if (taskData.status === "completed") {
            this.stopPolling();
            // 自动加载测试用例
            this.fetchTestCases();
          }
          return true;
        } else {
          console.error("未找到任务数据");
          return false;
        }
      } catch (error) {
        console.error("查询任务状态失败:", error);
        return false;
      }
    },

    async fetchTestCases() {
      this.loading = true;
      try {
        const response = await this.$axios.post("/api/v1/testcase/search", {
          task_id: this.task_id,
        });

        if (response.data.code === 0) {
          this.testcases = response.data.data.list.map((item) => {
            // 处理JSON字符串字段
            const jsonFields = ['preconditions', 'test_steps', 'expected_result', 'test_type'];
            jsonFields.forEach(field => {
              if (item[field] && typeof item[field] === 'string') {
                try {
                  item[field] = JSON.parse(item[field]);
                } catch (e) {
                  item[field] = [];
                }
              }
            });
            return item;
          });
        } else {
          this.$message.error(response.data.message || "获取测试用例失败");
        }
      } catch (error) {
        this.$message.error("请求失败: " + error.message);
      } finally {
        this.loading = false;
      }
    },

    startPolling(task_id) {
      // 先停止已有的轮询
      this.stopPolling();

      // 立即查询一次状态
      this.checkTaskStatus(task_id);

      // 设置定时轮询
      this.pollingInterval = setInterval(() => {
        this.checkTaskStatus(task_id);
      }, 3000);
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },
  },
  beforeDestroy() {
    this.stopPolling();
  },
};
</script>

<style scoped>
.testcases-container {
  padding: 20px;
}

.progress-card {
  margin-bottom: 20px;
}

.progress-header {
  margin-bottom: 20px;
}

.progress-details {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-message {
  display: flex;
  align-items: center;
}

.result-card {
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-switcher {
  margin-left: 20px;
}
</style>