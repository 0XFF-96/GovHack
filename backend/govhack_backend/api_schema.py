"""
API Schema customization for OpenAPI/Swagger documentation
"""

def preprocessing_filter_spec(endpoints):
    """
    Filter and modify API endpoints before schema generation
    """
    if not endpoints:
        return []
        
    # Remove Django admin and other internal endpoints from API docs
    filtered = []
    for endpoint in endpoints:
        if len(endpoint) >= 4:  # 确保endpoint格式正确
            path, path_regex, method, callback = endpoint[:4]
            # Skip admin URLs
            if path.startswith('/admin/'):
                continue
            # Skip schema URLs themselves
            if path.startswith('/api/schema/') or path.startswith('/api/docs/') or path.startswith('/api/redoc/'):
                continue
            filtered.append(endpoint)
    
    return filtered


def postprocessing_hook(result, generator, request, public):
    """
    Modify the generated OpenAPI schema
    """
    if not result:
        return {}
    
    # Add custom tags and grouping
    if 'paths' in result and result['paths']:
        for path, path_item in result['paths'].items():
            if isinstance(path_item, dict):
                for method, operation in path_item.items():
                    if method in ['get', 'post', 'put', 'patch', 'delete'] and isinstance(operation, dict):
                        # Add tags based on URL patterns
                        if '/chat/' in path:
                            operation.setdefault('tags', []).append('聊天对话')
                        elif '/data/' in path:
                            operation.setdefault('tags', []).append('数据处理')
                        elif '/trust/' in path:
                            operation.setdefault('tags', []).append('信任评分')
                        elif '/audit/' in path:
                            operation.setdefault('tags', []).append('审计追踪')
                        elif '/datasets/' in path:
                            operation.setdefault('tags', []).append('数据集管理')
    
    # Add custom info
    result.setdefault('info', {}).update({
        'contact': {
            'name': 'GovHack Team',
            'email': 'team@govhack.example.com'
        },
        'license': {
            'name': 'MIT License',
            'url': 'https://opensource.org/licenses/MIT'
        },
        'termsOfService': 'https://example.com/terms/',
    })
    
    # Add servers info
    result.setdefault('servers', []).extend([
        {
            'url': 'http://localhost:8000',
            'description': '开发环境'
        },
        {
            'url': 'https://api.govhack.example.com',
            'description': '生产环境'
        }
    ])
    
    # Add security schemes
    result.setdefault('components', {}).setdefault('securitySchemes', {}).update({
        'sessionAuth': {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid',
            'description': 'Django会话认证'
        }
    })
    
    return result