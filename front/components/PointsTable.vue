<template>
  <div class="points-table-container">
    <el-card class="table-card">
    <div class="table-header">
      <h3>测试点列表</h3>
      <div>
        <el-button 
          type="primary" 
          @click="handleGenerateTestCases"
          :disabled="selectedPoints.length === 0"
        >
          生成测试用例
        </el-button>
        <el-button type="primary" @click="handleCreate">新增测试点</el-button>
      </div>
    </div>

  <el-table
    ref="table"
    :data="pointsData"
    border
    style="width: 100%"
    v-loading="loading"
    @selection-change="handleSelectionChange"
  >
    <!-- 添加这个选择列 -->
    <el-table-column type="selection" width="55" align="center"/>
    <el-table-column prop="module" label="模块" width="120" />
    <el-table-column prop="function_name" label="功能名称" width="150" />
    <el-table-column prop="description" label="功能描述">
      <template #default="{ row }">
        <div class="test-points-content">
          {{ row.description }}
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="test_type" label="测试类型" width="120">
      <template #default="{ row }">
        <el-tag :type="getTestTypeTag(row.test_type)">
          {{ row.test_type }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="前置条件" width="180">
      <template #default="{ row }">
        <div v-if="row.preconditions && row.preconditions.length">
          <el-tag 
            v-for="(precond, index) in row.preconditions" 
            :key="index"
            size="small"
            style="margin-right: 5px; margin-bottom: 5px;"
          >
            {{ precond }}
          </el-tag>
        </div>
        <span v-else>无</span>
      </template>
    </el-table-column>
    <el-table-column prop="business_domain" label="业务领域" width="120" />
    <el-table-column prop="created_at" label="创建时间" width="180">
      <template #default="{ row }">
        {{ formatDate(row.created_at) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="180" fixed="right">
      <template #default="{ row }">
        <el-button-group>
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(row)"
          >删除</el-button>
        </el-button-group>
      </template>
    </el-table-column>
  </el-table>


      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
<el-dialog
  v-model="dialogVisible"
  :title="dialogTitle"
  width="50%"
>
  <el-form :model="form" label-width="100px">
    <!-- 需求ID字段（如果需要显示） -->
    <el-form-item label="需求ID" v-if="form.require_id">
      <el-input v-model="form.require_id" disabled />
    </el-form-item>
    
    <!-- 需求名称字段（如果需要显示） -->
    <el-form-item label="需求名称" v-if="form.require_name">
      <el-input v-model="form.require_name" disabled />
    </el-form-item>
    
    <!-- 模块字段 -->
    <el-form-item label="模块" required>
      <el-input v-model="form.module" />
    </el-form-item>
    
    <!-- 功能名称字段 -->
    <el-form-item label="功能名称" required>
      <el-input v-model="form.function_name" />
    </el-form-item>
    
    <!-- 前置条件字段 -->
    <el-form-item label="前置条件">
      <el-input
        v-model="form.preconditions"
        type="textarea"
        :rows="2"
        placeholder="多个条件用换行分隔"
      />
    </el-form-item>
    
    <!-- 功能描述字段 -->
    <el-form-item label="功能描述" required>
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="5"
        placeholder="请输入功能描述"
      />
    </el-form-item>
    
    <!-- 测试类型字段 -->
    <el-form-item label="测试类型" required>
      <el-select v-model="form.test_type" placeholder="请选择测试类型">
        <el-option
          v-for="type in testTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
    </el-form-item>
  </el-form>
  
  <template #footer>
    <span class="dialog-footer">
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitForm">确认</el-button>
    </span>
  </template>
</el-dialog>
  </div>
</template>

<script>
export default {
  name: 'PointsTable',
  props: {
    taskId: {
      type: String,
      required: true
    },
    requireId: {
      type: String,
      default: ''
    },
    requireName: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // 表格数据
      loading: false,
      pointsData: [],
      pagination: {
        current: 1,
        size: 10,
        total: 0
      },
      
      // 对话框相关
      dialogVisible: false,
      dialogTitle: '新增测试点',
      form: {
        point_id: '',
        task_id: '',
        module: '',
        function_name: '',
        description: '',
        test_type: '功能测试',
        preconditions: ''
      },
      testTypes: [
        { value: '功能测试', label: '功能测试' },
        { value: '性能测试', label: '性能测试' },
        { value: '安全测试', label: '安全测试' },
        { value: '兼容性测试', label: '兼容性测试' },
        { value: '用户体验测试', label: '用户体验测试' },
        { value: '其他', label: '其他' }
      ],
      isEdit: false,
      selectedPoints: [], // 存储选中的测试点
    }
  },
  created() {
    this.form.task_id = this.taskId
    this.form.require_id = this.requireId
    this.form.require_name = this.requireName
    this.fetchPointsData()
  },
  methods: {
    // 处理表格选中项变化
    handleSelectionChange(val) {
      this.selectedPoints = val
    },
    
    // 生成测试用例
    async handleGenerateTestCases() {
      if (this.selectedPoints.length === 0) {
        this.$message.warning('请至少选择一个测试点')
        return
      }

      if (!this.form.require_id) {
        this.$message.warning('缺少需求ID，请确保测试点关联到需求')
        return
      }

      try {
        this.loading = true
        const pointIds = this.selectedPoints.map(point => point.point_id)
        
        // 调用新的分析接口
        const res = await this.$axios.post('/api/v1/testcase/analysis', {
          require_id: this.form.require_id,
          point_ids: pointIds  // 传递选中的测试点ID
        })
        
        if (res.data.code === 0) {
          this.$message.success('测试用例分析任务已启动')
          // 跳转到测试用例页面，携带新的task_id和require_id
          this.$router.push({
            path: '/testcases',
            query: {
              task_id: res.data.data.task_id,
              require_id: this.form.require_id
            }
          })
        } else {
          this.$message.warning(res.data.message)
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '启动测试用例分析失败')
      } finally {
        this.loading = false
      }
    },

    // 获取测试点数据
    async fetchPointsData() {
      this.loading = true
      try {
        const res = await this.$axios.post('/api/v1/point/search', {task_id: this.taskId})
        
        if (res.data.code === 0) {
          // 处理返回数据中的preconditions字段
          this.pointsData = res.data.data.list.map(item => {
            return {
              ...item,
              // 确保preconditions是数组格式
              preconditions: Array.isArray(item.preconditions) ? 
                item.preconditions : 
                (typeof item.preconditions === 'string' ? JSON.parse(item.preconditions) : [])
            }
          })
          this.pagination.total = res.data.data.total
        } else {
          this.$message.warning(res.data.message)
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '获取测试点数据失败')
      } finally {
        this.loading = false
      }
    },
    
    // 分页大小变化
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchPointsData()
    },
    
    // 当前页变化
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchPointsData()
    },
    
    handleCreate() {
      this.dialogTitle = '新增测试点'
      this.isEdit = false
      this.form = {
        point_id: '',
        task_id: this.taskId,
        require_id: this.requireId,
        require_name: this.requireName,
        module: '',
        function_name: '',
        description: '',
        test_type: '功能测试',
        preconditions: ''
      }
      this.dialogVisible = true
    },
    
    // 编辑测试点
    handleEdit(row) {
      this.dialogTitle = '编辑测试点'
      this.isEdit = true
      this.form = {
        point_id: row.point_id,
        task_id: row.task_id,
        require_id: row.require_id,
        require_name: row.require_name,
        module: row.module,
        function_name: row.function_name,
        description: row.description,
        test_type: row.test_type,
        preconditions: Array.isArray(row.preconditions) 
          ? row.preconditions.join('\n') 
          : (row.preconditions || '')
      }
      this.dialogVisible = true
    },
    
    // 删除测试点
    handleDelete(row) {
      this.$confirm('确认删除该测试点吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const res = await this.$axios.post('/api/v1/point/delete', { point_id: row.point_id })
          
          if (res.data.code === 0) {
            this.$message.success('删除成功')
            this.fetchPointsData()
          } else {
            this.$message.warning(res.data.message)
          }
        } catch (error) {
          this.$message.error(error.response?.data?.message || '删除失败')
        }
      }).catch(() => {})
    },
    
    // 提交表单
    async submitForm() {
      try {
        // 构建请求数据
        const requestData = {
          ...this.form,
          preconditions: this.form.preconditions 
            ? this.form.preconditions.split('\n').filter(item => item.trim())
            : []
        }
        
        let res
        if (this.isEdit) {
          // 编辑
          res = await this.$axios.post('/api/v1/point/update', requestData)
        } else {
          // 新增
          res = await this.$axios.post('/api/v1/point/create', requestData)
        }
        
        if (res.data.code === 0) {
          this.$message.success(this.isEdit ? '更新成功' : '新增成功')
          this.dialogVisible = false
          this.fetchPointsData()
        } else {
          this.$message.warning(res.data.message)
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '操作失败')
      }
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).replace(/\//g, '-')
    },
    
    // 获取测试类型标签样式
    getTestTypeTag(type) {
      const map = {
        '功能测试': '',
        '性能测试': 'warning',
        '安全测试': 'danger',
        '兼容性测试': 'info',
        '用户体验测试': 'success',
        '其他': 'info'
      }
      return map[type] || 'info'
    }
  }
}
</script>

<style scoped>
.table-card {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.test-points-content {
  white-space: pre-line;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>