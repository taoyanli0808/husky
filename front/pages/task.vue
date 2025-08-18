<template>
  <div>
    <div v-if="loading" class="loading" v-loading="loading"></div>
    <div v-else-if="taskList.length === 0" class="empty-state">
      <el-empty description="暂无任务数据"></el-empty>
    </div>
    <div v-else>
      <div class="task-header">
        <div class="clearfix">
          <span>任务列表</span>
          <div style="float: right;">
            <el-button type="primary" size="mini" @click="refreshData">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
          </div>
        </div>
      </div>

      <div class="task-list">
        <div v-for="row in taskList" :key="row.task_id" class="task-item">
          <div class="task-header-info">
            <div class="task-title">
              <h3>任务ID: {{ row.task_id }}</h3>
            </div>
          </div>

          <div class="task-body">
            <div class="task-meta-info">
              <div class="meta-item">
                <span class="meta-label">任务类型:</span>
                <el-tag :type="row.task_type === 'point_analysis' ? 'primary' : 'success'" size="small">
                  {{ row.task_type === 'point_analysis' ? '功能分析' : '用例生成' }}
                </el-tag>
              </div>
              <div class="meta-item">
                <span class="meta-label">状态:</span>
                <el-tag :type="getStatusTagType(row.status)" size="small">
                  {{ getStatusName(row.status) }}
                </el-tag>
              </div>
              <div class="meta-item">
                <span class="meta-label">功能点数:</span>
                <span class="meta-value">{{ row.result?.points_count || 0 }}</span>
              </div>
              <div class="meta-item progress-item">
                <span class="meta-label">进度:</span>
                <el-progress 
                  :percentage="row.progress" 
                  :status="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'exception' : 'warning'"
                  :text-inside="true"
                  :stroke-width="14"
                  style="width: 120px;"/>
              </div>
            </div>

            <div class="task-message">
              <span class="message-label">消息:</span>
              <span class="message-content">{{ row.message }}</span>
            </div>
          </div>

          <div class="task-footer">
            <div class="footer-time-info">
              <span class="task-time">开始时间: {{ formatTime(row.start_time) }}</span>
              <span class="task-time">结束时间: {{ row.end_time ? formatTime(row.end_time) : '-' }}</span>
            </div>
            <div class="footer-buttons">
              <el-button 
                size="mini" 
                @click="viewTaskDetail(row)"
                :disabled="row.status !== 'completed'"
              >
                <i class="el-icon-view"></i> 详情
              </el-button>
              <el-button 
                size="mini" 
                @click="openPointsDrawer(row.task_id)"
                :disabled="row.status !== 'completed'"
              >
                <i class="el-icon-document"></i> 测试点
              </el-button>
              <el-button 
                size="mini" 
                type="danger" 
                @click="forceCancelTask(row.task_id)"
                :disabled="row.status === 'completed' || row.status === 'failed'"
              >
                <i class="el-icon-close"></i> 终止
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="pagination.current"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
        />
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog 
      :title="'任务详情 - ' + currentTask.task_id" 
      :visible.sync="detailVisible" 
      width="70%"
      top="5vh"
    >
      <el-tabs type="border-card">
        <el-tab-pane label="基本信息">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="任务类型">
              {{ currentTask.task_type === 'point_analysis' ? '功能点分析' : '测试用例生成' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusTagType(currentTask.status)" size="small">
                {{ getStatusName(currentTask.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="进度">{{ currentTask.progress }}%</el-descriptions-item>
            <el-descriptions-item label="关联需求">{{ currentTask.require_id || '-' }}</el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatTime(currentTask.start_time) }}</el-descriptions-item>
            <el-descriptions-item label="结束时间">{{ currentTask.end_time ? formatTime(currentTask.end_time) : '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="任务日志">
          <pre class="task-log">{{ currentTask.message }}</pre>
        </el-tab-pane>
        
        <el-tab-pane :label="currentTask.task_type === 'point_analysis' ? '功能点' : '测试用例'">
          <component 
            :is="currentTask.task_type === 'point_analysis' ? 'point-result' : 'testcase-result'" 
            :task-id="currentTask.task_id"
          />
        </el-tab-pane>
      </el-tabs>

      <span slot="footer" class="dialog-footer">
        <el-button @click="detailVisible = false">关 闭</el-button>
      </span>
    </el-dialog>

    <!-- 测试点抽屉 -->
    <el-drawer
        title="测试点列表"
        :visible.sync="pointsDrawerVisible"
        :direction="'ltr'"
        :size="'80%'"
    >
      <div class="points-drawer-content">
        <ProgressCard :taskId="currentTaskId" />
        <PointsTable :taskId="currentTaskId" :requireId="currentTask.require_id" />
      </div>
    </el-drawer>
  </div>
</template>

<script>
import request from '@/utils/request';
import ProgressCard from '@/components/ProgressCard.vue'
import PointsTable from '@/components/PointsTable.vue'

const PointResult = {
  props: ['taskId'],
  template: `
    <el-table :data="points" style="width: 100%" border>
      <el-table-column prop="function_name" label="功能名称" width="180" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="test_type" label="测试类型" width="120" />
      <el-table-column prop="business_domain" label="业务领域" width="120" />
    </el-table>
  `,
  data() {
    return {
      points: []
    }
  },
  created() {
    this.fetchPoints();
  },
  methods: {
    fetchPoints() {
      request.post('/api/v1/point/search', { task_id: this.taskId })
        .then(response => {
          this.points = response.data.data?.list || [];
        });
    }
  }
};

const TestcaseResult = {
  props: ['taskId'],
  template: `
    <el-table :data="testcases" style="width: 100%" border>
      <el-table-column prop="case_name" label="用例名称" width="180" />
      <el-table-column prop="priority" label="优先级" width="100">
        <template #default="{row}">
          <el-tag :type="row.priority === 'P0' ? 'danger' : row.priority === 'P1' ? 'warning' : 'info'">
            {{ row.priority }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="test_steps" label="测试步骤" show-overflow-tooltip>
        <template #default="{row}">
          <ol style="margin: 0; padding-left: 20px">
            <li v-for="(step, index) in row.test_steps" :key="index">
              {{ step }}
            </li>
          </ol>
        </template>
      </el-table-column>
    </el-table>
  `,
  data() {
    return {
      testcases: []
    }
  },
  created() {
    this.fetchTestcases();
  },
  methods: {
    fetchTestcases() {
      request.post('/api/v1/testcase/search', { task_id: this.taskId })
          .then(response => {
            this.testcases = response.data?.list || [];
          });
    }
  }
};

export default {
  name: 'TaskTable',
  components: {
    'point-result': PointResult,
    'testcase-result': TestcaseResult,
    ProgressCard,
    PointsTable
  },
  data() {
    return {
      loading: false,
      taskList: [],
      currentTask: {},
      detailVisible: false,
      pointsDrawerVisible: false,
      currentTaskId: '',
      pagination: {
        current: 1,
        size: 10,
        total: 0
      },
      sort: {
        prop: 'created_at',
        order: 'descending'
      }
    }
  },
  created() {
    this.fetchData();
  },
  methods: {
    openPointsDrawer(taskId) {
      this.currentTaskId = taskId;
      this.pointsDrawerVisible = true;
    },
    
    async fetchData() {
      this.loading = true;
      try {
          const params = {
            page: this.pagination.current,
            size: this.pagination.size,
            sort: this.sort.prop,
            order: this.sort.order === 'ascending' ? 'asc' : 'desc'
          };
          
          const response = await request.get('/api/v1/task/search', params);
          
          if (response.code === 0) {
            this.taskList = response.data?.list || [];
            this.pagination.total = response.data?.total || 0;
          } else {
            this.$message.error(response.message || '获取数据失败');
          }
        } catch (error) {
        console.error('请求失败:', error);
        this.$message.error('请求失败: ' + (error.response?.data?.message || error.message));
      } finally {
        this.loading = false;
      }
    },
    
    refreshData() {
      this.pagination.current = 1;
      this.fetchData();
      this.$message.success('数据已刷新');
    },
    
    viewTaskDetail(task) {
      this.currentTask = task;
      this.detailVisible = true;
    },
    
    forceCancelTask(taskId) {
      this.$confirm('确定要强制终止此任务吗?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        request.post('/api/v1/task/cancel', { task_id: taskId })
          .then(() => {
            this.$message.success('任务终止请求已发送');
            this.fetchData();
          });
      });
    },
    
    handleSizeChange(size) {
      this.pagination.size = size;
      this.fetchData();
    },
    
    handleCurrentChange(current) {
      this.pagination.current = current;
      this.fetchData();
    },
    
    handleSortChange({ prop, order }) {
      this.sort = { prop, order };
      this.fetchData();
    },
    
    formatTime(time) {
      if (!time) return '';
      const date = new Date(time);
      return date.getFullYear() + '-' +
             String(date.getMonth() + 1).padStart(2, '0') + '-' +
             String(date.getDate()).padStart(2, '0') + ' ' +
             String(date.getHours()).padStart(2, '0') + ':' +
             String(date.getMinutes()).padStart(2, '0') + ':' +
             String(date.getSeconds()).padStart(2, '0');
    },
    
    getStatusName(status) {
      const map = {
        'pending': '等待中',
        'processing': '进行中',
        'completed': '已完成',
        'failed': '已失败'
      };
      return map[status] || status;
    },
    
    getStatusTagType(status) {
      const map = {
        'pending': 'info',
        'processing': 'primary',
        'completed': 'success',
        'failed': 'danger'
      };
      return map[status] || '';
    }
  }
}
</script>

<style scoped>
.loading {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.task-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.task-list {
  margin-top: 20px;
}

.task-item {
  padding: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.task-item:hover {
  background-color: #f9fafc;
  transition: background-color 0.3s;
}

.task-header-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.task-meta {
  display: flex;
  gap: 8px;
}

.task-body {
  margin-bottom: 16px;
  padding: 16px;
  background-color: #f9fafc;
  border-radius: 4px;
}

.task-meta-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #e6e8eb;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.meta-value {
  font-size: 14px;
  color: #333;
}

.progress-item {
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}

.task-message {
  margin-top: 12px;
}

.message-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  margin-right: 8px;
}

.message-content {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
  word-break: break-all;
}

.task-message p {
  margin: 0;
  color: #333;
  line-height: 1.6;
  word-break: break-all;
  font-size: 13px;
}

.task-time-info {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.task-time {
  font-size: 12px;
  color: #666;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-time-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-buttons {
  display: flex;
}

.task-footer .el-button {
  margin-left: 8px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.points-drawer-content {
  width: 100%;
  height: 100%;
  min-height: 600px;
  overflow: auto;
}

.task-log {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 768px) {
  .task-header-info {
    flex-direction: column;
  }

  .task-meta {
    margin-top: 8px;
  }

  .task-progress {
    flex-direction: column;
    align-items: flex-start;
  }

  .task-time-info {
    flex-direction: column;
    gap: 6px;
  }

  .task-footer {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .task-footer .el-button {
    margin-bottom: 8px;
  }
}
</style>