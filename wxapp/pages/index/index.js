// index.js
Page({
  data: {
    statusText: "等待连接...",
    isAlarm: false,
    targetName: "",
    confidence: ""
  },

  onLoad: function () {
    this.connectSocket();
  },

  onUnload: function() {
    wx.closeSocket();
  },

  connectSocket: function () {
    const that = this;
    // ⚠️ 把这里换成你的电脑 IP！！！
    const wsUrl = "ws://192.168.219.78:8000/ws"; 

    wx.connectSocket({
      url: wsUrl,
      success: () => {
        console.log("正在连接...");
        that.setData({ statusText: "连接中..." });
      }
    });

    wx.onSocketOpen(function () {
      console.log("✅ WebSocket 已连接");
      that.setData({ statusText: "监控正常", isAlarm: false });
    });

    wx.onSocketMessage(function (res) {
      console.log("收到消息:", res.data);
      const data = JSON.parse(res.data);

      if (data.type === 'detection_alert') {
        // 收到报警！变红！
        that.setData({
          statusText: "⚠️ 发现目标！",
          isAlarm: true,
          targetName: data.top_object,
          confidence: data.conf
        });

        // 震动一下手机 (真机体验极佳)
        wx.vibrateLong();

        // 3秒后自动恢复正常
        setTimeout(() => {
          that.setData({ statusText: "监控正常", isAlarm: false });
        }, 3000);
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
  }
});