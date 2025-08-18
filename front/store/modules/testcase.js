const state = {
  testcaseList: [],
  currentTestcase: null,
  loading: false,
  pagination: {
    current: 1,
    size: 10,
    total: 0
  },
  taskId: '',
  requireId: '',
  taskStatus: null,
  taskMessage: '',
  progressSteps: [
    { desc: '等待开始', completed: false },
    { desc: '等待开始', completed: false },
    { desc: '等待开始', completed: false },
    { desc: '等待开始', completed: false }
  ]
}

const mutations = {
  SET_TESTCASE_LIST(state, list) {
    state.testcaseList = list
  },
  SET_CURRENT_TESTCASE(state, testcase) {
    state.currentTestcase = testcase
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_PAGINATION(state, pagination) {
    state.pagination = pagination
  },
  SET_TASK_ID(state, taskId) {
    state.taskId = taskId
  },
  SET_REQUIRE_ID(state, requireId) {
    state.requireId = requireId
  },
  SET_TASK_STATUS(state, status) {
    state.taskStatus = status
  },
  SET_TASK_MESSAGE(state, message) {
    state.taskMessage = message
  },
  UPDATE_PROGRESS_STEPS(state, steps) {
    state.progressSteps = steps
  }
}

const actions = {
  async fetchTestcaseList({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/testcase/list', params)
      if (response.data.code === 0) {
        commit('SET_TESTCASE_LIST', response.data.data.list)
        commit('SET_PAGINATION', {
          current: response.data.data.current,
          size: response.data.data.size,
          total: response.data.data.total
        })
      }
      return response.data
    } catch (error) {
      console.error('获取测试用例列表失败:', error)
      this.$message.error('获取测试用例列表失败')
      return { code: -1, message: '获取测试用例列表失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async generateTestcases({ commit }, pointIds) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/testcase/generate', { point_ids: pointIds })
      if (response.data.code === 0) {
        commit('SET_TASK_ID', response.data.data.task_id)
        this.$message.success('测试用例生成任务已启动')
      }
      return response.data
    } catch (error) {
      console.error('启动测试用例生成失败:', error)
      this.$message.error('启动测试用例生成失败')
      return { code: -1, message: '启动测试用例生成失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchTaskStatus({ commit }, taskId) {
    try {
      const response = await this.$axios.post('/api/v1/task/status', { task_id: taskId })
      if (response.data.code === 0) {
        commit('SET_TASK_STATUS', response.data.data)
        commit('SET_TASK_MESSAGE', response.data.data.message)

        // 更新进度步骤
        const steps = [...state.progressSteps]
        if (response.data.data.progress >= 25) {
          steps[0] = { desc: '测试点分析完成', completed: true }
        }
        if (response.data.data.progress >= 50) {
          steps[1] = { desc: '用例设计完成', completed: true }
        }
        if (response.data.data.progress >= 75) {
          steps[2] = { desc: '优先级排序完成', completed: true }
        }
        if (response.data.data.progress >= 100) {
          steps[3] = { desc: '生成完成', completed: true }
        }
        commit('UPDATE_PROGRESS_STEPS', steps)
      }
      return response.data
    } catch (error) {
      console.error('获取任务状态失败:', error)
      return { code: -1, message: '获取任务状态失败' }
    }
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}