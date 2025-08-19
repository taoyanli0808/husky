const state = {
  pointList: [],
  currentPoint: null,
  loading: false,
  pagination: {
    current: 1,
    size: 10,
    total: 0
  },
  activeTask: null,
  progressSteps: [
    { desc: '等待开始', completed: false },
    { desc: '等待开始', completed: false },
    { desc: '等待开始', completed: false },
    { desc: '等待开始', completed: false }
  ]
}

const mutations = {
  SET_POINT_LIST(state, list) {
    state.pointList = list
  },
  SET_CURRENT_POINT(state, point) {
    state.currentPoint = point
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_PAGINATION(state, pagination) {
    state.pagination = pagination
  },
  SET_ACTIVE_TASK(state, task) {
    state.activeTask = task
  },
  UPDATE_PROGRESS_STEPS(state, steps) {
    state.progressSteps = steps
  }
}

const actions = {
  async fetchPointList({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/point/list', params)
      if (response.data.code === 0) {
        commit('SET_POINT_LIST', response.data.data.list)
        commit('SET_PAGINATION', {
          current: response.data.data.current,
          size: response.data.data.size,
          total: response.data.data.total
        })
      }
      return response.data
    } catch (error) {
      console.error('获取测试点列表失败:', error)
      this.$message.error('获取测试点列表失败')
      return { code: -1, message: '获取测试点列表失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createPoint({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/point/create', data)
      if (response.data.code === 0) {
        this.$message.success('测试点创建成功')
      }
      return response.data
    } catch (error) {
      console.error('创建测试点失败:', error)
      this.$message.error('创建测试点失败')
      return { code: -1, message: '创建测试点失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updatePoint({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/point/update', data)
      if (response.data.code === 0) {
        this.$message.success('测试点更新成功')
      }
      return response.data
    } catch (error) {
      console.error('更新测试点失败:', error)
      this.$message.error('更新测试点失败')
      return { code: -1, message: '更新测试点失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deletePoint({ commit }, pointId) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/point/delete', { point_id: pointId })
      if (response.data.code === 0) {
        this.$message.success('测试点删除成功')
      }
      return response.data
    } catch (error) {
      console.error('删除测试点失败:', error)
      this.$message.error('删除测试点失败')
      return { code: -1, message: '删除测试点失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async analysisPoint({ commit }, requireId) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/point/analysis', { require_id: requireId })
      if (response.data.code === 0) {
        commit('SET_ACTIVE_TASK', response.data.data)
        this.$message.success('需求分析任务已启动')
      }
      return response.data
    } catch (error) {
      console.error('启动需求分析失败:', error)
      this.$message.error('启动需求分析失败')
      return { code: -1, message: '启动需求分析失败' }
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