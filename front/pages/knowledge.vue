<template>
    <div id="app" class="app-container">
      <!-- 文档检索模块 -->
      <el-card class="search-section">
        <h2>知识检索</h2>
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
        searchQuery: '',
        searchResults: []
      };
    },
    methods: {
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
    width: 100%;
    margin: 20px 0;
    padding: 20px;
  }
  
  .search-section {
    margin-bottom: 30px;
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
  </style>