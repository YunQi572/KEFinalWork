<template>
  <div class="knowledge-graph">
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'KnowledgeGraph',
  props: {
    nodes: {
      type: Array,
      required: true,
      default: () => []
    },
    links: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  emits: ['node-click', 'edge-click'],
  setup(props, { emit }) {
    const chartContainer = ref(null)
    let chartInstance = null

    // 初始化图表
    const initChart = () => {
      if (!chartContainer.value) return

      chartInstance = echarts.init(chartContainer.value)
      
      const option = {
        title: {
          text: '松材线虫病知识图谱',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 20,
            fontWeight: 'bold',
            color: '#333'
          }
        },
        tooltip: {
          formatter: (params) => {
            if (params.dataType === 'node') {
              return `<b>实体:</b> ${params.data.name}`
            } else if (params.dataType === 'edge') {
              return `<b>关系:</b> ${params.data.value}<br/>
                      <b>源:</b> ${params.data.source}<br/>
                      <b>目标:</b> ${params.data.target}`
            }
            return ''
          }
        },
        series: [{
          type: 'graph',
          layout: 'force',
          data: [],
          links: [],
          roam: true,
          label: {
            show: true,
            position: 'right',
            formatter: '{b}',
            fontSize: 12
          },
          edgeLabel: {
            show: true,
            formatter: '{c}',
            fontSize: 10,
            color: '#666'
          },
          labelLayout: {
            hideOverlap: true
          },
          force: {
            repulsion: 300,
            edgeLength: [100, 200],
            gravity: 0.1
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 3
            },
            label: {
              fontSize: 14,
              fontWeight: 'bold'
            }
          },
          lineStyle: {
            color: 'source',
            curveness: 0.3,
            width: 2
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1,
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          },
          categories: [
            { name: '实体', itemStyle: { color: '#5470c6' } }
          ]
        }]
      }

      chartInstance.setOption(option)

      // 添加点击事件监听
      chartInstance.on('click', (params) => {
        if (params.dataType === 'node') {
          emit('node-click', params.data)
        } else if (params.dataType === 'edge') {
          emit('edge-click', params.data)
        }
      })

      // 窗口大小变化时自适应
      window.addEventListener('resize', handleResize)
    }

    // 更新图表数据
    const updateChart = () => {
      if (!chartInstance) return

      // 为节点添加样式配置
      const nodesWithStyle = props.nodes.map(node => ({
        ...node,
        symbolSize: 40,
        category: 0
      }))

      chartInstance.setOption({
        series: [{
          data: nodesWithStyle,
          links: props.links
        }]
      })
    }

    // 处理窗口大小变化
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }

    // 监听数据变化
    watch(
      () => [props.nodes, props.links],
      () => {
        updateChart()
      },
      { deep: true }
    )

    onMounted(() => {
      initChart()
      updateChart()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize)
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
    })

    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.knowledge-graph {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 500px;
}
</style>
