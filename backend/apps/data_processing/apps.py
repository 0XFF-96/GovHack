from django.apps import AppConfig


class DataProcessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data_processing'
    verbose_name = '数据处理'