# AI 内容工业化平台｜后端接口详细 API 文档

> 适用范围：第一阶段核心闭环原型。  
> API 风格：RESTful + 异步任务轮询。  
> 数据格式：JSON。  
> 鉴权建议：Bearer Token / Session Cookie。  
> 统一前缀：`/api/v1`。

---

## 1. 通用规范

### 1.1 通用响应
```json
{
  "success": true,
  "data": {},
  "message": "ok",
  "requestId": "req_xxx"
}
```

### 1.2 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数不合法",
    "details": []
  },
  "requestId": "req_xxx"
}
```

### 1.3 分页参数
| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| page | number | 1 | 页码 |
| pageSize | number | 20 | 每页数量 |
| sortBy | string | updatedAt | 排序字段 |
| sortOrder | string | desc | asc/desc |

### 1.4 分页响应
```json
{
  "items": [],
  "page": 1,
  "pageSize": 20,
  "total": 100
}
```

---

## 2. 项目管理 API

### 2.1 创建项目
`POST /api/v1/projects`

请求：
```json
{
  "name": "诡城短剧试点",
  "projectType": "short_drama",
  "genre": "悬疑",
  "targetDurationSeconds": 600,
  "targetEpisodeCount": 10,
  "aspectRatio": "9:16",
  "language": "zh-CN",
  "styleDirection": "电影感、冷色调、悬疑氛围"
}
```

响应：
```json
{
  "id": "project_uuid",
  "name": "诡城短剧试点",
  "status": "draft",
  "createdAt": "2026-06-01T10:00:00Z"
}
```

### 2.2 项目列表
`GET /api/v1/projects?status=&projectType=&keyword=&page=&pageSize=`

响应字段：项目 ID、名称、类型、题材、当前阶段、进度、待审核数量、累计成本、更新时间。

### 2.3 项目详情
`GET /api/v1/projects/{projectId}`

返回项目基础信息、当前正式分析版本、当前正式剧本版本、流程状态统计。

### 2.4 更新项目
`PATCH /api/v1/projects/{projectId}`

可更新字段：名称、类型、题材、目标时长、目标集数、画幅、语言、风格方向、备注。

### 2.5 项目概览
`GET /api/v1/projects/{projectId}/overview`

响应：
```json
{
  "project": {},
  "progress": [
    {"step": "novel", "status": "completed"},
    {"step": "analysis", "status": "review"}
  ],
  "stats": {
    "characters": 8,
    "scenes": 12,
    "shots": 86,
    "generatedVideos": 15,
    "pendingReviews": 6,
    "totalCost": 128.5
  }
}
```

---

## 3. 小说输入 API

### 3.1 保存小说文本
`POST /api/v1/projects/{projectId}/novel-documents`

请求：
```json
{
  "title": "第一版小说文本",
  "sourceType": "paste",
  "rawText": "小说正文..."
}
```

### 3.2 获取小说文档
`GET /api/v1/projects/{projectId}/novel-documents`

### 3.3 更新小说文档
`PATCH /api/v1/novel-documents/{documentId}`

### 3.4 保存章节
`POST /api/v1/novel-documents/{documentId}/chapters`

请求：
```json
{
  "chapterNo": 1,
  "title": "第一章 雨夜",
  "content": "章节正文..."
}
```

### 3.5 章节列表
`GET /api/v1/novel-documents/{documentId}/chapters`

### 3.6 上传小说文件
`POST /api/v1/projects/{projectId}/novel-upload`

表单：`multipart/form-data`，字段 `file`。

---

## 4. AI 小说分析 API

### 4.1 发起小说分析任务
`POST /api/v1/projects/{projectId}/analysis-tasks`

请求：
```json
{
  "novelDocumentId": "doc_uuid",
  "analysisScope": "full",
  "outputLevel": "detailed",
  "modelProviderId": "model_uuid"
}
```

响应：
```json
{
  "taskId": "task_uuid",
  "status": "queued"
}
```

### 4.2 分析版本列表
`GET /api/v1/projects/{projectId}/analysis-versions`

### 4.3 分析版本详情
`GET /api/v1/analysis-versions/{versionId}`

### 4.4 编辑分析版本
`PATCH /api/v1/analysis-versions/{versionId}`

请求：
```json
{
  "theme": "人性与复仇",
  "summary": "故事梗概...",
  "plotStructure": {},
  "characters": [],
  "scenes": [],
  "props": [],
  "emotionCurve": []
}
```

### 4.5 确认分析版本
`POST /api/v1/analysis-versions/{versionId}/confirm`

请求：
```json
{
  "comment": "确认该版本作为后续剧本输入"
}
```

效果：将当前版本置为 `confirmed`，同项目其他分析版本置为 `history`，更新项目 `currentAnalysisVersionId`。

### 4.6 重新生成分析
`POST /api/v1/analysis-versions/{versionId}/regenerate`

请求：
```json
{
  "instruction": "加强人物关系和悬疑反转分析",
  "modelProviderId": "model_uuid"
}
```

---

## 5. 剧本 API

### 5.1 发起剧本生成任务
`POST /api/v1/projects/{projectId}/script-tasks`

请求：
```json
{
  "analysisVersionId": "analysis_uuid",
  "scriptType": "episode_scene_script",
  "episodeCount": 10,
  "styleInstruction": "短剧节奏，强钩子，结尾反转",
  "modelProviderId": "model_uuid"
}
```

### 5.2 剧本版本列表
`GET /api/v1/projects/{projectId}/script-versions`

### 5.3 剧本版本详情
`GET /api/v1/script-versions/{versionId}`

### 5.4 编辑剧本版本
`PATCH /api/v1/script-versions/{versionId}`

请求字段：`title`、`logline`、`episodes`、`scenes`、`fullText`。

### 5.5 确认剧本版本
`POST /api/v1/script-versions/{versionId}/confirm`

### 5.6 剧本版本对比
`GET /api/v1/script-versions/{versionId}/diff?targetVersionId=xxx`

### 5.7 从剧本提取资产候选
`POST /api/v1/script-versions/{versionId}/extract-assets`

响应：角色候选、场景候选、风格候选、道具候选、声音候选。

---

## 6. 资产卡 API

### 6.1 资产卡总览
`GET /api/v1/projects/{projectId}/asset-cards?type=&reviewStatus=&keyword=`

响应：
```json
{
  "characters": [],
  "scenes": [],
  "styles": [],
  "props": [],
  "voices": []
}
```

### 6.2 发起资产卡生成任务
`POST /api/v1/projects/{projectId}/asset-card-tasks`

请求：
```json
{
  "scriptVersionId": "script_uuid",
  "assetTypes": ["character", "scene", "style"],
  "modelProviderId": "model_uuid"
}
```

### 6.3 创建角色卡
`POST /api/v1/projects/{projectId}/characters`

### 6.4 获取角色卡详情
`GET /api/v1/characters/{cardId}`

### 6.5 更新角色卡
`PATCH /api/v1/characters/{cardId}`

### 6.6 确认角色卡
`POST /api/v1/characters/{cardId}/confirm`

### 6.7 场景卡接口
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/projects/{projectId}/scenes` | 创建场景卡 |
| GET | `/api/v1/scenes/{cardId}` | 场景卡详情 |
| PATCH | `/api/v1/scenes/{cardId}` | 更新场景卡 |
| POST | `/api/v1/scenes/{cardId}/confirm` | 确认场景卡 |

### 6.8 风格卡接口
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/projects/{projectId}/styles` | 创建风格卡 |
| GET | `/api/v1/styles/{cardId}` | 风格卡详情 |
| PATCH | `/api/v1/styles/{cardId}` | 更新风格卡 |
| POST | `/api/v1/styles/{cardId}/confirm` | 确认风格卡 |

### 6.9 道具卡和声音卡接口
第一阶段可按同样模式提供：

```text
POST   /api/v1/projects/{projectId}/props
GET    /api/v1/props/{cardId}
PATCH  /api/v1/props/{cardId}
POST   /api/v1/props/{cardId}/confirm

POST   /api/v1/projects/{projectId}/voices
GET    /api/v1/voices/{cardId}
PATCH  /api/v1/voices/{cardId}
POST   /api/v1/voices/{cardId}/confirm
```

### 6.10 生成资产参考图
`POST /api/v1/asset-cards/{assetType}/{cardId}/image-tasks`

请求：
```json
{
  "promptMode": "use_card_prompt",
  "count": 4,
  "modelProviderId": "image_model_uuid",
  "parameters": {
    "aspectRatio": "9:16",
    "seed": 12345
  }
}
```

---

## 7. 媒体资产 API

### 7.1 上传媒体文件
`POST /api/v1/projects/{projectId}/media-assets`

表单字段：
| 字段 | 说明 |
|---|---|
| file | 文件 |
| assetType | reference_image/audio/document |
| sourceType | upload |
| relatedType | character/scene/style/shot |
| relatedId | 关联对象 ID |

### 7.2 媒体资产列表
`GET /api/v1/projects/{projectId}/media-assets?assetType=&relatedType=&relatedId=`

### 7.3 获取媒体详情
`GET /api/v1/media-assets/{assetId}`

### 7.4 获取下载/预览 URL
`GET /api/v1/media-assets/{assetId}/signed-url`

### 7.5 删除媒体资产
`DELETE /api/v1/media-assets/{assetId}`

建议第一阶段做软删除，避免影响历史版本追溯。

---

## 8. Storyboard API

### 8.1 发起 Storyboard 生成任务
`POST /api/v1/projects/{projectId}/storyboard-tasks`

请求：
```json
{
  "scriptVersionId": "script_uuid",
  "shotDensity": "medium",
  "defaultDurationSeconds": 4,
  "modelProviderId": "model_uuid"
}
```

### 8.2 镜头列表
`GET /api/v1/projects/{projectId}/shots?episodeNo=&sceneNo=&reviewStatus=&page=&pageSize=`

### 8.3 镜头详情
`GET /api/v1/shots/{shotId}`

### 8.4 创建镜头
`POST /api/v1/projects/{projectId}/shots`

### 8.5 更新镜头
`PATCH /api/v1/shots/{shotId}`

可更新字段：画面描述、景别、机位、运镜、角色、场景、道具、台词、旁白、时长、提示词、排序。

### 8.6 确认镜头
`POST /api/v1/shots/{shotId}/confirm`

### 8.7 批量确认镜头
`POST /api/v1/projects/{projectId}/shots/batch-confirm`

请求：
```json
{
  "shotIds": ["shot_1", "shot_2"],
  "comment": "分镜确认"
}
```

### 8.8 重新生成镜头提示词
`POST /api/v1/shots/{shotId}/prompt-regenerate`

请求：
```json
{
  "instruction": "加强悬疑氛围和冷色调",
  "includeAssets": true
}
```

---

## 9. 镜头生成任务 API

### 9.1 创建镜头生成任务
`POST /api/v1/shots/{shotId}/generation-tasks`

请求：
```json
{
  "taskType": "video_generation",
  "inputMode": "image_to_video",
  "modelProviderId": "video_model_uuid",
  "inputAssetIds": ["first_frame_asset_uuid"],
  "count": 2,
  "parameters": {
    "durationSeconds": 5,
    "aspectRatio": "9:16",
    "motionStrength": 0.6
  }
}
```

### 9.2 批量创建镜头生成任务
`POST /api/v1/projects/{projectId}/generation-tasks/batch`

请求：
```json
{
  "shotIds": ["shot_1", "shot_2"],
  "taskType": "image_generation",
  "modelProviderId": "image_model_uuid",
  "count": 1,
  "parameters": {}
}
```

### 9.3 任务列表
`GET /api/v1/projects/{projectId}/generation-tasks?status=&taskType=&shotId=`

### 9.4 任务详情
`GET /api/v1/generation-tasks/{taskId}`

### 9.5 取消任务
`POST /api/v1/generation-tasks/{taskId}/cancel`

### 9.6 重试任务
`POST /api/v1/generation-tasks/{taskId}/retry`

### 9.7 生成结果列表
`GET /api/v1/generation-tasks/{taskId}/results`

---

## 10. 审核 API

### 10.1 审核生成结果
`POST /api/v1/generation-results/{resultId}/review`

请求：
```json
{
  "action": "approve",
  "comment": "角色和场景一致，设为通过版本"
}
```

`action` 可选：`approve`、`reject`、`need_changes`、`discard`。

### 10.2 设置镜头通过版本
`POST /api/v1/shots/{shotId}/confirm-result`

请求：
```json
{
  "generationResultId": "result_uuid",
  "comment": "设为该镜头最终视频"
}
```

### 10.3 审核记录列表
`GET /api/v1/projects/{projectId}/review-records?targetType=&targetId=`

### 10.4 待审核列表
`GET /api/v1/projects/{projectId}/pending-reviews`

返回待确认分析、剧本、资产卡、镜头、生成结果和导出版本。

---

## 11. 后期预览与导出 API

### 11.1 创建预览导出任务
`POST /api/v1/projects/{projectId}/preview-tasks`

请求：
```json
{
  "shotIds": ["shot_1", "shot_2"],
  "useConfirmedResultsOnly": true,
  "exportSettings": {
    "resolution": "1080x1920",
    "fps": 25,
    "withSubtitle": true,
    "withAudio": true,
    "format": "mp4"
  }
}
```

### 11.2 导出版本列表
`GET /api/v1/projects/{projectId}/exports`

### 11.3 导出版本详情
`GET /api/v1/exports/{exportId}`

### 11.4 下载导出文件
`GET /api/v1/exports/{exportId}/download-url`

---

## 12. 任务中心 API

### 12.1 全局任务列表
`GET /api/v1/tasks?projectId=&status=&taskType=&page=&pageSize=`

### 12.2 任务日志
`GET /api/v1/tasks/{taskId}/logs`

### 12.3 任务状态轮询
`GET /api/v1/tasks/{taskId}/status`

响应：
```json
{
  "taskId": "task_uuid",
  "status": "running",
  "progress": 45,
  "message": "正在调用视频模型",
  "resultCount": 0
}
```

---

## 13. 模型配置 API

### 13.1 模型列表
`GET /api/v1/model-providers?modelType=&enabled=`

### 13.2 创建模型配置
`POST /api/v1/model-providers`

请求：
```json
{
  "provider": "openai",
  "modelName": "gpt-4.1",
  "modelType": "text",
  "capabilities": ["structured_output", "long_context"],
  "defaultParameters": {"temperature": 0.7},
  "costConfig": {"unit": "token", "inputPrice": 0.01, "outputPrice": 0.03},
  "secretRef": "OPENAI_API_KEY"
}
```

### 13.3 更新模型配置
`PATCH /api/v1/model-providers/{providerId}`

### 13.4 启用/禁用模型
`POST /api/v1/model-providers/{providerId}/toggle`

### 13.5 测试模型连接
`POST /api/v1/model-providers/{providerId}/test`

---

## 14. 提示词模板 API

### 14.1 模板列表
`GET /api/v1/prompt-templates?templateType=&enabled=`

### 14.2 创建模板
`POST /api/v1/prompt-templates`

### 14.3 模板详情
`GET /api/v1/prompt-templates/{templateId}`

### 14.4 更新模板
`PATCH /api/v1/prompt-templates/{templateId}`

### 14.5 渲染模板预览
`POST /api/v1/prompt-templates/{templateId}/render`

请求：
```json
{
  "variables": {
    "storySummary": "...",
    "characterCards": []
  }
}
```

---

## 15. 成本统计 API

### 15.1 项目成本概览
`GET /api/v1/projects/{projectId}/costs/summary`

### 15.2 成本明细
`GET /api/v1/projects/{projectId}/costs?modelType=&taskType=&startDate=&endDate=`

### 15.3 模型调用记录
`GET /api/v1/projects/{projectId}/model-invocations`

---

## 16. 权限建议

| 操作 | owner | editor | reviewer | viewer |
|---|---|---|---|---|
| 查看项目 | 是 | 是 | 是 | 是 |
| 编辑文本/剧本/资产 | 是 | 是 | 否 | 否 |
| 发起生成任务 | 是 | 是 | 否 | 否 |
| 审核通过 | 是 | 是 | 是 | 否 |
| 删除资产 | 是 | 否 | 否 | 否 |
| 模型配置 | 是 | 否 | 否 | 否 |

---

## 17. 第一阶段接口优先级

### P0 必做
项目、小说输入、分析任务、分析版本、剧本任务、剧本版本、资产卡、Storyboard、镜头生成任务、生成结果审核、媒体上传、任务轮询、预览导出。

### P1 增强
成本统计、模型测试、提示词模板、批量生成、版本对比、任务日志。

### P2 后续
复杂权限、通知、WebSocket 实时推送、资产复用推荐、工作流模板。
