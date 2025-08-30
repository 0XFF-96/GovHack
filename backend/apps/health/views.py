from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import time


@csrf_exempt
def health_check(request):
    """系统健康检查端点"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {},
        "metrics": {}
    }
    
    # 检查数据库连接
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # 检查Redis连接
    try:
        cache_key = "health_check"
        cache.set(cache_key, "ok", 30)
        result = cache.get(cache_key)
        if result == "ok":
            health_status["checks"]["cache"] = "ok"
        else:
            health_status["checks"]["cache"] = "error: cache test failed"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["cache"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # 检查磁盘空间
    try:
        import shutil
        total, used, free = shutil.disk_usage("/app")
        free_percent = (free / total) * 100
        
        if free_percent > 10:
            health_status["checks"]["disk_space"] = "ok"
        else:
            health_status["checks"]["disk_space"] = f"warning: only {free_percent:.1f}% free"
        
        health_status["metrics"]["disk"] = {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "free_percent": round(free_percent, 1)
        }
    except Exception as e:
        health_status["checks"]["disk_space"] = f"error: {str(e)}"
    
    # 添加一些基本指标
    health_status["metrics"].update({
        "debug_mode": settings.DEBUG,
        "django_version": getattr(settings, 'DJANGO_VERSION', 'unknown'),
    })
    
    # 根据健康状态返回适当的HTTP状态码
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JsonResponse(health_status, status=status_code)