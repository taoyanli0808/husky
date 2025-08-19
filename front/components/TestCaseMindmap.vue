<template>
  <div :id="chartId" class="mindmap-container" :style="{ height: height + 'px' }"></div>
</template>

<script>
import echarts from 'echarts'

export default {
  name: 'TestCaseMindmap',
  props: {
    testcases: {
      type: Array,
      required: true
    },
    height: {
      type: Number,
      default: 800
    }
  },
  data() {
    return {
      chartId: 'mindmap-' + Math.random().toString(36).substr(2, 9),
      chartInstance: null
    }
  },
  watch: {
    testcases: {
      handler(newVal) {
        if (this.chartInstance && newVal.length > 0) {
          this.updateMindmap()
        }
      },
      deep: true
    }
  },
  mounted() {
    if (this.testcases.length > 0) {
      this.initMindmap()
    }
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.dispose()
      this.chartInstance = null
    }
  },
  methods: {
    initMindmap() {
      this.chartInstance = echarts.init(document.getElementById(this.chartId))
      this.updateMindmap()

      // 监听窗口大小变化，重新调整图表大小
      window.addEventListener('resize', this.handleResize)
    },

    updateMindmap() {
      if (!this.chartInstance) return

      // 构建脑图数据
      const mindmapData = this.buildMindmapData()

      // 配置脑图选项
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}'
        },
        series: [{
          type: 'graph',
          layout: 'force',
          animation: true,
          data: mindmapData.nodes,
          links: mindmapData.links,
          categories: mindmapData.categories,
          roam: true,
          label: {
            show: true,
            position: 'right',
            formatter: '{b}',
            fontSize: 12,
            color: '#333'
          },
          lineStyle: {
            color: 'source',
            curveness: 0.3
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 4
            }
          },
          force: {
            repulsion: 1200,
            edgeLength: [60, 120],
            layoutAnimation: true
          }
        }]
      }

      this.chartInstance.setOption(option)
    },

    buildMindmapData() {
      const nodes = []
      const links = []
      const categories = [
        { name: '根节点' },
        { name: '测试用例' },
        { name: '前置条件' },
        { name: '操作步骤' },
        { name: '预期结果' },
        { name: '优先级' }
      ]

      // 添加根节点
      nodes.push({
        id: 'root',
        name: '测试用例集',
        category: 0,
        symbolSize: 60,
        itemStyle: { color: '#409EFF' }
      })

      // 添加测试用例节点和关系
      this.testcases.forEach((caseItem, index) => {
        const caseId = 'case-' + index
        nodes.push({
          id: caseId,
          name: caseItem.case_name,
          category: 1,
          symbolSize: 45,
          itemStyle: {
            color: this.getPriorityColor(caseItem.priority)
          }
        })

        // 连接根节点和测试用例
        links.push({
          source: 'root',
          target: caseId
        })

        // 添加优先级节点
        const priorityId = 'priority-' + index
        nodes.push({
          id: priorityId,
          name: '优先级: ' + caseItem.priority,
          category: 5,
          symbolSize: 30,
          itemStyle: {
            color: this.getPriorityColor(caseItem.priority)
          }
        })

        // 连接测试用例和优先级
        links.push({
          source: caseId,
          target: priorityId
        })

        // 添加前置条件节点
        if (Array.isArray(caseItem.preconditions) && caseItem.preconditions.length > 0) {
          const preconditionId = 'precondition-' + index
          nodes.push({
            id: preconditionId,
            name: '前置条件',
            category: 2,
            symbolSize: 30,
            itemStyle: { color: '#67C23A' }
          })

          links.push({
            source: caseId,
            target: preconditionId
          })

          caseItem.preconditions.forEach((condition, condIndex) => {
            const condId = 'cond-' + index + '-' + condIndex
            nodes.push({
              id: condId,
              name: condition,
              category: 2,
              symbolSize: 20,
              itemStyle: { color: '#67C23A' }
            })

            links.push({
              source: preconditionId,
              target: condId
            })
          })
        }

        // 添加操作步骤节点
        if (Array.isArray(caseItem.test_steps) && caseItem.test_steps.length > 0) {
          const stepId = 'step-' + index
          nodes.push({
            id: stepId,
            name: '操作步骤',
            category: 3,
            symbolSize: 30,
            itemStyle: { color: '#E6A23C' }
          })

          links.push({
            source: caseId,
            target: stepId
          })

          caseItem.test_steps.forEach((step, stepIndex) => {
            const stepDetailId = 'stepdetail-' + index + '-' + stepIndex
            nodes.push({
              id: stepDetailId,
              name: `${stepIndex + 1}. ${step}`,
              category: 3,
              symbolSize: 20,
              itemStyle: { color: '#E6A23C' }
            })

            links.push({
              source: stepId,
              target: stepDetailId
            })
          })
        }

        // 添加预期结果节点
        if (Array.isArray(caseItem.expected_result) && caseItem.expected_result.length > 0) {
          const resultId = 'result-' + index
          nodes.push({
            id: resultId,
            name: '预期结果',
            category: 4,
            symbolSize: 30,
            itemStyle: { color: '#F56C6C' }
          })

          links.push({
            source: caseId,
            target: resultId
          })

          caseItem.expected_result.forEach((result, resultIndex) => {
            const resultDetailId = 'resultdetail-' + index + '-' + resultIndex
            nodes.push({
              id: resultDetailId,
              name: result,
              category: 4,
              symbolSize: 20,
              itemStyle: { color: '#F56C6C' }
            })

            links.push({
              source: resultId,
              target: resultDetailId
            })
          })
        }
      })

      return {
        nodes,
        links,
        categories
      }
    },

    getPriorityColor(priority) {
      switch (priority) {
        case 'P0': return '#F56C6C'
        case 'P1': return '#E6A23C'
        case 'P2': return '#409EFF'
        default: return '#67C23A'
      }
    },

    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    }
  }
}
</script>

<style scoped>
.mindmap-container {
  width: 100%;
  overflow: hidden;
}
</style>