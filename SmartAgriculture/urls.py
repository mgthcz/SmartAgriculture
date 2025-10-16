"""
URL configuration for text_325 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from ImageDetectionAndCounting import views_ImageDetectionAndCounting  # 图片检测与计数
from VideoTrackingCount import views_VideoTrackingCount
from PhotoDetectionAndRecognition import views_PhotoDetectionAndRecognition
from AiAgricultureExpertsAnswerQuestions import views_AiAgricultureExpertsAnswerQuestions
from index_home import views_index

urlpatterns = [
    # 管理员系统
    path('admin/', admin.site.urls),

    # 0.主页面 index_home/
    path('', views_index.viewsindex, name='index_home'),
    path('get_models_datas/', views_index.get_models_datas, name='get_models_datas'),  # 实时更新数据
    path('insert_temtime_data/', views_index.insert_temtime_data, name='insert_temtime_data'),  # 插入时间数据
    path('On_off_ontrol/', views_index.On_off_ontrol, name='On_off_ontrol'),  # 控制按钮
    path('wechat/', views_index.wechat, name='wechat'),  # 微信公众号提示
    path('update_user_settings/', views_index.update_user_settings, name='update_user_settings'),  # 更新用户极大极小值设置

    # 1.图片检测与计数
    path('ImageDetectionAndCounting/', views_ImageDetectionAndCounting.ImageDetectionAndCounting,
         name='ImageDetectionAndCounting'),

    # 2.视频上传与检测
    path('VideoTrackingCount/', views_VideoTrackingCount.upload, name='VideoTrackingCount'),
    path('process_video/', views_VideoTrackingCount.process_video, name='process_video'),  # 视频处理及其路由上传
    path('video_chart/', views_VideoTrackingCount.get_chart_data, name='video_chart'),  # 图表数据上传

    # 拍照上传检测
    path('PhotoDetectionAndRecognition/', views_PhotoDetectionAndRecognition.camera_capture_view,
         name='PhotoDetectionAndRecognition'),
    path('capture_and_process/', views_PhotoDetectionAndRecognition.capture_and_process,
         name='capture_and_process'),  # 图片处理上传

    # 智能问答模块
    path('AiAgricultureExpertsAnswerQuestions/',
         views_AiAgricultureExpertsAnswerQuestions.AiAgricultureExpertsAnswerQuestions,
         name='AiAgricultureExpertsAnswerQuestions'),
]

# 针对媒体文件的 URL 路由配置
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
