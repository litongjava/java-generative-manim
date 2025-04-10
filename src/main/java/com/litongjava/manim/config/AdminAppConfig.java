package com.litongjava.manim.config;

import com.litongjava.annotation.AConfiguration;
import com.litongjava.annotation.Initialization;
import com.litongjava.manim.handler.ExplanationHandler;
import com.litongjava.manim.handler.TextMessageHander;
import com.litongjava.tio.boot.admin.config.TioAdminDbConfiguration;
import com.litongjava.tio.boot.server.TioBootServer;
import com.litongjava.tio.http.server.router.HttpRequestRouter;

@AConfiguration
public class AdminAppConfig {

  @Initialization
  public void config() {
    // 配置数据库相关
    new TioAdminDbConfiguration().config();
    //new TioAdminRedisDbConfiguration().config();
    //new TioAdminMongoDbConfiguration().config();
    //new TioAdminInterceptorConfiguration().config();
    //new TioAdminHandlerConfiguration().config();

    //    // 获取 HTTP 请求路由器
    TioBootServer server = TioBootServer.me();
    HttpRequestRouter r = server.getRequestRouter();
    if (r != null) {
      //      // 获取文件处理器，并添加文件上传和获取 URL 的接口
      //      SystemFileTencentCosHandler systemUploadHandler = Aop.get(SystemFileTencentCosHandler.class);
      //      r.add("/api/system/file/upload", systemUploadHandler::upload);
      //      r.add("/api/system/file/url", systemUploadHandler::getUrl);
      ExplanationHandler explanationHandler = new ExplanationHandler();
      r.add("/api/explanation/video", explanationHandler::index);
      TextMessageHander textMessageHander = new TextMessageHander();
      r.add("/sse", textMessageHander::send);
    }
    //
    //
    //    // 配置控制器
    //    new TioAdminControllerConfiguration().config();
  }
}
