<template>
  <div class="upload-requirement">
    <el-button
      :loading="loading"
      type="primary"
      @click="openUploadDialog"
      :size="size"
    >
      {{ buttonText }}
    </el-button>

    <el-dialog
      title="上传需求文档"
      :visible.sync="uploadDialogVisible"
      width="400px"
      top="15vh"
    >
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
        :auto-upload="false"
        :show-file-list="true"
        :drag="true"
      >
        <div class="el-upload-dragger">
          <i class="el-icon-upload"></i>
          <div class="el-upload__text">
            <em>点击或拖拽文件到此处上传</em>
          </div>
          <div class="el-upload__tip mt-2">支持上传PDF/Markdown文件，单文件最大20MB</div>
        </div>
      </el-upload>

      <el-alert
        v-if="uploadStatus.show"
        :title="uploadStatus.message"
        :type="uploadStatus.type"
        show-icon
        class="status-alert"
      />

      <div slot="footer" class="dialog-footer" style="display: flex; justify-content: flex-end; padding: 10px 20px;">
        <el-button @click="uploadDialogVisible = false" size="mini" style="width: 100px;">取 消</el-button>
        <el-button type="primary" @click="submitUpload" :loading="loading" size="mini" style="width: 100px; margin-left: 20px;">上 传</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'UploadRequirement',
  props: {
    buttonText: {
      type: String,
      default: '上传需求'
    },
    size: {
      type: String,
      default: 'mini'
    },
    uploadUrl: {
      type: String,
      default: 'http://127.0.0.1:5000/api/v1/file/upload'
    }
  },
  data() {
    return {
      uploadDialogVisible: false,
      loading: false,
      uploadStatus: {
        show: false,
        type: 'success',
        message: ''
      }
    }
  },
  methods: {
    openUploadDialog() {
      console.log('上传按钮被点击');
      this.uploadDialogVisible = true;
    },
    submitUpload() {
      if (this.$refs.uploadRef) {
        this.loading = true;
        this.$refs.uploadRef.submit();
      }
    },
    handleUploadSuccess(response) {
      console.log('上传成功:', response);
      this.loading = false;

      if (response && response.data && response.data.added_nodes !== undefined) {
        this.showStatusAlert(
          `成功添加 ${response.data.added_nodes} 个文本块`,
          'success'
        );
        // 上传成功后通知父组件刷新数据
        this.$emit('uploadSuccess');
        setTimeout(() => {
          this.uploadDialogVisible = false;
        }, 1500);
      } else {
        console.error('无效的响应结构:', response);
        this.showStatusAlert('上传成功但响应格式异常', 'warning');
      }
    },
    handleUploadError(err) {
      console.error('上传失败:', err);
      this.loading = false;
      this.showStatusAlert('文件上传失败，请重试', 'error');
    },
    handleExceed() {
      this.$message.warning('每次只能上传一个文件，请先移除当前文件');
    },
    beforeUpload(file) {
      this.loading = true;
      const isAllowedType = ['application/pdf', 'text/markdown'].includes(file.type);
      if (!isAllowedType) {
        this.$message.error('只能上传 PDF 或 Markdown 文件');
        this.loading = false;
        return false;
      }

      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        this.$message.error('文件大小不能超过 20MB');
        this.loading = false;
        return false;
      }

      return true;
    },
    showStatusAlert(message, type = 'success') {
      this.uploadStatus = {
        show: true,
        type,
        message
      };
      setTimeout(() => {
        this.uploadStatus.show = false;
      }, 3000);
    }
  }
}
</script>

<style scoped>
.status-alert {
  margin-top: 15px;
}

.el-dialog__header {
  width: 400px;
  box-sizing: border-box;
}

/* 使用更具体的选择器结合::v-deep和!important */
::v-deep .el-dialog .el-dialog__body {
  width: 400px !important;
  box-sizing: border-box !important;
  padding: 10px 20px !important;
  /* 确保上下padding为10px */
  padding-top: 10px !important;
  padding-bottom: 10px !important;
}

.upload-demo {
  width: 100%;
}
</style>