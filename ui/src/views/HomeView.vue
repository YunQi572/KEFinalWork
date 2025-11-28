<template>
  <div class="home-view">
    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <div class="title">松材线虫病知识图谱系统</div>
      <div class="search-box">
        <el-input
          v-model="newEntityName"
          placeholder="输入新实体名称（如：湿地松）"
          class="input-entity"
          @keyup.enter="handleAddEntity"
        >
          <template #append>
            <el-button
              type="primary"
              :icon="Plus"
              @click="handleAddEntity"
              :loading="adding"
            >
              智能添加
            </el-button>
          </template>
        </el-input>
      </div>
      <div class="actions">
        <el-button :icon="Refresh" @click="loadGraph" :loading="loading">
          刷新图谱
        </el-button>
      </div>
    </div>

    <!-- 图谱可视化区域 -->
    <div class="graph-container">
      <KnowledgeGraph
        v-if="!loading"
        :nodes="graphData.nodes"
        :links="graphData.links"
        @node-click="handleNodeClick"
        @edge-click="handleEdgeClick"
      />
      <div v-else class="loading-container">
        <el-icon class="is-loading" :size="50">
          <Loading />
        </el-icon>
        <p>加载中...</p>
      </div>
    </div>

    <!-- 相似词选择对话框 -->
    <el-dialog
      v-model="similarDialogVisible"
      title="选择相似实体"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="similar-dialog-content">
        <div class="input-entity-info">
          <span class="label">您输入的实体：</span>
          <span class="entity-name">{{ pendingEntityName }}</span>
        </div>
        
        <el-divider />
        
        <div class="similar-list-title">
          <el-icon><Search /></el-icon>
          请选择一个与之相似的已有实体（用于推理新的关系）
          <span v-if="similarStats" class="stats-info">
            （图谱内: {{ similarStats.in_graph_count }} 个，优先显示）
          </span>
        </div>
        
        <el-alert
          v-if="similarStats && similarStats.in_graph_count === 0"
          type="warning"
          :closable="false"
          show-icon
          class="no-graph-alert"
        >
          <template #title>
            当前相似词都不在图谱中，建议选择相似度最高的词进行添加
          </template>
        </el-alert>
        
        <el-radio-group v-model="selectedSimilar" class="similar-list">
          <el-radio
            v-for="(item, index) in similarEntities"
            :key="index"
            :label="item.entity"
            :class="['similar-item', { 'priority-item': item.in_graph }]"
          >
            <div class="similar-item-content">
              <span class="rank">{{ index + 1 }}.</span>
              <span class="entity">{{ item.entity }}</span>
              <el-tag
                :type="item.in_graph ? 'success' : 'info'"
                size="small"
                class="status-tag"
              >
                {{ item.in_graph ? '✓ 图谱中' : '图谱外' }}
              </el-tag>
              <span class="similarity" :class="{ 'high-similarity': item.in_graph }">
                相似度: {{ (item.similarity * 100).toFixed(1) }}%
              </span>
            </div>
          </el-radio>
        </el-radio-group>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="similarDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="generateTriples"
            :loading="generating"
            :disabled="!selectedSimilar"
          >
            下一步：生成候选关系
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 三元组选择对话框 -->
    <el-dialog
      v-model="triplesDialogVisible"
      title="选择要添加的知识关系"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="triples-dialog-content">
        <div class="triple-info-header">
          <el-alert type="info" :closable="false">
            <template #title>
              <div class="alert-content">
                <span>已为 <strong>{{ pendingEntityName }}</strong> 生成 {{ candidateTriples.length }} 个候选关系</span>
                <span class="sub-info">基于相似词: {{ selectedSimilarEntity }}</span>
              </div>
            </template>
          </el-alert>
        </div>

        <el-divider />

        <div class="triples-list-title">
          <el-icon><Connection /></el-icon>
          请选择一个最合适的知识关系添加到图谱中：
        </div>

        <el-radio-group v-model="selectedTripleIndex" class="triples-list">
          <el-radio
            v-for="(triple, index) in candidateTriples"
            :key="index"
            :label="index"
            class="triple-item"
          >
            <div class="triple-item-content">
              <span class="triple-rank">{{ index + 1 }}</span>
              <div class="triple-visual">
                <span class="entity head-entity">{{ triple.head_entity }}</span>
                <div class="relation-arrow">
                  <div class="arrow-line"></div>
                  <span class="relation-label">{{ triple.relation }}</span>
                  <div class="arrow-head">▶</div>
                </div>
                <span class="entity tail-entity">{{ triple.tail_entity }}</span>
              </div>
            </div>
          </el-radio>
        </el-radio-group>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="triplesDialogVisible = false">取消</el-button>
          <el-button @click="goBackToSimilar">
            <el-icon><Back /></el-icon>
            返回上一步
          </el-button>
          <el-button
            type="primary"
            @click="confirmAddTriple"
            :loading="adding"
            :disabled="selectedTripleIndex === null"
          >
            <el-icon><Check /></el-icon>
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑节点对话框 -->
    <el-dialog
      v-model="nodeDialogVisible"
      :title="`节点: ${selectedNode?.name}`"
      width="400px"
    >
      <el-form :model="nodeForm" label-width="80px">
        <el-form-item label="节点名称">
          <el-input v-model="nodeForm.name" placeholder="请输入节点名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="nodeDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="handleDeleteNode">删除节点</el-button>
          <el-button type="primary" @click="handleUpdateNode">保存修改</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑边对话框 -->
    <el-dialog
      v-model="edgeDialogVisible"
      title="编辑关系"
      width="500px"
    >
      <el-form :model="edgeForm" label-width="80px">
        <el-form-item label="头实体">
          <el-input v-model="edgeForm.head_entity" disabled />
        </el-form-item>
        <el-form-item label="关系">
          <el-select v-model="edgeForm.relation" placeholder="请选择关系">
            <el-option
              v-for="rel in relations"
              :key="rel"
              :label="rel"
              :value="rel"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="尾实体">
          <el-input v-model="edgeForm.tail_entity" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="edgeDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="handleDeleteEdge">删除关系</el-button>
          <el-button type="primary" @click="handleUpdateEdge">保存修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Loading, Search, Connection, Back, Check } from '@element-plus/icons-vue'
import KnowledgeGraph from '@/components/KnowledgeGraph.vue'
import api from '@/api'

// 数据状态
const loading = ref(false)
const adding = ref(false)
const graphData = ref({ nodes: [], links: [] })
const relations = ref([])
const newEntityName = ref('')

// 节点编辑
const nodeDialogVisible = ref(false)
const selectedNode = ref(null)
const nodeForm = ref({ name: '' })

// 边编辑
const edgeDialogVisible = ref(false)
const selectedEdge = ref(null)
const edgeForm = ref({
  id: null,
  head_entity: '',
  relation: '',
  tail_entity: ''
})

// 加载图谱数据
const loadGraph = async () => {
  loading.value = true
  try {
    const data = await api.getGraph()
    graphData.value = data
    ElMessage.success('图谱加载成功')
  } catch (error) {
    ElMessage.error(`加载失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 加载有效关系列表
const loadRelations = async () => {
  try {
    const data = await api.getRelations()
    relations.value = data.relations
  } catch (error) {
    console.error('加载关系列表失败:', error)
  }
}

// 相似词选择对话框
const similarDialogVisible = ref(false)
const similarEntities = ref([])
const selectedSimilar = ref('')
const pendingEntityName = ref('')
const similarStats = ref(null)

// 三元组选择对话框
const triplesDialogVisible = ref(false)
const candidateTriples = ref([])
const selectedTripleIndex = ref(null)
const generating = ref(false)
const selectedSimilarEntity = ref('')

// 智能添加实体（第一步：获取相似词）
const handleAddEntity = async () => {
  if (!newEntityName.value.trim()) {
    ElMessage.warning('请输入实体名称')
    return
  }

  adding.value = true
  try {
    const result = await api.getSimilarEntities(newEntityName.value.trim())
    
    // 保存待添加的实体名称和统计信息
    pendingEntityName.value = result.input
    similarEntities.value = result.similar_entities
    similarStats.value = result.stats || null
    
    // 默认选择第一个相似词（优先是图谱内的）
    if (similarEntities.value.length > 0) {
      selectedSimilar.value = similarEntities.value[0].entity
    }
    
    // 提示用户图谱内实体数量
    if (similarStats.value && similarStats.value.in_graph_count > 0) {
      ElMessage.info(`已找到 ${similarStats.value.in_graph_count} 个图谱内的相似实体，建议优先选择`)
    }
    
    // 显示相似词选择对话框
    similarDialogVisible.value = true
  } catch (error) {
    ElMessage.error(`查询相似词失败: ${error.message}`)
  } finally {
    adding.value = false
  }
}

// 生成候选三元组（第二步：基于选择的相似词）
const generateTriples = async () => {
  if (!selectedSimilar.value) {
    ElMessage.warning('请选择一个相似词')
    return
  }

  generating.value = true
  
  try {
    const result = await api.generateTriples({
      entity_name: pendingEntityName.value,
      similar_entity: selectedSimilar.value
    })
    
    // 保存候选三元组
    candidateTriples.value = result.candidate_triples
    selectedSimilarEntity.value = result.similar_entity
    selectedTripleIndex.value = candidateTriples.value.length > 0 ? 0 : null
    
    // 关闭相似词对话框，打开三元组选择对话框
    similarDialogVisible.value = false
    triplesDialogVisible.value = true
    
    ElMessage.success(`已生成 ${result.total_candidates} 个候选关系`)
  } catch (error) {
    ElMessage.error(`生成候选关系失败: ${error.message}`)
  } finally {
    generating.value = false
  }
}

// 返回上一步
const goBackToSimilar = () => {
  triplesDialogVisible.value = false
  similarDialogVisible.value = true
}

// 确认添加三元组（第三步：用户选择后插入数据库）
const confirmAddTriple = async () => {
  if (selectedTripleIndex.value === null) {
    ElMessage.warning('请选择一个关系')
    return
  }

  const selectedTriple = candidateTriples.value[selectedTripleIndex.value]
  
  adding.value = true
  triplesDialogVisible.value = false
  
  try {
    const result = await api.addNodeWithTriple({
      entity_name: pendingEntityName.value,
      similar_entity: selectedSimilarEntity.value,
      selected_triple: selectedTriple
    })
    
    ElMessage.success({
      message: `添加成功！${result.triple.head_entity} --[${result.triple.relation}]--> ${result.triple.tail_entity}`,
      duration: 5000
    })
    
    // 清空所有状态
    newEntityName.value = ''
    pendingEntityName.value = ''
    selectedSimilar.value = ''
    similarEntities.value = []
    similarStats.value = null
    candidateTriples.value = []
    selectedTripleIndex.value = null
    selectedSimilarEntity.value = ''
    
    await loadGraph()
  } catch (error) {
    ElMessage.error(`添加失败: ${error.message}`)
  } finally {
    adding.value = false
  }
}

// 处理节点点击
const handleNodeClick = (node) => {
  selectedNode.value = node
  nodeForm.value.name = node.name
  nodeDialogVisible.value = true
}

// 处理边点击
const handleEdgeClick = (edge) => {
  selectedEdge.value = edge
  edgeForm.value = {
    id: edge.id,
    head_entity: edge.source,
    relation: edge.value,
    tail_entity: edge.target
  }
  edgeDialogVisible.value = true
}

// 删除节点
const handleDeleteNode = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除节点 "${selectedNode.value.name}" 吗？这将删除所有与该节点相关的关系。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.deleteNode(selectedNode.value.name)
    ElMessage.success('删除成功')
    nodeDialogVisible.value = false
    await loadGraph()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

// 更新节点
const handleUpdateNode = async () => {
  if (!nodeForm.value.name.trim()) {
    ElMessage.warning('节点名称不能为空')
    return
  }

  if (nodeForm.value.name === selectedNode.value.name) {
    ElMessage.info('未做任何修改')
    nodeDialogVisible.value = false
    return
  }

  try {
    await api.updateNode(selectedNode.value.name, nodeForm.value.name)
    ElMessage.success('更新成功')
    nodeDialogVisible.value = false
    await loadGraph()
  } catch (error) {
    ElMessage.error(`更新失败: ${error.message}`)
  }
}

// 删除边
const handleDeleteEdge = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条关系吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.deleteEdge(selectedEdge.value.id)
    ElMessage.success('删除成功')
    edgeDialogVisible.value = false
    await loadGraph()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

// 更新边
const handleUpdateEdge = async () => {
  if (!edgeForm.value.relation) {
    ElMessage.warning('请选择关系')
    return
  }

  try {
    await api.updateEdge(edgeForm.value)
    ElMessage.success('更新成功')
    edgeDialogVisible.value = false
    await loadGraph()
  } catch (error) {
    ElMessage.error(`更新失败: ${error.message}`)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadGraph()
  loadRelations()
})
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.top-bar {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  gap: 20px;
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  white-space: nowrap;
}

.search-box {
  flex: 1;
  max-width: 600px;
}

.input-entity {
  width: 100%;
}

.actions {
  display: flex;
  gap: 10px;
}

.graph-container {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  background: white;
  margin: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.loading-container p {
  margin-top: 16px;
  font-size: 16px;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 相似词对话框样式 */
.similar-dialog-content {
  padding: 10px 0;
}

.input-entity-info {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.input-entity-info .label {
  color: #606266;
  margin-right: 8px;
}

.input-entity-info .entity-name {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.similar-list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.similar-list-title .stats-info {
  color: #67c23a;
  font-weight: 600;
  font-size: 13px;
}

.no-graph-alert {
  margin-bottom: 16px;
}

.similar-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.similar-item {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  transition: all 0.3s;
}

/* 图谱内实体高亮 */
.similar-item.priority-item {
  border: 2px solid #67c23a;
  background: #f0f9ff;
}

.similar-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
  transform: translateX(4px);
}

.similar-item.priority-item:hover {
  border-color: #67c23a;
  background: #e1f3d8;
}

.similar-item.is-checked {
  border-color: #409eff;
  background: #ecf5ff;
}

.similar-item.priority-item.is-checked {
  border-color: #67c23a;
  background: #e1f3d8;
}

.similar-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.similar-item-content .rank {
  color: #909399;
  font-weight: bold;
  min-width: 24px;
}

.similar-item-content .entity {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.similar-item-content .status-tag {
  margin-left: auto;
}

.similar-item-content .similarity {
  color: #909399;
  font-size: 13px;
  font-weight: 500;
  min-width: 100px;
  text-align: right;
}

.similar-item-content .similarity.high-similarity {
  color: #67c23a;
  font-weight: 600;
}

/* 三元组选择对话框样式 */
.triples-dialog-content {
  padding: 10px 0;
}

.triple-info-header {
  margin-bottom: 16px;
}

.alert-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alert-content strong {
  color: #409eff;
  font-size: 16px;
}

.alert-content .sub-info {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.triples-list-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
  margin-bottom: 16px;
  font-weight: 500;
}

.triples-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 450px;
  overflow-y: auto;
  padding: 8px;
}

.triple-item {
  width: 100%;
  padding: 16px;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
  background: #fafafa;
}

.triple-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.2);
}

.triple-item.is-checked {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.triple-item-content {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.triple-rank {
  color: #909399;
  font-weight: bold;
  font-size: 18px;
  min-width: 32px;
  text-align: center;
}

.triple-visual {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.triple-visual .entity {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.triple-visual .head-entity {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.triple-visual .tail-entity {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.relation-arrow {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
  min-width: 150px;
}

.arrow-line {
  flex: 1;
  height: 3px;
  background: linear-gradient(to right, #409eff, #67c23a);
  border-radius: 2px;
}

.relation-label {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: -20px;
  background: #409eff;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.arrow-head {
  color: #67c23a;
  font-size: 20px;
  margin-left: -4px;
}
</style>
