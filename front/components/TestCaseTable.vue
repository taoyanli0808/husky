<template>
  <el-table
    :data="testcases"
    v-loading="loading"
    border
    style="width: 100%"
  >
    <el-table-column prop="case_id" label="用例ID" width="150"></el-table-column>
    <el-table-column prop="case_name" label="用例名称">
      <template slot-scope="scope">
        <strong>{{ scope.row.case_name }}</strong>
      </template>
    </el-table-column>
    <el-table-column prop="priority" label="优先级" width="100">
      <template slot-scope="scope">
        <el-tag
          :type="
            scope.row.priority === 'P0'
              ? 'danger'
              : scope.row.priority === 'P1'
              ? 'warning'
              : scope.row.priority === 'P2'
              ? 'primary'
              : 'success'
          "
        >
          {{ scope.row.priority }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="test_type" label="测试类型" width="150">
      <template slot-scope="scope">
        <div v-if="Array.isArray(scope.row.test_type)">
          <el-tag
            v-for="(item, index) in scope.row.test_type"
            :key="index"
            size="small"
            style="margin-right: 5px; margin-bottom: 5px"
          >
            {{ item }}
          </el-tag>
        </div>
        <span v-else>-</span>
      </template>
    </el-table-column>
    <el-table-column prop="preconditions" label="前置条件">
      <template slot-scope="scope">
        <div v-if="Array.isArray(scope.row.preconditions)">
          <el-tag
            v-for="(item, index) in scope.row.preconditions"
            :key="index"
            size="small"
            style="margin-right: 5px; margin-bottom: 5px"
          >
            {{ item }}
          </el-tag>
        </div>
        <span v-else>-</span>
      </template>
    </el-table-column>
    <el-table-column prop="test_steps" label="操作步骤">
      <template slot-scope="scope">
        <div v-if="Array.isArray(scope.row.test_steps)">
          <ol style="margin: 0; padding-left: 20px">
            <li v-for="(step, index) in scope.row.test_steps" :key="index">
              {{ step }}
            </li>
          </ol>
        </div>
        <span v-else>-</span>
      </template>
    </el-table-column>
    <el-table-column
      prop="expected_result"
      label="预期结果"
    >
      <template slot-scope="scope">
        <div v-if="Array.isArray(scope.row.expected_result)">
          <ul style="margin: 0; padding-left: 20px">
            <li v-for="(result, index) in scope.row.expected_result" :key="index">
              {{ result }}
            </li>
          </ul>
        </div>
        <span v-else>-</span>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  name: 'TestCaseTable',
  props: {
    testcases: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>