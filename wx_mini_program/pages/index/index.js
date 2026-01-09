const app = getApp()

// CHANGE THIS TO YOUR SERVER URL
// For local testing in simulator: http://localhost:8000/analyze (Check "Does not verify domain names")
// For production: https://bmwuv.com/analyze
const API_URL = 'https://bmwuv.com/analyze'; 

Page({
  data: {
    jdText: '',
    resumeFile: null,
    persona: 'hrbp',
    loading: false,
    result: null
  },

  onJdInput(e) {
    this.setData({
      jdText: e.detail.value
    });
  },

  onPersonaChange(e) {
    this.setData({
      persona: e.detail.value
    });
  },

  chooseResume() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf', 'docx', 'doc', 'txt', 'md'],
      success: (res) => {
        const file = res.tempFiles[0];
        // Simple validation
        const ext = file.name.split('.').pop().toLowerCase();
        if (['pdf', 'docx', 'doc', 'txt', 'md'].indexOf(ext) === -1) {
          wx.showToast({
            title: '不支持的文件格式',
            icon: 'none'
          });
          return;
        }
        
        this.setData({
          resumeFile: file,
          result: null // Clear previous result
        });
      },
      fail: (err) => {
        console.error('Choose file failed', err);
      }
    });
  },

  startAnalysis() {
    if (!this.data.jdText) {
      wx.showToast({
        title: '请填写 JD',
        icon: 'none'
      });
      return;
    }
    if (!this.data.resumeFile) {
      wx.showToast({
        title: '请上传简历',
        icon: 'none'
      });
      return;
    }

    this.setData({ loading: true });
    wx.showLoading({
      title: '正在诊断中...',
      mask: true
    });

    wx.uploadFile({
      url: API_URL,
      filePath: this.data.resumeFile.path,
      name: 'resume_file',
      formData: {
        'jd_text': this.data.jdText,
        'persona': this.data.persona
      },
      success: (res) => {
        console.log('Upload success', res);
        try {
          // wx.uploadFile returns data as string
          const data = JSON.parse(res.data);
          
          if (res.statusCode !== 200) {
            throw new Error(data.detail || 'Server Error');
          }

          this.setData({
            result: data
          });
          
          wx.showToast({
            title: '诊断完成',
            icon: 'success'
          });
        } catch (e) {
          console.error('Parse error', e);
          wx.showModal({
            title: '错误',
            content: e.message || '解析响应失败',
            showCancel: false
          });
        }
      },
      fail: (err) => {
        console.error('Upload failed', err);
        wx.showModal({
          title: '网络错误',
          content: err.errMsg,
          showCancel: false
        });
      },
      complete: () => {
        this.setData({ loading: false });
        wx.hideLoading();
      }
    });
  }
})
