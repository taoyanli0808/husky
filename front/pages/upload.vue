<template>
    <div id="app" class="app-container">
      <!-- 文档上传模块 -->
      <el-card class="upload-section">
        <h2>文档上传</h2>
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          name="file"
          :limit="1"
          :action="uploadUrl"
          :multiple="false"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :on-exceed="handleExceed"
          :before-upload="beforeUpload"
          :auto-upload="true"
          :show-file-list="false"
        >
          <el-button size="medium" type="primary">点击上传</el-button>
          <div slot="tip" class="el-upload__tip">支持上传PDF/Markdown文件，单文件最大10MB</div>
        </el-upload>
        <el-alert
          v-if="uploadStatus.show"
          :title="uploadStatus.message"
          :type="uploadStatus.type"
          show-icon
          class="status-alert"
        />
      </el-card>
  
      <!-- 文档检索模块 -->
      <el-card class="search-section">
        <h2>文档检索</h2>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="输入问题..."
            class="search-input"
            @keyup.enter.native="handleSearch"
          >
            <el-button
              slot="append"
              icon="el-icon-search"
              type="primary"
              @click="handleSearch"
            />
          </el-input>
        </div>
        
        <div v-if="searchResults.length" class="results-container">
          <h3>检索结果（{{ searchResults.length }} 条）</h3>
          <el-card
            v-for="(result, index) in searchResults"
            :key="index"
            class="result-item"
          >
            <div class="result-header">
              <el-tag type="info">相关度 {{ result.score.toFixed(2) }}</el-tag>
              <span class="doc-source">来源：文档 {{ result.doc_id }}</span>
            </div>
            <p class="result-text">{{ result.text.slice(0, 250) }}...</p>
          </el-card>
        </div>
      </el-card>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'App',
    data() {
      return {
        uploadUrl: 'http://127.0.0.1:5000/api/v1/file/upload', 
        searchQuery: '',
        uploadStatus: {
          show: false,
          type: 'success',
          message: ''
        },
        searchResults: []
      };
    },
    methods: {
      // 处理文件上传成功
      handleUploadSuccess(response, file, fileList) {
        this.$nextTick(() => {
          if (this.$refs.uploadRef) {
            this.$refs.uploadRef.clearFiles();
          }
        });

        // 正确处理嵌套的响应结构
        if (response && response.data && response.data.added_nodes !== undefined) {
          this.showStatusAlert(
            `成功添加 ${response.data.added_nodes} 个文本块`,
            'success'
          );
        } else {
          console.error('无效的响应结构:', response);
          this.showStatusAlert('上传成功但响应格式异常', 'warning');
        }
      },
  
      // 处理上传错误
      handleUploadError(err) {
        console.error('上传失败:', err);
        this.showStatusAlert('文件上传失败，请重试', 'error');
      },

      // 添加文件超出限制处理
      handleExceed() {
        this.$message.warning('每次只能上传一个文件，请先移除当前文件');
      },

      beforeUpload(file) {
        // 检查文件类型
        const isAllowedType = ['application/pdf', 'text/markdown'].includes(file.type);
        if (!isAllowedType) {
          this.$message.error('只能上传 PDF 或 Markdown 文件');
          return false;
        }
        
        // 检查文件大小 (10MB)
        const isLt10M = file.size / 1024 / 1024 < 10;
        if (!isLt10M) {
          this.$message.error('文件大小不能超过 10MB');
          return false;
        }
        
        return true;
      },
  
      // 显示状态提示
      showStatusAlert(message, type = 'success') {
        this.uploadStatus = {
          show: true,
          type,
          message
        };
        setTimeout(() => {
          this.uploadStatus.show = false;
        }, 3000);
      },
  
      // 执行搜索
      handleSearch() {
        if (!this.searchQuery.trim()) {
          this.$message.warning('请输入搜索内容');
          return;
        }
  
        this.$axios.post('/search', {q: this.searchQuery})
          .then((res) => {
            console.log('搜索结果:', res)
            this.searchResults = res.data.results
          })
          .catch((error) => {
            console.error('搜索失败:', error)
            this.searchResults = [] // 确保重置为空数组
            this.$message.error('搜索失败：' + (error.response?.data?.message || '网络异常'))
          })
      }
    }
  };
  </script>
  
  <style>
  .app-container {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
  }
  
  .upload-section, .search-section {
    margin-bottom: 30px;
  }
  
  .upload-demo {
    margin: 20px 0;
  }
  
  .search-box {
    margin: 20px 0;
  }
  
  .search-input {
    margin-bottom: 15px;
  }
  
  .results-container {
    margin-top: 20px;
  }
  
  .result-item {
    margin: 10px 0;
    padding: 15px;
  }
  
  .result-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .doc-source {
    margin-left: 15px;
    color: #666;
    font-size: 0.9em;
  }
  
  .result-text {
    color: #333;
    line-height: 1.6;
  }
  
  .status-alert {
    margin-top: 15px;
  }
  
  .el-upload__tip {
    margin-top: 8px;
    color: #999;
    font-size: 12px;
  }
  </style>