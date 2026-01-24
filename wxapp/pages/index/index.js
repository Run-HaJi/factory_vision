// index.js
const SERVER_IP = "192.168.219.78:8000"; 
const wsUrl = `ws://${SERVER_IP}/ws`;
const apiUrl = `http://${SERVER_IP}/history`;
const staticBaseUrl = `http://${SERVER_IP}`; // 用于拼接图片地址

Page({
  data: {
    statusText: "等待连接...",
    isAlarm: false,
    targetName: "",
    confidence: "",
    alertImage: "",  // 🔥 新增：用于显示报警图片
    historyLogs: []
  },

  onLoad: function () {
    this.connectSocket();
    this.fetchHistory(); // 🔥 启动时先拉取一次历史
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
      const data = JSON.parse(res.data);
      if (data.type === 'detection_alert') {
        that.setData({
          statusText: "⚠️ 发现目标！",
          isAlarm: true,
          targetName: data.top_object,
          confidence: data.conf,
          // 🔥 拼接实时图片地址
          alertImage: staticBaseUrl + data.image_url 
        });

        that.fetchHistory(); 
        wx.vibrateLong();

        // 5秒后恢复 (时间加长点，不然图片还没看清就没了)
        setTimeout(() => {
          that.setData({ statusText: "监控正常", isAlarm: false, alertImage: "" });
        }, 5000);
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
    wx.request({
      url: apiUrl,
      method: 'GET',
      success(res) {
        const logs = res.data.map(item => {
          item.shortTime = item.timestamp.substring(11, 19);
          // 如果数据库里有图片路径，就拼接完整
          if (item.image_url) {
            item.fullImageUrl = staticBaseUrl + item.image_url;
          }
          return item;
        });
        that.setData({ historyLogs: logs });
      }
    });
  }
});