// index.js

// 🔥【核心配置】以后只改这里！会自动应用到下面所有链接
const SERVER_IP = "192.168.219.78:8000"; 

const wsUrl = `ws://${SERVER_IP}/ws`;
const apiUrl = `http://${SERVER_IP}/history`;
const staticBaseUrl = `http://${SERVER_IP}`; 

Page({
  data: {
    statusText: "等待连接...",
    isAlarm: false,
    targetName: "",
    confidence: "",
    alertImage: "", 
    historyLogs: []
  },

  onLoad: function () {
    this.connectSocket();
    this.fetchHistory(); 
  },

  onUnload: function() {
    wx.closeSocket();
  },

  connectSocket: function () {
    const that = this;
    
    // 这里的 url 已经自动使用了上面的 SERVER_IP，不用手动改了
    wx.connectSocket({
      url: wsUrl,
      success: () => {
        console.log("正在连接...", wsUrl);
        that.setData({ statusText: "连接中..." });
      }
    });

    wx.onSocketOpen(function () {
      console.log("✅ WebSocket 已连接");
      that.setData({ statusText: "监控正常", isAlarm: false });
    });

    wx.onSocketMessage(function (res) {
      // 加上 try-catch 防止解析非 JSON 数据报错
      try {
        const data = JSON.parse(res.data);
        console.log("收到服务端消息:", data);

        // 只要有检测结果，就视为报警 (兼容性更强)
        if (data.type === 'detection_alert' || data.detections) {
          that.setData({
            statusText: "⚠️ 发现目标！",
            isAlarm: true,
            targetName: data.top_object || "未知目标",
            confidence: data.conf || "0.0",
            alertImage: staticBaseUrl + data.image_url 
          });

          wx.vibrateLong();

          // 🔥🔥【关键修改】延迟 300ms 再拉取，等待数据库写入完成 🔥🔥
          setTimeout(() => {
             console.log("🔄 触发列表刷新...");
             that.fetchHistory(); 
          }, 300);

          // 5秒后恢复监控状态
          setTimeout(() => {
            that.setData({ statusText: "监控正常", isAlarm: false, alertImage: "" });
          }, 5000);
        }
      } catch (e) {
        console.error("解析消息失败:", e);
      }
    });

    wx.onSocketClose(function () {
      console.log("WebSocket 已断开");
      that.setData({ statusText: "连接断开" });
    });
    
    wx.onSocketError(function(err){
      console.error("连接失败", err);
      that.setData({ statusText: "连接失败" });
    });
  },

  fetchHistory: function() {
    const that = this;
    // 🔥 给 URL 加个随机时间戳，强制微信不使用缓存，每次都去服务器拿最新的
    const noCacheUrl = `${apiUrl}?t=${Date.now()}`;

    wx.request({
      url: noCacheUrl,
      method: 'GET',
      success(res) {
        console.log("📜 历史记录已更新，共", res.data.length, "条");
        const logs = res.data.map(item => {
          // 简单的防崩溃处理
          if(item.timestamp) {
             item.shortTime = item.timestamp.substring(11, 19);
          } else {
             item.shortTime = "--:--:--";
          }
          
          if (item.image_url) {
            item.fullImageUrl = staticBaseUrl + item.image_url;
          }
          return item;
        });
        that.setData({ historyLogs: logs });
      },
      fail(err) {
        console.error("拉取历史失败:", err);
      }
    });
  },

  viewEvidence: function(e) {
    const imgUrl = e.currentTarget.dataset.url;
    if (imgUrl) {
      console.log("正在查看证据:", imgUrl);
      wx.previewImage({
        current: imgUrl, 
        urls: [imgUrl] 
      });
    } else {
      wx.showToast({
        title: '该记录无现场画面',
        icon: 'none'
      });
    }
  }
});