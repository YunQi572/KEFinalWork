/**
 * API服务模块 - 与后端通信
 */
import axios from 'axios'
import { API_CONFIG } from '@/config'

// 创建axios实例
const apiClient = axios.create({
  baseURL: `${API_CONFIG.BASE_URL}/api`,
  timeout: API_CONFIG.TIMEOUT,
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
  },

  /**
   * 图像分析 - 识别松材线虫病相关实体并进行预测分析
   * @param {FormData} formData - 包含图像文件和分析参数的FormData
   */
  analyzeImage(formData) {
    return apiClient.post('/image/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: API_CONFIG.IMAGE_ANALYSIS_TIMEOUT // 图像分析可能需要更长时间
    })
  },

  /**
   * 验证实体组合的合理性
   * @param {Object} data - { entities, validation_type }
   */
  validateEntities(data) {
    return apiClient.post('/entities/validate', data)
  },

  /**
   * 获取知识图谱更新建议
   * @param {string} entityNames - 逗号分隔的实体名称（可选）
   */
  getUpdateSuggestions(entityNames = null) {
    const params = entityNames ? { entity_names: entityNames } : {}
    return apiClient.get('/knowledge/update-suggestions', { params })
  },

  /**
   * 获取图像分析历史记录
   * @param {number} limit - 返回记录数量限制
   */
  getAnalysisHistory(limit = 10) {
    return apiClient.get('/image/analysis-history', {
      params: { limit }
    })
  },

  /**
   * 添加高级节点
   * @param {string} nodeName - 要标记为高级节点的节点名称
   */
  addHighLevelNode(nodeName) {
    return apiClient.post('/graph/add-high-level-node', null, {
      params: { node_name: nodeName }
    })
  },

  /**
   * 移除高级节点标记
   * @param {string} nodeName - 要移除的高级节点名称
   */
  removeHighLevelNode(nodeName) {
    return apiClient.delete('/graph/remove-high-level-node', {
      params: { node_name: nodeName }
    })
  }
}
