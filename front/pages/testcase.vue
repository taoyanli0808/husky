<template>
    <el-table :data="testcases" @cell-dblclick="handleDoubleClick">
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="case_id" label="ID">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.case_id"
            @blur="saveEdit(row)"
            autofocus
          />
          <span v-else>{{ row.case_id }}</span>
        </template>
      </el-table-column>
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="case_name" label="用例名称">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.case_name"
            @blur="saveEdit(row)"
            autofocus
          />
          <span v-else>{{ row.case_name }}</span>
        </template>
      </el-table-column>
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="precondition" label="前置条件">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.precondition"
            @blur="saveEdit(row)"
            autofocus
          />
          <span v-else>{{ row.precondition }}</span>
        </template>
      </el-table-column>
      <!-- 名称列（双击编辑） -->
      <el-table-column prop="test_steps" label="测试步骤">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.test_steps"
            @blur="saveEdit(row)"
            autofocus
          />
          <span v-else>{{ row.test_steps }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="expected_result" label="预期结果">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.expected_result"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.expected_result }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="priority" label="优先级">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.priority"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.priority }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="test_type" label="测试类型">
        <template #default="{ row }">
          <el-input
            v-if="row.editing"
            v-model="row.test_type"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.test_type }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="create" label="是否用户添加">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.create"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.create }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="modify" label="是否修改">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.modify"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.modify }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="accept" label="是否采纳">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.accept"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.accept }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="review" label="是否评审">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.review"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.review }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="verify" label="测试通过">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.verify"
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.verify }}</span>
        </template>
      </el-table-column>
      <!-- 年龄列（带数字校验） -->
      <el-table-column prop="created_at" label="创建时间">
        <template #default="{ row }">
          <el-input-number
            v-if="row.editing"
            v-model="row.created_at"
            :min="0"
            @blur="saveEdit(row)"
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
            :min="0"
            @blur="saveEdit(row)"
          />
          <span v-else>{{ row.updated_at }}</span>
        </template>
      </el-table-column>
      <!-- 操作列 -->
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button type="primary" @click="toggleEdit(row)" size="small">
            {{ row.editing ? '保存' : '编辑' }}
          </el-button>
          <el-button type="primary" @click="deleteTestcase(row)" size="small">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </template>
  
  <script>
  export default {
    data() {
      return {
        testcases: []
      }
    },
    mounted() {
      this.searchTestcases()
    },
    methods: {
      // 双击单元格进入编辑
      handleDoubleClick(row, column) {
        if (!row.editing) {
          this.$set(row, 'editing', true)
        }
      },
      // 保存修改（自动触发）
      saveEdit(row) {
        row.editing = false
        console.log('自动保存:', row)
        this.$axios({
          url: '/api/v1/testcase/update',
          method: 'post',
          data: row,
          headers: {
            'Content-Type': 'application/json;'
          }
        }).then((res) => {
          console.log(res)
          if (res.data.code === 0) {
            this.$message({
              type: 'info',
              message: res.data.message,
              center: true
            })
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
      // 按钮切换编辑状态
      toggleEdit(row) {
        row.editing = !row.editing
        if (!row.editing) {
          this.saveEdit(row)
        }
      },
      searchTestcases() {
        const require_id = this.$route.query.require_id
        this.$axios({
          url: '/api/v1/testcase/search',
          method: 'post',
          data: {'require_id': require_id},
          headers: {
            'Content-Type': 'application/json;'
          }
        }).then((res) => {
          console.log(res)
          if (res.data.code === 0) {
            this.testcases = res.data.data
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
      deleteTestcase(row) {
        this.$axios({
          url: '/api/v1/testcase/delete',
          method: 'post',
          data: {'case_id': row.case_id},
          headers: {
            'Content-Type': 'application/json;'
          }
        }).then((res) => {
          this.$message({
            type: 'warning',
            message: res.data.message,
            center: true
          })
          this.searchTestcases()
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