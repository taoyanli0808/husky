const state = {
  taskList: [],
  currentTask: null,
  loading: false,
  pagination: {
    current: 1,
    size: 10,
    total: 0
  }
}

const mutations = {
  SET_TASK_LIST(state, list) {
    state.taskList = list
  },
  SET_CURRENT_TASK(state, task) {
    state.currentTask = task
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_PAGINATION(state, pagination) {
    state.pagination = pagination
  }
}

const actions = {
  async fetchTaskList({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/task/list', params)
      if (response.data.code === 0) {
        commit('SET_TASK_LIST', response.data.data.list)
        commit('SET_PAGINATION', {
          current: response.data.data.current,
          size: response.data.data.size,
          total: response.data.data.total
        })
      }
      return response.data
    } catch (error) {
      console.error('获取任务列表失败:', error)
      this.$message.error('获取任务列表失败')
      return { code: -1, message: '获取任务列表失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchTaskDetail({ commit }, taskId) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/task/detail', { task_id: taskId })
      if (response.data.code === 0) {
        commit('SET_CURRENT_TASK', response.data.data)
      }
      return response.data
    } catch (error) {
      console.error('获取任务详情失败:', error)
      this.$message.error('获取任务详情失败')
      return { code: -1, message: '获取任务详情失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}