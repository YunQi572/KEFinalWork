<template>
  <div class="image-analysis">
    <!-- 图像上传区域 -->
    <div class="upload-section">
      <div class="upload-header">
        <h3>
          <el-icon><Camera /></el-icon>
          松材线虫病图像分析
        </h3>
        <p>上传松树、昆虫或病害相关图片，系统将自动识别并分析</p>
      </div>

      <el-upload
        ref="uploadRef"
        class="upload-dragger"
        drag
        :action="uploadAction"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :file-list="fileList"
        :limit="1"
        :on-exceed="handleExceed"
        accept="image/*"
        :disabled="analyzing"
      >
        <div class="upload-content">
          <el-icon class="el-icon--upload" :size="50">
            <UploadFilled />
          </el-icon>
          <div class="el-upload__text">
            将图片拖拽到此处，或<em>点击上传</em>
          </div>
          <div class="el-upload__tip">
            支持 JPG、PNG、GIF 格式，单张图片不超过10MB
          </div>
        </div>
      </el-upload>

      <!-- 分析配置 -->
      <div class="analysis-config">
        <el-form :model="analysisForm" label-position="top" class="config-form">
          <div class="form-row">
            <el-form-item label="分析类型">
              <el-select v-model="analysisForm.analyzeType" placeholder="选择分析类型">
                <el-option label="完整分析（推荐）" value="full" />
                <el-option label="仅实体识别" value="entity_only" />
                <el-option label="仅关系分析" value="relationship_only" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="置信度阈值">
              <el-slider
                v-model="analysisForm.confidenceThreshold"
                :min="0.1"
                :max="1.0"
                :step="0.1"
                :format-tooltip="formatTooltip"
                show-tooltip
              />
            </el-form-item>
            
            <el-form-item label="自动更新知识图谱">
              <el-switch
                v-model="analysisForm.updateKnowledge"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 分析进行中 -->
    <div v-if="analyzing" class="analyzing-section">
      <el-card class="analysis-progress">
        <div class="progress-content">
          <el-icon class="is-loading" :size="40">
            <Loading />
          </el-icon>
          <h4>正在分析图像...</h4>
          <p>{{ analysisStep }}</p>
          <el-progress
            :percentage="progressPercentage"
            :color="progressColor"
            striped
            striped-flow
          />
        </div>
      </el-card>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisResult" class="results-section">
      <el-row :gutter="20">
        <!-- 左侧：图像预览和基本信息 -->
        <el-col :span="8">
          <el-card class="image-preview-card">
            <template #header>
              <div class="card-header">
                <span>图像信息</span>
                <el-tag :type="getConfidenceTagType(analysisResult.analysis_summary?.avg_confidence)">
                  平均置信度: {{ (analysisResult.analysis_summary?.avg_confidence * 100)?.toFixed(1) || 0 }}%
                </el-tag>
              </div>
            </template>
            
            <div class="image-preview">
              <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="上传的图像" />
            </div>
            
            <div class="image-info">
              <el-descriptions :column="1" size="small">
                <el-descriptions-item label="分析ID">
                  {{ analysisResult.analysis_id }}
                </el-descriptions-item>
                <el-descriptions-item label="图像尺寸">
                  {{ analysisResult.image_info?.size?.[0] }} × {{ analysisResult.image_info?.size?.[1] }}
                </el-descriptions-item>
                <el-descriptions-item label="检测实体">
                  {{ analysisResult.detected_entities?.length || 0 }} 个
                </el-descriptions-item>
                <el-descriptions-item label="分析时间">
                  {{ formatTime(Date.now()) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：检测结果 -->
        <el-col :span="16">
          <el-tabs v-model="activeTab" class="result-tabs">
            <!-- 实体识别结果 -->
            <el-tab-pane label="实体识别" name="entities" :disabled="!analysisResult.detected_entities?.length">
              <el-card class="entities-card">
                <div v-if="analysisResult.detected_entities?.length" class="entities-list">
                  <div
                    v-for="(entity, index) in analysisResult.detected_entities"
                    :key="index"
                    class="entity-item"
                    :class="getEntityItemClass(entity)"
                  >
                    <div class="entity-header">
                      <div class="entity-basic">
                        <el-tag :type="getEntityTypeTag(entity.type)" size="small">
                          {{ getEntityTypeLabel(entity.type) }}
                        </el-tag>
                        <span class="entity-name">{{ entity.name }}</span>
                        <el-tag v-if="entity.matched_kb_entity" type="success" size="small">
                          匹配: {{ entity.matched_kb_entity }}
                        </el-tag>
                      </div>
                      <div class="entity-scores">
                        <el-progress
                          :percentage="entity.confidence * 100"
                          :width="80"
                          type="circle"
                          :color="getConfidenceColor(entity.confidence)"
                          :format="() => (entity.confidence * 100).toFixed(1) + '%'"
                        />
                        <div class="score-labels">
                          <div>置信度</div>
                          <div>{{ (entity.confidence * 100).toFixed(1) }}%</div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="entity.features" class="entity-features">
                      <h5>📊 检测特征详情：</h5>
                      <div class="features-grid">
                        <el-tag
                          v-for="(value, key) in entity.features"
                          :key="key"
                          size="small"
                          class="feature-tag"
                        >
                          {{ formatFeatureKey(key) }}: {{ formatFeatureValue(value) }}
                        </el-tag>
                      </div>
                      
                      <!-- 显示相似度信息 -->
                      <div v-if="entity.similarity !== undefined" class="similarity-info">
                        <h5>相似度分析：</h5>
                        <el-progress
                          :percentage="entity.similarity * 100"
                          :color="getSimilarityColor(entity.similarity)"
                          :show-text="false"
                        />
                        <span class="similarity-text">
                          与知识库匹配度: {{ (entity.similarity * 100).toFixed(1) }}%
                          <el-tag v-if="entity.matched_kb_entity" type="success" size="small">
                            → {{ entity.matched_kb_entity }}
                          </el-tag>
                          <el-tag v-else type="info" size="small">
                            新发现实体
                          </el-tag>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="未检测到实体" />
              </el-card>
            </el-tab-pane>

            <!-- 关系分析结果 -->
            <el-tab-pane label="关系分析" name="relationships" :disabled="!analysisResult.relationship_analysis">
              <el-card class="relationships-card">
                <div v-if="analysisResult.relationship_analysis" class="relationship-content">
                  <div class="relationship-summary">
                    <el-alert
                      :title="analysisResult.relationship_analysis.analysis_summary"
                      type="info"
                      show-icon
                      :closable="false"
                    />
                  </div>

                  <div class="relationship-details">
                    <!-- 已知关系 -->
                    <div v-if="analysisResult.relationship_analysis.existing_relationships?.length" class="relation-section">
                      <h4>
                        <el-icon><Connection /></el-icon>
                        已知关系
                      </h4>
                      <div class="relations-list">
                        <div
                          v-for="(rel, index) in analysisResult.relationship_analysis.existing_relationships"
                          :key="index"
                          class="relation-item existing"
                        >
                          <span class="entity">{{ rel.head_entity }}</span>
                          <div class="relation-arrow">
                            <span class="relation-label">{{ rel.relation }}</span>
                            <el-icon><Right /></el-icon>
                          </div>
                          <span class="entity">{{ rel.tail_entity }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- 潜在关系 -->
                    <div v-if="analysisResult.relationship_analysis.potential_relationships?.length" class="relation-section">
                      <h4>
                        <el-icon><MagicStick /></el-icon>
                        推理关系
                      </h4>
                      <div class="relations-list">
                        <div
                          v-for="(rel, index) in analysisResult.relationship_analysis.potential_relationships"
                          :key="index"
                          class="relation-item potential"
                        >
                          <span class="entity">{{ rel.head_entity }}</span>
                          <div class="relation-arrow">
                            <span class="relation-label">{{ rel.relation }}</span>
                            <el-icon><Right /></el-icon>
                          </div>
                          <span class="entity">{{ rel.tail_entity }}</span>
                          <el-tag type="warning" size="small">
                            {{ (rel.confidence * 100).toFixed(1) }}%
                          </el-tag>
                        </div>
                      </div>
                    </div>

                    <!-- 验证结果 -->
                    <div v-if="analysisResult.relationship_analysis.validation_result?.validated_scenarios?.length" class="validation-section">
                      <h4>
                        <el-icon><Check /></el-icon>
                        场景验证
                      </h4>
                      <div
                        v-for="(scenario, index) in analysisResult.relationship_analysis.validation_result.validated_scenarios"
                        :key="index"
                        class="scenario-item"
                      >
                        <div class="scenario-header">
                          <span class="scenario-name">{{ scenario.scenario }}</span>
                          <el-tag :type="getRiskTagType(scenario.risk_assessment)">
                            {{ scenario.risk_assessment }}
                          </el-tag>
                        </div>
                        <el-progress
                          :percentage="scenario.confidence * 100"
                          :color="getConfidenceColor(scenario.confidence)"
                          :show-text="false"
                        />
                        <p class="scenario-recommendation">{{ scenario.recommendation }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="未进行关系分析" />
              </el-card>
            </el-tab-pane>

            <!-- 疾病预测结果 -->
            <el-tab-pane label="疾病预测" name="prediction" :disabled="!analysisResult.disease_prediction">
              <el-card class="prediction-card">
                <div v-if="analysisResult.disease_prediction" class="prediction-content">
                  <div class="prediction-summary">
                    <div class="summary-cards">
                      <div class="summary-card risk-card">
                        <div class="card-icon">
                          <el-icon :size="30"><Warning /></el-icon>
                        </div>
                        <div class="card-content">
                          <div class="card-title">风险等级</div>
                          <div class="card-value" :class="getRiskClass(analysisResult.disease_prediction.disease_prediction?.risk_level)">
                            {{ analysisResult.disease_prediction.disease_prediction?.risk_level || '未知' }}
                          </div>
                        </div>
                      </div>
                      
                      <div class="summary-card confidence-card">
                        <div class="card-icon">
                          <el-icon :size="30"><DataAnalysis /></el-icon>
                        </div>
                        <div class="card-content">
                          <div class="card-title">预测置信度</div>
                          <div class="card-value">
                            {{ (analysisResult.disease_prediction.disease_prediction?.confidence * 100)?.toFixed(1) || 0 }}%
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 可能疾病 -->
                  <div v-if="analysisResult.disease_prediction.disease_prediction?.likely_diseases?.length" class="diseases-section">
                    <h4>
                      <el-icon><First /></el-icon>
                      可能疾病
                    </h4>
                    <div class="diseases-list">
                      <el-tag
                        v-for="disease in analysisResult.disease_prediction.disease_prediction.likely_diseases"
                        :key="disease"
                        type="danger"
                        size="large"
                        class="disease-tag"
                      >
                        {{ disease }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- 传播分析 -->
                  <div v-if="analysisResult.disease_prediction.transmission_analysis?.paths?.length" class="transmission-section">
                    <h4>
                      <el-icon><Share /></el-icon>
                      传播途径
                    </h4>
                    <div class="transmission-list">
                      <div
                        v-for="(path, index) in analysisResult.disease_prediction.transmission_analysis.paths"
                        :key="index"
                        class="transmission-item"
                      >
                        <span class="vector">{{ path.vector }}</span>
                        <div class="transmission-arrow">
                          <span class="transmission-label">{{ path.relation }}</span>
                          <el-icon><Right /></el-icon>
                        </div>
                        <span class="pathogen">{{ path.pathogen }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 防治建议 -->
                  <div v-if="analysisResult.disease_prediction.recommended_actions?.treatments?.length" class="treatments-section">
                    <h4>
                      <el-icon><Tools /></el-icon>
                      防治建议
                    </h4>
                    <div class="treatments-list">
                      <div
                        v-for="(treatment, index) in analysisResult.disease_prediction.recommended_actions.treatments"
                        :key="index"
                        class="treatment-item"
                      >
                        <el-tag type="success" size="small">{{ treatment.disease }}</el-tag>
                        <span class="treatment-text">{{ treatment.treatment }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- AI洞察 -->
                  <div v-if="analysisResult.disease_prediction.ai_insights" class="ai-insights-section">
                    <h4>
                      <el-icon><Cpu /></el-icon>
                      AI分析洞察
                    </h4>
                    <el-alert
                      :title="analysisResult.disease_prediction.ai_insights"
                      type="info"
                      show-icon
                      :closable="false"
                    />
                  </div>
                </div>
                <el-empty v-else description="未进行疾病预测" />
              </el-card>
            </el-tab-pane>

            <!-- 知识更新 -->
            <el-tab-pane label="知识更新" name="knowledge" :disabled="!analysisResult.knowledge_update">
              <el-card class="knowledge-card">
                <div v-if="analysisResult.knowledge_update" class="knowledge-content">
                  <div class="update-stats">
                    <div class="stats-grid">
                      <div class="stat-item">
                        <div class="stat-number">{{ analysisResult.knowledge_update.new_entities_added || 0 }}</div>
                        <div class="stat-label">新增实体</div>
                      </div>
                      <div class="stat-item">
                        <div class="stat-number">{{ analysisResult.knowledge_update.new_relations_added || 0 }}</div>
                        <div class="stat-label">新增关系</div>
                      </div>
                      <div class="stat-item">
                        <div class="stat-number">{{ analysisResult.knowledge_update.features_updated || 0 }}</div>
                        <div class="stat-label">更新特征</div>
                      </div>
                      <div class="stat-item">
                        <div class="stat-number">{{ analysisResult.knowledge_update.skipped_low_confidence || 0 }}</div>
                        <div class="stat-label">跳过低置信度</div>
                      </div>
                    </div>
                  </div>

                  <div v-if="analysisResult.knowledge_update.updates?.length" class="updates-list">
                    <h4>更新详情</h4>
                    <div
                      v-for="(update, index) in analysisResult.knowledge_update.updates"
                      :key="index"
                      class="update-item"
                    >
                      <el-tag :type="getUpdateTypeTag(update.type)" size="small">
                        {{ getUpdateTypeLabel(update.type) }}
                      </el-tag>
                      <span class="update-description">{{ getUpdateDescription(update) }}</span>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="未进行知识更新" />
              </el-card>
            </el-tab-pane>
          </el-tabs>
        </el-col>
      </el-row>

      <!-- 建议和操作 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="recommendations-card">
            <template #header>
              <div class="card-header">
                <span>分析建议</span>
                <el-button type="primary" size="small" @click="saveAnalysisResult">
                  <el-icon><DocumentCopy /></el-icon>
                  保存结果
                </el-button>
              </div>
            </template>
            
            <div class="recommendations-list">
              <div
                v-for="(recommendation, index) in analysisResult.recommendations"
                :key="index"
                class="recommendation-item"
              >
                <el-icon><InfoFilled /></el-icon>
                {{ recommendation }}
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Camera, UploadFilled, Loading, Connection, Right, MagicStick, Check, Warning,
  DataAnalysis, First, Share, Tools, Cpu, DocumentCopy, InfoFilled
} from '@element-plus/icons-vue'
import api from '@/api'
import { API_CONFIG, UPLOAD_CONFIG, ANALYSIS_CONFIG, UI_CONFIG } from '@/config'

// 响应式数据
const uploadRef = ref()
const fileList = ref([])
const analyzing = ref(false)
const analysisStep = ref('')
const progressPercentage = ref(0)
const imagePreviewUrl = ref('')
const analysisResult = ref(null)
const activeTab = ref('entities')

// 分析配置表单
const analysisForm = reactive({
  analyzeType: ANALYSIS_CONFIG.DEFAULT_ANALYSIS_TYPE,
  confidenceThreshold: ANALYSIS_CONFIG.DEFAULT_CONFIDENCE_THRESHOLD,
  updateKnowledge: true
})

// 上传配置 - 使用配置文件
const uploadAction = `${API_CONFIG.BASE_URL}/api/image/analyze`

// 进度条颜色
const progressColor = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

// 上传前检查
const beforeUpload = (file) => {
  const isImage = UPLOAD_CONFIG.ACCEPTED_TYPES.includes(file.type)
  const isLtMaxSize = file.size < UPLOAD_CONFIG.MAX_SIZE

  if (!isImage) {
    ElMessage.error('只能上传图片格式的文件!')
    return false
  }
  if (!isLtMaxSize) {
    ElMessage.error(`上传文件大小不能超过 ${UPLOAD_CONFIG.MAX_SIZE / 1024 / 1024}MB!`)
    return false
  }

  // 创建图片预览
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreviewUrl.value = e.target.result
  }
  reader.readAsDataURL(file)

  // 开始分析
  startAnalysis(file)
  
  return false // 阻止自动上传
}

// 开始分析
const startAnalysis = async (file) => {
  analyzing.value = true
  progressPercentage.value = 0
  analysisResult.value = null
  
  try {
    // 模拟分析步骤
    const steps = [
      { text: '正在上传图像...', duration: 1000, progress: 20 },
      { text: '正在进行实体识别...', duration: 2000, progress: 50 },
      { text: '正在分析实体关系...', duration: 1500, progress: 75 },
      { text: '正在进行疾病预测...', duration: 1000, progress: 90 },
      { text: '正在更新知识图谱...', duration: 500, progress: 100 }
    ]

    for (const step of steps) {
      analysisStep.value = step.text
      await new Promise(resolve => setTimeout(resolve, step.duration))
      progressPercentage.value = step.progress
    }

    // 调用实际的分析API
    const formData = new FormData()
    formData.append('file', file)
    formData.append('analyze_type', analysisForm.analyzeType)
    formData.append('update_knowledge', analysisForm.updateKnowledge)
    formData.append('confidence_threshold', analysisForm.confidenceThreshold)

    const result = await api.analyzeImage(formData)
    analysisResult.value = result
    
    console.log('分析结果:', result) // 调试日志
    
    ElMessage.success(`图像分析完成! 检测到 ${result.detected_entities?.length || 0} 个实体`)
    
    // 根据结果切换到相应的标签页
    if (result.detected_entities?.length) {
      activeTab.value = 'entities'
    } else {
      ElMessage.warning('未检测到实体')
    }
    
  } catch (error) {
    ElMessage.error(`分析失败: ${error.message}`)
    console.error('图像分析失败:', error)
  } finally {
    analyzing.value = false
    analysisStep.value = ''
    progressPercentage.value = 0
  }
}

// 处理文件数量超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一张图片，请先删除已上传的图片')
}

// 上传成功处理（实际不会触发，因为beforeUpload返回false）
const handleUploadSuccess = () => {
  // 这里不会执行到
}

// 上传失败处理
const handleUploadError = (error) => {
  ElMessage.error(`上传失败: ${error.message}`)
  analyzing.value = false
}

// 工具函数
const formatTooltip = (value) => `${(value * 100).toFixed(0)}%`

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const formatFeatureKey = (key) => {
  const keyMap = {
    'dominant_color': '主要颜色',
    'texture': '纹理',
    'detection_basis': '检测依据',
    'avg_rgb': '平均RGB值',
    'color_variance': '颜色方差',
    'area': '面积',
    'perimeter': '周长',
    'aspect_ratio': '宽高比',
    'compactness': '紧密度',
    'texture_roughness': '纹理粗糙度',
    'texture_uniformity': '纹理均匀性',
    'brightness': '亮度',
    'ai_detected': 'AI检测',
    'ai_confidence': 'AI置信度',
    'ai_description': 'AI描述',
    'matched_kb_entity': '匹配实体',
    'similarity_score': '相似度得分',
    'match_reason': '匹配原因',
    'is_unknown': '未知实体'
  }
  return keyMap[key] || key
}

const formatFeatureValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  } else if (typeof value === 'object') {
    return JSON.stringify(value)
  } else if (typeof value === 'number') {
    // 对于数值类型，根据数值大小决定保留的小数位数
    if (Number.isInteger(value)) {
      return String(value)
    } else if (Math.abs(value) >= 100) {
      // 大数值保留整数部分
      return Math.round(value).toString()
    } else if (Math.abs(value) >= 10) {
      // 中等数值保留一位小数
      return value.toFixed(1)
    } else {
      // 小数值保留两位小数
      return value.toFixed(2)
    }
  } else {
    return String(value)
  }
}

const getEntityTypeLabel = (type) => {
  const labels = {
    'insect': '昆虫',
    'tree': '植物',
    'disease_symptom': '病症',
    'environment': '环境'
  }
  return labels[type] || type
}

const getEntityTypeTag = (type) => {
  const tags = {
    'insect': 'danger',
    'tree': 'success',
    'disease_symptom': 'warning',
    'environment': 'info'
  }
  return tags[type] || ''
}

const getEntityItemClass = (entity) => {
  if (entity.confidence > 0.8) return 'high-confidence'
  if (entity.confidence > 0.6) return 'medium-confidence'
  return 'low-confidence'
}

const getConfidenceTagType = (confidence) => {
  if (confidence > 0.8) return 'success'
  if (confidence > 0.6) return ''
  return 'warning'
}

const getConfidenceColor = (confidence) => {
  if (confidence > 0.8) return '#67c23a'
  if (confidence > 0.6) return '#e6a23c'
  return '#f56c6c'
}

// 获取相似度颜色
const getSimilarityColor = (similarity) => {
  if (similarity > 0.8) return '#67c23a'  // 绿色：高相似度
  if (similarity > 0.6) return '#e6a23c'  // 橙色：中等相似度
  if (similarity > 0.4) return '#f56c6c'  // 红色：低相似度
  return '#909399'  // 灰色：很低相似度
}

const getRiskTagType = (risk) => {
  const types = {
    '高风险': 'danger',
    '中风险': 'warning',
    '低风险': 'success'
  }
  return types[risk] || 'info'
}

const getRiskClass = (risk) => {
  const classes = {
    '高风险': 'high-risk',
    '中风险': 'medium-risk',
    '低风险': 'low-risk'
  }
  return classes[risk] || ''
}

const getUpdateTypeTag = (type) => {
  const tags = {
    'new_entity': 'success',
    'new_relation': 'primary',
    'update_features': 'warning'
  }
  return tags[type] || 'info'
}

const getUpdateTypeLabel = (type) => {
  const labels = {
    'new_entity': '新实体',
    'new_relation': '新关系',
    'update_features': '特征更新'
  }
  return labels[type] || type
}

const getUpdateDescription = (update) => {
  if (update.type === 'new_entity') {
    return `添加实体: ${update.entity}`
  } else if (update.type === 'new_relation') {
    return `添加关系: ${update.head_entity} --[${update.relation}]--> ${update.tail_entity}`
  }
  return '更新操作'
}

// 保存分析结果
const saveAnalysisResult = async () => {
  try {
    // 这里可以调用API保存结果到数据库
    // 暂时使用本地下载
    const dataStr = JSON.stringify(analysisResult.value, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `image_analysis_${analysisResult.value.analysis_id}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('分析结果已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}
</script>

<style scoped>
.image-analysis {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 30px;
}

.upload-header {
  margin-bottom: 20px;
  text-align: center;
}

.upload-header h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
  color: #303133;
}

.upload-header p {
  color: #606266;
  font-size: 14px;
}

.upload-dragger {
  margin-bottom: 20px;
}

.upload-content {
  text-align: center;
  padding: 40px 0;
}

.analysis-config {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.config-form .form-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

.analyzing-section {
  margin-bottom: 30px;
}

.analysis-progress {
  max-width: 600px;
  margin: 0 auto;
}

.progress-content {
  text-align: center;
  padding: 20px;
}

.progress-content h4 {
  margin: 10px 0;
  color: #303133;
}

.progress-content p {
  color: #606266;
  margin-bottom: 20px;
}

.results-section {
  margin-bottom: 30px;
}

.image-preview-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-preview {
  margin-bottom: 20px;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-tabs {
  background: white;
}

.entities-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.entity-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.entity-item.high-confidence {
  border-color: #67c23a;
  background: #f0f9ff;
}

.entity-item.medium-confidence {
  border-color: #e6a23c;
}

.entity-item.low-confidence {
  border-color: #f56c6c;
}

.entity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.entity-basic {
  display: flex;
  align-items: center;
  gap: 8px;
}

.entity-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.entity-scores {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-labels {
  text-align: center;
  font-size: 12px;
  color: #606266;
}

.entity-features h5 {
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
}

.features-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-tag {
  font-size: 12px;
}

.similarity-info {
  margin-top: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.similarity-info h5 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.similarity-text {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

.relationship-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.relationship-summary {
  margin-bottom: 20px;
}

.relation-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #303133;
}

.relations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.relation-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  gap: 12px;
}

.relation-item.existing {
  background: #f0f9ff;
  border: 1px solid #409eff;
}

.relation-item.potential {
  background: #fff7e6;
  border: 1px solid #e6a23c;
}

.relation-item .entity {
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  font-weight: 500;
}

.relation-arrow {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
}

.relation-label {
  font-size: 12px;
  color: #409eff;
  font-weight: 600;
}

.scenario-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 12px;
}

.scenario-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.scenario-name {
  font-weight: 600;
  color: #303133;
}

.scenario-recommendation {
  margin-top: 8px;
  color: #606266;
  font-size: 14px;
}

.prediction-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  gap: 16px;
}

.risk-card {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
}

.confidence-card {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #303133;
}

.card-icon {
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
}

.card-value.high-risk {
  color: #f56c6c;
}

.card-value.medium-risk {
  color: #e6a23c;
}

.card-value.low-risk {
  color: #67c23a;
}

.diseases-section h4,
.transmission-section h4,
.treatments-section h4,
.ai-insights-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #303133;
}

.diseases-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.disease-tag {
  font-size: 14px;
  padding: 8px 12px;
}

.transmission-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transmission-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  gap: 12px;
}

.vector,
.pathogen {
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  font-weight: 500;
}

.transmission-arrow {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
}

.transmission-label {
  font-size: 12px;
  color: #e6a23c;
  font-weight: 600;
}

.treatments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.treatment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.treatment-text {
  color: #303133;
}

.knowledge-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 6px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.updates-list h4 {
  margin-bottom: 12px;
  color: #303133;
}

.update-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.update-description {
  color: #303133;
}

.recommendations-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: #e1f3d8;
  border-radius: 6px;
  border-left: 4px solid #67c23a;
}

.recommendation-item .el-icon {
  color: #67c23a;
  margin-top: 2px;
}
</style>