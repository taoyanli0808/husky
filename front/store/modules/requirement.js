const state = {
  requirementList: [],
  currentRequirement: null,
  loading: false,
  pagination: {
    current: 1,
    size: 10,
    total: 0
  }
}

const mutations = {
  SET_REQUIREMENT_LIST(state, list) {
    state.requirementList = list
  },
  SET_CURRENT_REQUIREMENT(state, requirement) {
    state.currentRequirement = requirement
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_PAGINATION(state, pagination) {
    state.pagination = pagination
  }
}

const actions = {
  async fetchRequirementList({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/require/search', params)
      if (response.data.code === 0) {
        commit('SET_REQUIREMENT_LIST', response.data.data)
        // 假设API返回分页信息，如果没有则需要调整
        commit('SET_PAGINATION', {
          current: 1,
          size: response.data.data.length,
          total: response.data.data.length
        })
      }
      return response.data
    } catch (error) {
      console.error('获取需求列表失败:', error)
      this.$message.error('获取需求列表失败')
      return { code: -1, message: '获取需求列表失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async updateRequirement({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/require/update', data)
      if (response.data.code === 0) {
        this.$message.success('需求更新成功')
      }
      return response.data
    } catch (error) {
      console.error('更新需求失败:', error)
      this.$message.error('更新需求失败')
      return { code: -1, message: '更新需求失败' }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteRequirement({ commit }, requireId) {
    commit('SET_LOADING', true)
    try {
      const response = await this.$axios.post('/api/v1/require/delete', { require_id: requireId })
      if (response.data.code === 0) {
        this.$message.success('需求删除成功')
      }
      return response.data
    } catch (error) {
      console.error('删除需求失败:', error)
      this.$message.error('删除需求失败')
      return { code: -1, message: '删除需求失败' }
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