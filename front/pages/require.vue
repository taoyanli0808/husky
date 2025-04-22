<template>
    <el-table :data="requires">
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="require_id" label="ID">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.require_id"
          />
          <span v-else>{{ row.require_id }}</span>
        </template>
      </el-table-column>
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="require_name" label="需求名称">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.require_name"
          />
          <span v-else>{{ row.require_name }}</span>
        </template>
      </el-table-column>
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="summary" label="需求摘要">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.summary"
          />
          <span v-else>{{ row.summary }}</span>
        </template>
      </el-table-column>
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="content" label="需求原文">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.content"
          />
          <span v-else>{{ row.content }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="images" label="图片集合">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.images"
          />
          <span v-else>{{ row.images }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="version" label="需求版本">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.version"
          />
          <span v-else>{{ row.version }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="owner" label="需求负责人">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.owner"
          />
          <span v-else>{{ row.owner }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="completeness" label="完整性">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.completeness"
          />
          <span v-else>{{ row.completeness }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="testability" label="可测性">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.testability"
          />
          <span v-else>{{ row.testability }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="clarity" label="清晰度">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.clarity"
          />
          <span v-else>{{ row.clarity }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="consistency" label="一致性">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.consistency"
          />
          <span v-else>{{ row.consistency }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="total_score" label="需求总分">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.total_score"
          />
          <span v-else>{{ row.total_score }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="issues" label="问题明细">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
          />
          <span v-else>{{ row.issues }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="created_at" label="创建时间">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.created_at"
          />
          <span v-else>{{ row.created_at }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="updated_at" label="修改时间">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.updated_at"
          />
          <span v-else>{{ row.updated_at }}</span>
        </template>
      </el-table-column>
      <!-- 操作列 -->
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button type="primary" @click="generateTestcase(row)" size="small">
            生成用例
          </el-button>
          <el-button type="primary" @click="deleteRequire(row)" size="small">
            删除需求
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </template>
  
  <script>
  export default {
    data() {
      return {
        requires: []
      }
    },
    mounted() {
      this.searchRequires()
    },
    methods: {
      searchRequires() {
        this.$axios({
          url: '/api/v1/require/search',
          method: 'post',
          data: {},
          headers: {
            'Content-Type': 'application/json;'
          }
        }).then((res) => {
          console.log(res)
          if (res.data.code === 0) {
            this.requires = res.data.data
          } else {
            this.$message({
              type: 'warning',
              message: res.data.message,
              center: true
            })
          }
        }).catch((error) => {
          this.$message({
            type: 'error',
            message: error.response.data.message,
            center: true
          })
        })
      },
      generateTestcase (row) {
        this.$axios({
          url: '/api/v1/testcase/create',
          method: 'post',
          data: {'require_id': row.require_id},
          headers: {
            'Content-Type': 'application/json;'
          }
        }).then((res) => {
            this.$message({
              type: 'warning',
              message: res.data.message,
              center: true
            })
            // this.searchRequires()
        }).catch((error) => {
          this.$message({
            type: 'error',
            message: error.response.data.message,
            center: true
          })
        })
      },
      deleteRequire(row) {
        this.$axios({
          url: '/api/v1/require/delete',
          method: 'post',
          data: {'require_id': row.require_id},
          headers: {
            'Content-Type': 'application/json;'
          }
        }).then((res) => {
            this.$message({
              type: 'warning',
              message: res.data.message,
              center: true
            })
            this.searchRequires()
        }).catch((error) => {
          this.$message({
            type: 'error',
            message: error.response.data.message,
            center: true
          })
        })
      }
    }
  }
  </script>