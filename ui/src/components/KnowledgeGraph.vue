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
              // 使用后端返回的category字段判断是否为高级节点
              const isHighLevel = params.data.category === 1
              const levelText = isHighLevel ? '<span style="color: #ff7c00;">(高级节点)</span>' : ''
              return `<b>实体:</b> ${params.data.name} ${levelText}`
            } else if (params.dataType === 'edge') {
              return `<b>关系:</b> ${params.data.value}<br/>
                      <b>源:</b> ${params.data.source}<br/>
                      <b>目标:</b> ${params.data.target}`
            }
            return ''
          }
        },
        legend: {
          data: [
            { name: '普通节点', itemStyle: { color: '#5470c6' } },
            { name: '高级节点', itemStyle: { color: '#ff7c00' } }
          ],
          top: 50
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
            show: false
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
            color: '#c0c4cc',
            curveness: 0.2,
            width: 1.5
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1,
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          },
          categories: [
            { name: '普通节点', itemStyle: { color: '#5470c6' } },
            { name: '高级节点', itemStyle: { color: '#ff7c00' } }
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

      // 为节点添加样式配置，使用后端返回的category字段判断高级节点
      const highLevelSet = new Set(
        props.nodes.filter(n => n.category === 1).map(n => n.name)
      )

      const nodesWithStyle = props.nodes.map(node => {
        // 使用后端返回的category字段：1=高级节点，0=普通节点
        const isHighLevel = node.category === 1
        return {
          ...node,
          symbolSize: isHighLevel ? 25 : 15, // 高级节点更大
          category: node.category !== undefined ? node.category : 0, // 保留后端返回的category
          itemStyle: {
            color: isHighLevel ? '#ff7c00' : '#5470c6' // 高级节点橙色，普通节点蓝色
          },
          label: {
            show: true,
            position: 'right',
            formatter: node.name,
            fontSize: isHighLevel ? 13 : 11, // 高级节点标签更大
            fontWeight: isHighLevel ? 'bold' : 'normal' // 高级节点标签加粗
          }
        }
      })

      const linksWithStyle = props.links.map(link => {
        const sourceHigh = highLevelSet.has(link.source)
        const targetHigh = highLevelSet.has(link.target)
        const bothHigh = sourceHigh && targetHigh
        return {
          ...link,
          lineStyle: {
            color: bothHigh ? '#ff7c00' : '#c0c4cc',
            width: bothHigh ? 2.5 : 1.5,
            opacity: bothHigh ? 0.95 : 0.8
          }
        }
      })

      chartInstance.setOption({
        series: [{
          data: nodesWithStyle,
          links: linksWithStyle
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