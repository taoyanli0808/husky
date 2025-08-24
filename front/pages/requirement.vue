<template>
  <div>
    <!-- 顶部区域 -->
    <div class="top-section">
      <div class="container">
        <div class="top-content">
  <div class="left-text">需求列表</div>
  <div class="right-button">
    <upload-requirement @uploadSuccess="searchRequires" />
  </div>
</div>
      </div>
    </div>
    <div v-if="loading" class="loading" v-loading="loading"></div>
    <div v-else-if="requires.length === 0" class="empty-state">
      <el-empty description="暂无需求数据"></el-empty>
    </div>
    <div v-else class="require-list">
      <div v-for="row in requires" :key="row.require_id" class="require-item">
        <div class="require-header">
          <div class="require-title">
            <el-input v-if="row.editing" v-model="row.require_name" placeholder="请输入需求名称" />
            <h3 v-else>{{ row.require_name }}</h3>
          </div>
          <div class="require-meta">
            <span class="require-id">{{ row.require_id }}</span>
          </div>
        </div>
        
        <div class="require-body">
          <div class="require-basic-info">
            <span class="basic-info-item">业务领域：{{ row.business_domain }}</span>
            <span class="basic-info-item">所属模块：{{ row.module }}</span>
          </div>
          
          <div class="require-description">
            <el-input v-if="row.editing" v-model="row.description" type="textarea" placeholder="请输入需求描述" />
            <p v-else class="small-description">需求描述：{{ row.description }}</p>
          </div>
          
          <div class="require-tags">
            <template v-if="Array.isArray(row.tags)">
              <el-tag v-for="(tag, index) in row.tags" :key="index" size="mini" style="margin-right: 5px;">
                {{ tag }}
              </el-tag>
            </template>
          </div>
        </div>
        
        <div class="require-footer">
          <div class="require-footer-meta">
            <span class="require-time">创建: {{ row.created_at | formatDate }}</span>
            <span class="require-time">更新: {{ row.updated_at | formatDate }}</span>
          </div>
          <el-button-group>
            <el-button 
              type="primary" 
              size="mini" 
              @click="toggleEdit(row)">
              {{ row.editing ? '保存' : '编辑' }}
            </el-button>
            <el-button 
              type="success" 
              size="mini" 
              @click="analysisRequirements(row)">
              分析
            </el-button>
            <el-button 
              type="danger" 
              size="mini" 
              @click="deleteRequire(row)">
              删除
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
import request from '@/utils/request'
import UploadRequirement from '@/components/UploadRequirement.vue'

export default {
  components: {
    UploadRequirement
  },
  filters: {
    formatDate(value) {
      if (!value) return ''
      const date = new Date(value)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  },
  data() {
    return {
      requires: [],
      loading: false
    }
  },
  mounted() {
    this.searchRequires()
  },
  methods: {
    
    getScoreType(score) {
      if (score >= 4) return 'success'
      if (score >= 3) return 'warning'
      return 'danger'
    },
    
    async searchRequires() {
      console.log('开始请求需求数据...')
      this.loading = true
      try {
        const res = await request.post('/api/v1/require/search')
        console.log('请求结果:', res)
        if (res.code === 0) {
          this.requires = res.data.map(item => {
            // 计算总分（quality_score各项的平均值）
            const scores = Object.values(item.quality_score)
            const total = scores.reduce((sum, score) => sum + score, 0) / scores.length
            
            return {
              ...item,
              total_score: total.toFixed(1), // 保留1位小数
              editing: false,
              originalData: JSON.parse(JSON.stringify(item))
            }
          })
        } else {
          this.$message.warning(res.message)
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '获取需求列表失败')
      } finally {
        this.loading = false
      }
    },
    
    toggleEdit(row) {
      if (row.editing) {
        // 保存逻辑
        this.saveRequire(row)
      } else {
        // 进入编辑模式
        row.editing = true
      }
    },
    
    async saveRequire(row) {
      try {
        const { require_id, require_name, description, quality_score } = row
        const res = await request.post('/api/v1/require/update', {
          require_id,
          require_name,
          description,
          quality_score
        })
        
        if (res.code === 0) {
          this.$message.success('需求更新成功')
          row.editing = false
          row.originalData = JSON.parse(JSON.stringify(row))
        } else {
          this.$message.warning(res.message)
          // 恢复原始数据
          Object.assign(row, JSON.parse(JSON.stringify(row.originalData)))
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '更新需求失败')
        Object.assign(row, JSON.parse(JSON.stringify(row.originalData)))
      }
    },
    
    async analysisRequirements(row) {
      try {
        this.loading = true;
        
        // 调用服务端分析接口
        const res = await request.post('/api/v1/point/analysis', {
          require_id: row.require_id
        });
        
        if (res.code === 0) {
          // 获取到task_id后进行跳转
          this.$router.push({
            path: '/tasks',
            query: {
              task_id: res.data.task_id,
              require_id: row.require_id
            }
          });
        } else {
          this.$message.warning(res.message || '需求分析失败');
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '需求分析请求失败');
      } finally {
        this.loading = false;
      }
    },
    
    async deleteRequire(row) {
      try {
        await this.$confirm(`确认删除需求 "${row.require_name}"?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const res = await request.post('/api/v1/require/delete', {
          require_id: row.require_id
        })
        
        if (res.code === 0) {
          this.$message.success('需求删除成功')
          this.searchRequires()
        } else {
          this.$message.warning(res.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(error.response?.data?.message || '删除需求失败')
        }
      }
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

.require-list {
  margin-top: 20px;
}

.require-item {
  padding: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.require-item:hover {
  background-color: #f9f9f9;
}

.require-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.require-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  cursor: pointer;
}

.require-title h3:hover {
  color: #1890ff;
}

.require-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 12px;
  color: #999;
}

.require-id {
  margin-bottom: 4px;
  background-color: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.require-time {
  margin-bottom: 2px;
}

.require-body {
  margin-bottom: 16px;
}

.require-basic-info {
  margin-bottom: 12px;
}

.require-basic-info .basic-info-item {
  margin-right: 12px;
  margin-bottom: 8px;
  display: inline-block;
  font-size: 12px;
}

.small-description {
  margin: 0;
  color: #666;
  line-height: 1.6;
  word-break: break-all;
  font-size: 12px;
}

.require-description p {
  margin: 0;
  color: #666;
  line-height: 1.6;
  word-break: break-all;
}

.require-tags {
  margin-top: 12px;
}

.require-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.require-footer-meta {
  font-size: 12px;
  color: #999;
}

.require-footer-meta .require-time {
  margin-right: 12px;
}

.require-footer .el-button {
  margin-left: 8px;
}

@media (max-width: 768px) {
  .require-header {
    flex-direction: column;
  }

  .require-meta {
    align-items: flex-start;
    margin-top: 8px;
  }

  .require-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .require-footer-meta {
    margin-bottom: 10px;
  }

  .require-footer .el-button {
    margin-bottom: 8px;
  }
}
/* 顶部区域样式 */
.top-section {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 15px 0;
  margin-bottom: 20px;
}

.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-text {
  font-size: 18px;
  font-weight: bold;
  color: #304156;
}

/* 上传弹框样式 */
.status-alert {
  margin-top: 15px;
  z-index: 1000;
}

.el-upload__tip {
  margin-top: 8px;
  color: #999;
  font-size: 12px;
}
</style>

<!-- 上传需求弹框 -->
<el-dialog
  title="上传需求文档"
  :visible.sync="uploadDialogVisible"
  width="50%"
  top="15vh"
>
  <el-upload
    ref="uploadRef"
    class="upload-demo"
    name="file"
    :limit="1"
    :action="uploadUrl"
    :multiple="false"
    :on-success="handleUploadSuccess"
    :on-error="handleUploadError"
    :on-exceed="handleExceed"
    :before-upload="beforeUpload"
    :auto-upload="true"
    :show-file-list="false"
  >
    <el-button size="medium" type="primary">点击上传</el-button>
    <div slot="tip" class="el-upload__tip">支持上传PDF/Markdown文件，单文件最大10MB</div>
  </el-upload>
  <el-alert
    v-if="uploadStatus.show"
    :title="uploadStatus.message"
    :type="uploadStatus.type"
    show-icon
    class="status-alert"
  />

  <span slot="footer" class="dialog-footer">
    <el-button @click="uploadDialogVisible = false">取 消</el-button>
  </span>
</el-dialog>