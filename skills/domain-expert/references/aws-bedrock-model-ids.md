# AWS Bedrock Foundation Model IDs

此文件記錄 AWS Bedrock 中 Claude 4.5 系列和 Amazon Nova 系列模型的正確 Model ID。

## Claude 4.6 系列模型

### Claude Sonnet 4.6

- **Model ID**: `anthropic.claude-sonnet-4-6`
- **Provider**: Anthropic
- **Input Modalities**: Text, Image
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: Anthropic 最智能的模型,在編碼和複雜代理應用中表現出色
- **支援區域 (Cross-region inference profile)**:
  - af-south-1
  - ap-northeast-1, ap-northeast-2, ap-northeast-3
  - ap-south-1, ap-south-2
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-4
  - ca-central-1, ca-west-1
  - eu-central-1, eu-central-2
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-2, eu-west-3
  - me-south-1
  - mx-central-1
  - sa-east-1
  - us-east-1, us-east-2
  - us-west-1, us-west-2
  - us-gov-west-1, us-gov-east-1

### Claude Opus 4.6

- **Model ID**: `anthropic.claude-opus-4-6-v1`
- **Provider**: Anthropic
- **Input Modalities**: Text, Image
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 為生產級代碼、複雜代理和辦公任務設定新標準,提供 Opus 級別智能但成本降低三分之一
- **支援區域 (Cross-region inference profile)**:
  - ap-northeast-1, ap-northeast-2, ap-northeast-3
  - ap-south-1, ap-south-2
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-4
  - ca-central-1
  - eu-central-1, eu-central-2
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-2, eu-west-3
  - me-central-1
  - sa-east-1
  - us-east-1, us-east-2
  - us-west-1, us-west-2

### Claude Haiku 4.5

- **Model ID**: `anthropic.claude-haiku-4-5-20251001-v1:0`
- **Provider**: Anthropic
- **Input Modalities**: Text, Image
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 混合推理模型,提供近乎即時的回應和擴展思考以進行更深層推理
- **支援區域 (Cross-region inference profile)**:
  - ap-northeast-1, ap-northeast-2, ap-northeast-3
  - ap-south-1, ap-south-2
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-4
  - ca-central-1
  - eu-central-1, eu-central-2
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-2, eu-west-3
  - me-central-1
  - sa-east-1
  - us-east-1, us-east-2
  - us-west-1, us-west-2

## Amazon Nova 系列模型

### Nova 2 Lite

- **Model ID**: `amazon.nova-2-lite-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image, Video
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 輕量級多模態模型,支援文字、圖像和視頻輸入
- **支援區域 (Cross-region inference profile)**:
  - ap-east-2
  - ap-northeast-1, ap-northeast-2
  - ap-south-1
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-4, ap-southeast-5, ap-southeast-7
  - ca-central-1, ca-west-1
  - eu-central-1
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-2, eu-west-3
  - il-central-1
  - me-central-1
  - us-east-1, us-east-2
  - us-west-1, us-west-2

### Nova 2 Sonic

- **Model ID**: `amazon.nova-2-sonic-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Speech
- **Output Modalities**: Speech, Text
- **Streaming**: Yes
- **Description**: 語音處理模型,支援語音輸入和語音/文字輸出
- **支援區域 (Single-region)**:
  - ap-northeast-1
  - eu-north-1
  - us-east-1
  - us-west-2

### Nova Lite

- **Model ID**: `amazon.nova-lite-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image, Video
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 輕量級多模態基礎模型
- **支援區域 (Single-region)**:
  - ap-northeast-1
  - ap-southeast-2, ap-southeast-3
  - eu-north-1
  - eu-west-2
  - me-central-1
  - us-east-1
  - us-gov-west-1
- **支援區域 (Cross-region inference profile)**:
  - ap-east-2
  - ap-northeast-1, ap-northeast-2
  - ap-south-1
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-4, ap-southeast-5, ap-southeast-7
  - ca-central-1
  - eu-central-1
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-3
  - il-central-1
  - me-central-1
  - us-east-1, us-east-2
  - us-west-1, us-west-2

### Nova Micro

- **Model ID**: `amazon.nova-micro-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 超輕量級文字模型,適合快速回應場景
- **支援區域 (Single-region)**:
  - ap-southeast-2
  - eu-west-2
  - us-east-1
  - us-gov-west-1
- **支援區域 (Cross-region inference profile)**:
  - ap-east-2
  - ap-northeast-1, ap-northeast-2
  - ap-south-1
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-5, ap-southeast-7
  - eu-central-1
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-3
  - il-central-1
  - me-central-1
  - us-east-1, us-east-2
  - us-west-2

### Nova Premier

- **Model ID**: `amazon.nova-premier-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image, Video
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 旗艦級多模態模型,提供最高品質的理解和生成能力
- **支援區域 (Cross-region inference profile)**:
  - us-east-1, us-east-2
  - us-west-2

### Nova Pro

- **Model ID**: `amazon.nova-pro-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image, Video
- **Output Modalities**: Text
- **Streaming**: Yes
- **Description**: 專業級多模態模型,平衡性能與成本
- **支援區域 (Single-region)**:
  - ap-southeast-2, ap-southeast-3
  - eu-west-2
  - me-central-1
  - us-east-1
  - us-gov-west-1
- **支援區域 (Cross-region inference profile)**:
  - ap-east-2
  - ap-northeast-1, ap-northeast-2
  - ap-south-1
  - ap-southeast-1, ap-southeast-2, ap-southeast-3, ap-southeast-4, ap-southeast-5, ap-southeast-7
  - eu-central-1
  - eu-north-1
  - eu-south-1, eu-south-2
  - eu-west-1, eu-west-3
  - il-central-1
  - me-central-1
  - us-east-1, us-east-2
  - us-west-1, us-west-2

### Nova Canvas

- **Model ID**: `amazon.nova-canvas-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image
- **Output Modalities**: Image
- **Streaming**: No
- **Description**: 圖像生成模型
- **支援區域 (Single-region)**:
  - ap-northeast-1
  - eu-west-1
  - us-east-1

### Nova Reel

- **Model ID**: `amazon.nova-reel-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image
- **Output Modalities**: Video
- **Streaming**: No
- **Description**: 視頻生成模型
- **支援區域 (Single-region)**:
  - ap-northeast-1
  - eu-west-1
  - us-east-1

### Nova Reel v1.1

- **Model ID**: `amazon.nova-reel-v1:1`
- **Provider**: Amazon
- **Input Modalities**: Text, Image
- **Output Modalities**: Video
- **Streaming**: No
- **Description**: 視頻生成模型 (改進版本)
- **支援區域 (Single-region)**:
  - us-east-1

### Nova Sonic

- **Model ID**: `amazon.nova-sonic-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Speech
- **Output Modalities**: Speech, Text
- **Streaming**: Yes
- **Description**: 語音處理模型
- **支援區域 (Single-region)**:
  - ap-northeast-1
  - eu-north-1
  - us-east-1

### Nova Multimodal Embeddings

- **Model ID**: `amazon.nova-2-multimodal-embeddings-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text, Image, Audio, Video
- **Output Modalities**: Embedding
- **Streaming**: No
- **Description**: 多模態嵌入模型,支援文字、圖像、音頻和視頻
- **支援區域 (Single-region)**:
  - us-east-1

### Rerank 1.0

- **Model ID**: `amazon.rerank-v1:0`
- **Provider**: Amazon
- **Input Modalities**: Text
- **Output Modalities**: Text
- **Streaming**: No
- **Description**: 文本重排序模型,用於搜尋結果優化
- **支援區域 (Single-region)**:
  - ap-northeast-1
  - ca-central-1
  - eu-central-1
  - us-west-2

## 使用說明

### Inference Parameters

- **Claude 4.6 模型**的推理參數請參考:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html

- **Amazon Nova 模型**的推理參數請參考:  
  https://docs.aws.amazon.com/nova/latest/userguide/getting-started-schema.html

### Cross-Region Inference

這些模型支援 Cross-region inference profile,可以在同一地理區域內的多個區域進行推理調用。更多資訊請參考:
https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html

### 模型選擇建議

#### Claude 4.6 系列
- **Claude Sonnet 4.6**: 最適合複雜的編碼和代理任務,平衡智能與成本
- **Claude Opus 4.6**: 最高智能等級,適合生產級代碼和複雜辦公任務
- **Claude Haiku 4.5**: 快速回應,適合需要即時互動的場景

#### Amazon Nova 系列
- **Nova Premier**: 旗艦級模型,最高品質的多模態理解和生成
- **Nova Pro**: 專業級模型,平衡性能與成本
- **Nova Lite/2 Lite**: 輕量級模型,適合快速多模態處理
- **Nova Micro**: 超輕量級文字模型,適合簡單快速任務
- **Nova Canvas**: 專業圖像生成
- **Nova Reel**: 視頻生成
- **Nova Sonic/2 Sonic**: 語音處理和轉換

## 參考資料

- [AWS Bedrock 支援的模型列表](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [Claude Messages API 支援的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-supported-models.html)
- [Anthropic Claude Models in Amazon Bedrock](https://aws.amazon.com/bedrock/anthropic/)
- [Amazon Nova User Guide](https://docs.aws.amazon.com/nova/latest/userguide/)
- [AWS Bedrock Cross-Region Inference](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html)

---

**最後更新**: 2026-02-28
**資料來源**: AWS Bedrock 官方文件
