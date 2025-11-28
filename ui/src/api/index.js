/**
 * API服务模块 - 与后端通信
 */
import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export default {
  /**
   * 获取完整知识图谱
   */
  getGraph() {
    return apiClient.get('/graph')
  },

  /**
   * 获取相似实体（添加节点第一步）
   * @param {string} entityName - 实体名称
   * @param {number} topn - 返回前N个相似实体
   */
  getSimilarEntities(entityName, topn = 10) {
    return apiClient.get(`/node/similar/${encodeURIComponent(entityName)}`, {
      params: { topn }
    })
  },

  /**
   * 生成候选三元组（添加节点第二步）
   * @param {Object} data - { entity_name, similar_entity }
   */
  generateTriples(data) {
    return apiClient.post('/node/generate-triples', data)
  },

  /**
   * 使用选择的三元组添加节点（添加节点第三步）
   * @param {Object} data - { entity_name, similar_entity, selected_triple }
   */
  addNodeWithTriple(data) {
    return apiClient.post('/node/add', data)
  },

  /**
   * 删除节点
   * @param {string} nodeName - 节点名称
   */
  deleteNode(nodeName) {
    return apiClient.delete('/node/delete', { data: { name: nodeName } })
  },

  /**
   * 更新节点
   * @param {string} oldName - 旧名称
   * @param {string} newName - 新名称
   */
  updateNode(oldName, newName) {
    return apiClient.put('/node/update', { 
      old_name: oldName, 
      new_name: newName 
    })
  },

  /**
   * 删除边
   * @param {number} edgeId - 边的ID
   */
  deleteEdge(edgeId) {
    return apiClient.delete(`/edge/delete/${edgeId}`)
  },

  /**
   * 更新边
   * @param {object} edge - 边数据
   */
  updateEdge(edge) {
    return apiClient.put('/edge/update', edge)
  },

  /**
   * 获取所有有效关系
   */
  getRelations() {
    return apiClient.get('/relations')
  }
}
