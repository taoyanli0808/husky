<template>
  <div class="require-container">
    <el-table :data="requires" border style="width: 100%">
      <!-- 基础信息列 -->
      <el-table-column prop="require_id" label="需求ID" width="180" />
      <el-table-column prop="require_name" label="需求名称" width="180">
        <template #default="{ row }">
          <el-input v-if="row.editing" v-model="row.require_name" />
          <span v-else>{{ row.require_name }}</span>
        </template>
      </el-table-column>
      
      <!-- 分类信息列 -->
      <el-table-column prop="business_domain" label="业务域" width="120" />
      <el-table-column prop="module" label="功能模块" width="150" />
      
      <!-- 内容列 -->
      <el-table-column prop="description" label="需求描述" width="250">
        <template #default="{ row }">
          <el-input v-if="row.editing" v-model="row.description" type="textarea" />
          <span v-else>{{ row.description }}</span>
        </template>
      </el-table-column>
      
      <!-- 质量评分列 -->
      <!-- <el-table-column label="质量评分" width="300">
        <el-table-column prop="quality_score.completeness" label="完整性" width="80">
          <template #default="{ row }">
            <el-rate v-if="row.editing" v-model="row.quality_score.completeness" :max="5" />
            <el-rate v-else :value="row.quality_score.completeness" disabled :max="5" />
          </template>
        </el-table-column>
        <el-table-column prop="quality_score.testability" label="可测性" width="80">
          <template #default="{ row }">
            <el-rate v-if="row.editing" v-model="row.quality_score.testability" :max="5" />
            <el-rate v-else :value="row.quality_score.testability" disabled :max="5" />
          </template>
        </el-table-column>
        <el-table-column prop="quality_score.clarity" label="清晰度" width="80">
          <template #default="{ row }">
            <el-rate v-if="row.editing" v-model="row.quality_score.clarity" :max="5" />
            <el-rate v-else :value="row.quality_score.clarity" disabled :max="5" />
          </template>
        </el-table-column>
        <el-table-column prop="quality_score.consistency" label="一致性" width="80">
          <template #default="{ row }">
            <el-rate v-if="row.editing" v-model="row.quality_score.consistency" :max="5" />
            <el-rate v-else :value="row.quality_score.consistency" disabled :max="5" />
          </template>
        </el-table-column>
      </el-table-column> -->
      
      <!-- 其他信息列 -->
      <!-- <el-table-column prop="total_score" label="总分" width="80">
        <template #default="{ row }">
          <el-tag :type="getScoreType(row.total_score)">
            {{ row.total_score }}
          </el-tag>
        </template>
      </el-table-column> -->
      
      <el-table-column label="标签" width="150">
        <template #default="{ row }">
          <template v-if="Array.isArray(row.tags)">
            <el-tag v-for="(tag, index) in row.tags" :key="index" size="mini" style="margin-right: 5px;">
              {{ tag }}
            </el-tag>
          </template>
        </template>
      </el-table-column>

      <!-- 时间信息列 -->
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ row.created_at }}
        </template>
      </el-table-column>
      
      <el-table-column prop="updated_at" label="更新时间" width="180">
        <template #default="{ row }">
          {{ row.updated_at }}
        </template>
      </el-table-column>
      
      <!-- 操作列 -->
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button 
              type="primary" 
              size="small" 
              @click="toggleEdit(row)">
              {{ row.editing ? '保存' : '编辑' }}
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="analysisRequirements(row)">
              需求分析
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="deleteRequire(row)">
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
  
<script>
export default {
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
      this.loading = true
      try {
        const res = await this.$axios.post('/api/v1/require/search')
        if (res.data.code === 0) {
          this.requires = res.data.data.map(item => {
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
          this.$message.warning(res.data.message)
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
        const res = await this.$axios.post('/api/v1/require/update', {
          require_id,
          require_name,
          description,
          quality_score
        })
        
        if (res.data.code === 0) {
          this.$message.success('需求更新成功')
          row.editing = false
          row.originalData = JSON.parse(JSON.stringify(row))
        } else {
          this.$message.warning(res.data.message)
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
        const res = await this.$axios.post('/api/v1/point/analysis', {
          require_id: row.require_id
        });
        
        if (res.data.code === 0) {
          // 获取到task_id后进行跳转
          this.$router.push({
            path: '/points',
            query: {
              task_id: res.data.data.task_id,
              require_id: row.require_id
            }
          });
        } else {
          this.$message.warning(res.data.message || '需求分析失败');
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
        
        const res = await this.$axios.post('/api/v1/require/delete', {
          require_id: row.require_id
        })
        
        if (res.data.code === 0) {
          this.$message.success('需求删除成功')
          this.searchRequires()
        } else {
          this.$message.warning(res.data.message)
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
.require-container {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.el-table {
  margin-top: 20px;
}

.el-tag {
  margin-right: 5px;
}

.el-rate {
  line-height: 1;
}
</style>