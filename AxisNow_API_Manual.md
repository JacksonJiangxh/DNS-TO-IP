# AxisNow API 完整使用调用手册

## 目录

1. [API 概述](#1-api-概述)
2. [认证方式](#2-认证方式)
3. [API 基础信息](#3-api-基础信息)
4. [核心模块详解](#4-核心模块详解)
   - 4.1 [DNS 路由规则 (DNS Routing Rules)](#41-dns-路由规则-dns-routing-rules)
   - 4.2 [DNS 路由域名 (DNS Routing Domains)](#42-dns-路由域名-dns-routing-domains)
   - 4.3 [DNS 提供商 (DNS Providers)](#43-dns-提供商-dns-providers)
   - 4.4 [DNS 记录 (DNS Records)](#44-dns-记录-dns-records)
   - 4.5 [集群 (Clusters)](#45-集群-clusters)
   - 4.6 [边缘节点 (Edges)](#46-边缘节点-edges)
   - 4.7 [计费 (Billing)](#47-计费-billing)
   - 4.8 [工作负载标识 (Workload Identity)](#48-工作负载标识-workload-identity)
   - 4.9 [包管理 (Packages)](#49-包管理-packages)
   - 4.10 [环境 (Environments)](#410-环境-environments)
5. [完整模块列表](#5-完整模块列表)
6. [错误处理](#6-错误处理)
7. [curl 命令示例 (Windows CMD/PowerShell)](#7-curl-命令示例-windows-cmdpowershell)
8. [Python 客户端示例](#8-python-客户端示例)

---

## 1. API 概述

### 1.1 简介

AxisNow Client API 是一个功能强大的客户端 API，用于与 AxisNow 平台的产品和服务进行交互。该 API 遵循 OpenAPI 3.1.0 规范，提供了 RESTful 风格的接口，支持 DNS 管理、边缘计算部署、计费管理等多种功能。

### 1.2 主要功能

- **智能 DNS 路由**：支持动态 DNS 路由规则管理，实现智能流量分配
- **多 DNS 提供商集成**：支持 Cloudflare、阿里云、DNSPod、华为云、AWS Route 53、ClouDNS 等主流 DNS 服务提供商
- **边缘节点管理**：支持边缘节点的部署、升级、监控等完整生命周期管理
- **集群管理**：支持集群的创建、配置和扩缩容
- **计费管理**：支持订阅计划、发票管理、支付方式更新等
- **工作负载标识**：支持客户端工作负载的身份识别和管理

### 1.3 API 规范

| 属性 | 值 |
|------|-----|
| 规范版本 | OpenAPI 3.1.0 |
| API 版本 | 0.0.1 |
| 许可证 | BSD-3-Clause |
| 协议 | HTTPS |
| 数据格式 | JSON |

---

## 2. 认证方式

### 2.1 API Token 认证

大多数 API 端点使用 API Token 进行认证。认证方式为在请求头中包含 Bearer Token：

```
Authorization: Bearer <your-api-token>
```

**注意**：不同的功能模块可能需要不同的 API Token 权限范围。

### 2.2 客户端 ID 认证

部分端点（如获取客户端配置）使用 Client ID 进行认证。

### 2.3 Stripe Webhook 密钥

Stripe Webhook 端点使用 Stripe 私钥进行验证签名。

### 2.4 无认证端点

部分端点（如包版本查询、环境信息）不需要认证。

---

## 3. API 基础信息

### 3.1 API 服务器地址

```
https://api.axisnow.io/client/v1
```

### 3.2 通用响应格式

#### 成功响应

```json
{
  "success": true,
  "messages": [],
  "errors": [],
  "result": {
    "items": [],
    "result_info": {
      "page": 1,
      "per_page": 20,
      "count": 10,
      "total_count": 100
    }
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "messages": [
    {
      "code": "ERROR_CODE",
      "message": "错误描述"
    }
  ],
  "errors": []
}
```

### 3.3 分页参数

| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `page` | integer | 页码，从1开始 | 1 |
| `per_page` | integer | 每页返回数量 | 20 |

---

## 4. 核心模块详解

---

### 4.1 DNS 路由规则 (DNS Routing Rules)

#### 4.1.1 模块概述

DNS 路由规则模块用于管理智能 DNS 路由规则，支持基于地理位置、延迟、健康状态等条件的动态流量分配。

#### 4.1.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/dns_routing_rules` | 列出所有 DNS 路由规则 |
| POST | `/dns_routing_rules` | 创建新的 DNS 路由规则 |
| GET | `/dns_routing_rules/{uuid}` | 获取单个 DNS 路由规则详情 |
| PUT | `/dns_routing_rules/{uuid}` | 更新 DNS 路由规则 |
| DELETE | `/dns_routing_rules/{uuid}` | 删除 DNS 路由规则 |
| POST | `/dns_routing_rules/filter` | 按条件筛选 DNS 路由规则 |
| POST | `/dns_routing_rules/events/filter` | 筛选 DNS 路由规则事件 |

#### 4.1.3 调用示例

**示例 1：列出所有 DNS 路由规则**

```python
import requests

API_URL = "https://api.axisnow.io/client/v1"
API_TOKEN = "your-api-token"

def list_dns_rules(page=1, per_page=20):
    """
    列出所有 DNS 路由规则
    
    Args:
        page: 页码
        per_page: 每页数量
    
    Returns:
        DNS 路由规则列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(
        f"{API_URL}/dns_routing_rules",
        headers=headers,
        params=params
    )
    
    return response.json()

# 调用示例
result = list_dns_rules(page=1, per_page=50)
print(result)
```

**示例 2：创建 DNS 路由规则（A 记录类型）**

```python
import requests
import json

def create_dns_rule_a_record(domain, name, address_pool):
    """
    创建 A 记录类型的 DNS 路由规则
    
    Args:
        domain: 域名
        name: 规则名称
        address_pool: IP 地址池
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "name": name,
        "record_type": "a",
        "address_pool": address_pool,
        "response_strategy": "quality_optimized",
        "status": "enabled"
    }
    
    response = requests.post(
        f"{API_URL}/dns_routing_rules",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建包含多个 IP 的 DNS 路由规则
address_pool = [
    {
        "addresses": ["1.2.3.4", "5.6.7.8"],
        "geo_isp": "CN"
    }
]

result = create_dns_rule_a_record(
    domain="example.com",
    name="我的服务-A",
    address_pool=address_pool
)
print(result)
```

**示例 3：创建 DNS 路由规则（CNAME 记录类型）**

```python
def create_dns_rule_cname(domain, name, cname_pool):
    """
    创建 CNAME 类型的 DNS 路由规则
    
    Args:
        domain: 域名
        name: 规则名称
        cname_pool: CNAME 地址池
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "name": name,
        "record_type": "cname",
        "cname_address_pool": cname_pool,
        "response_strategy": "priority_order",
        "status": "enabled"
    }
    
    response = requests.post(
        f"{API_URL}/dns_routing_rules",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建 CNAME 类型的 DNS 路由规则
cname_pool = [
    {
        "addresses": ["origin.example.com"],
        "weight": 100
    }
]

result = create_dns_rule_cname(
    domain="example.com",
    name="CNAME 规则",
    cname_pool=cname_pool
)
print(result)
```

**示例 4：按条件筛选 DNS 路由规则**

```python
def filter_dns_rules(keyword=None, domain=None, status=None):
    """
    按条件筛选 DNS 路由规则
    
    Args:
        keyword: 关键词搜索（名称和描述）
        domain: 域名过滤
        status: 状态过滤 (enabled/disabled)
    
    Returns:
        筛选结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {}
    
    if keyword:
        payload["keyword"] = keyword
    if domain:
        payload["domain"] = {"contains": [domain]}
    if status:
        payload["status"] = {"equal": [status]}
    
    response = requests.post(
        f"{API_URL}/dns_routing_rules/filter",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 筛选启用状态的规则
result = filter_dns_rules(status="enabled")
print(result)
```

**示例 5：获取和更新 DNS 路由规则**

```python
def get_dns_rule(uuid):
    """
    获取单个 DNS 路由规则详情
    
    Args:
        uuid: 规则 UUID
    
    Returns:
        规则详情
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/dns_routing_rules/{uuid}",
        headers=headers
    )
    
    return response.json()

def update_dns_rule(uuid, updates):
    """
    更新 DNS 路由规则
    
    Args:
        uuid: 规则 UUID
        updates: 更新字段
    
    Returns:
        更新结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_URL}/dns_routing_rules/{uuid}",
        headers=headers,
        data=json.dumps(updates)
    )
    
    return response.json()

# 获取规则详情
rule_uuid = "d7b0d7a9-0e91-428f-a33d-1cf74218b341"
rule = get_dns_rule(rule_uuid)
print("规则详情:", rule)

# 更新规则名称
updates = {
    "name": "更新后的规则名称",
    "description": "这是更新后的描述"
}
updated_rule = update_dns_rule(rule_uuid, updates)
print("更新结果:", updated_rule)
```

**示例 6：删除 DNS 路由规则**

```python
def delete_dns_rule(uuid):
    """
    删除 DNS 路由规则
    
    Args:
        uuid: 规则 UUID
    
    Returns:
        删除结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"{API_URL}/dns_routing_rules/{uuid}",
        headers=headers
    )
    
    return response.json()

# 删除规则
result = delete_dns_rule("d7b0d7a9-0e91-428f-a33d-1cf74218b341")
print(result)
```

#### 4.1.4 响应策略类型

| 策略 | 描述 |
|------|------|
| `priority_order` | 按优先级顺序选择 |
| `quality_optimized` | 质量优化选择（基于延迟和稳定性） |

#### 4.1.5 DNS 记录类型

| 类型 | 描述 |
|------|------|
| `a` | A 记录（IPv4 地址） |
| `cname` | CNAME 记录（别名） |

---

### 4.2 DNS 路由域名 (DNS Routing Domains)

#### 4.2.1 模块概述

DNS 路由域名模块用于管理与第三方 DNS 提供商集成的域名配置。

#### 4.2.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/dns_routing_domains` | 列出所有 DNS 路由域名 |
| POST | `/dns_routing_domains` | 创建新的 DNS 路由域名 |
| GET | `/dns_routing_domains/{uuid}` | 获取单个 DNS 路由域名详情 |
| PUT | `/dns_routing_domains/{uuid}` | 更新 DNS 路由域名 |
| DELETE | `/dns_routing_domains/{uuid}` | 删除 DNS 路由域名 |
| POST | `/dns_routing_domains/filter` | 按条件筛选 DNS 路由域名 |
| POST | `/dns_routing_domains/test_integrations` | 测试集成配置 |
| POST | `/dns_routing_domains/3rd_records` | 获取第三方 DNS 记录 |

#### 4.2.3 调用示例

**示例 1：列出所有 DNS 路由域名**

```python
def list_dns_domains(page=1, per_page=20):
    """
    列出所有 DNS 路由域名
    
    Args:
        page: 页码
        per_page: 每页数量
    
    Returns:
        域名列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(
        f"{API_URL}/dns_routing_domains",
        headers=headers,
        params=params
    )
    
    return response.json()

# 调用示例
result = list_dns_domains()
print(result)
```

**示例 2：创建 Cloudflare DNS 路由域名**

```python
def create_cloudflare_domain(domain, api_token, zone_id):
    """
    创建 Cloudflare 域名集成
    
    Args:
        domain: 域名
        api_token: Cloudflare API Token
        zone_id: Cloudflare Zone ID
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "type": "zone",
        "source": "custom",
        "provider_type": "cloudflare",
        "zone_config": {
            "api_token": api_token,
            "zone_id": zone_id
        }
    }
    
    response = requests.post(
        f"{API_URL}/dns_routing_domains",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建 Cloudflare 域名集成
result = create_cloudflare_domain(
    domain="example.com",
    api_token="your-cloudflare-api-token",
    zone_id="your-zone-id"
)
print(result)
```

**示例 3：创建阿里云 DNS 路由域名**

```python
def create_alibaba_domain(domain, access_key_id, access_key_secret, zone_id):
    """
    创建阿里云域名集成
    
    Args:
        domain: 域名
        access_key_id: 阿里云 Access Key ID
        access_key_secret: 阿里云 Access Key Secret
        zone_id: 阿里云 Zone ID
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "type": "zone",
        "source": "custom",
        "provider_type": "alibaba-cloud",
        "zone_config": {
            "access_key_id": access_key_id,
            "access_key_secret": access_key_secret,
            "zone_id": zone_id
        }
    }
    
    response = requests.post(
        f"{API_URL}/dns_routing_domains",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()
```

**示例 4：创建 DNSPod 域名集成**

```python
def create_dnspod_domain(domain, secret_id, secret_key, zone_id, zone_plan):
    """
    创建 DNSPod 域名集成
    
    Args:
        domain: 域名
        secret_id: DNSPod Secret ID
        secret_key: DNSPod Secret Key
        zone_id: DNSPod Zone ID
        zone_plan: 套餐类型
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "domain": domain,
        "type": "zone",
        "source": "custom",
        "provider_type": "dnspod",
        "zone_config": {
            "secret_id": secret_id,
            "secret_key": secret_key,
            "zone_id": zone_id,
            "zone_plan": zone_plan
        }
    }
    
    response = requests.post(
        f"{API_URL}/dns_routing_domains",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()
```

**示例 5：测试域名集成配置**

```python
def test_domain_integration(provider_type, zone_config):
    """
    测试域名集成配置是否有效
    
    Args:
        provider_type: DNS 提供商类型
        zone_config: 区域配置
    
    Returns:
        测试结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "provider_type": provider_type,
        "zone_config": zone_config
    }
    
    response = requests.post(
        f"{API_URL}/dns_routing_domains/test_integrations",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 测试 Cloudflare 集成
cloudflare_config = {
    "api_token": "your-cloudflare-token",
    "zone_id": "your-zone-id"
}

result = test_domain_integration("cloudflare", cloudflare_config)
print("集成测试结果:", result)
```

**示例 6：获取第三方 DNS 记录**

```python
def get_third_party_records(domain_uuid, subdomain=None):
    """
    获取第三方 DNS 提供商的 DNS 记录
    
    Args:
        domain_uuid: 域名 UUID
        subdomain: 子域名过滤（可选）
    
    Returns:
        DNS 记录列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "dns_routing_domain_uuid": domain_uuid
    }
    
    if subdomain:
        payload["subdomain"] = subdomain
    
    response = requests.post(
        f"{API_URL}/dns_routing_domains/3rd_records",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 获取第三方 DNS 记录
result = get_third_party_records("domain-uuid")
print(result)
```

**示例 7：按条件筛选域名**

```python
def filter_dns_domains(keyword=None, status=None, provider_type=None):
    """
    按条件筛选 DNS 路由域名
    
    Args:
        keyword: 关键词搜索
        status: 状态过滤
        provider_type: 提供商类型过滤
    
    Returns:
        筛选结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {}
    
    if keyword:
        payload["keyword"] = keyword
    if status:
        payload["status"] = {"equal": [status]}
    if provider_type:
        payload["provider_type"] = {"equal": [provider_type]}
    
    response = requests.post(
        f"{API_URL}/dns_routing_domains/filter",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 筛选 Cloudflare 域名
result = filter_dns_domains(provider_type="cloudflare")
print(result)
```

#### 4.2.4 支持的 DNS 提供商

| 提供商 | 类型标识 | 必需参数 |
|--------|----------|----------|
| Cloudflare | `cloudflare` | `api_token`, `zone_id` |
| 阿里云 | `alibaba-cloud` | `access_key_id`, `access_key_secret`, `zone_id` |
| DNSPod | `dnspod` | `secret_id`, `secret_key`, `zone_id`, `zone_plan` |
| 华为云 | `huawei_cloud` | `domain_name`, `ak`, `sk`, `zone_id` |
| AWS Route 53 | `aws_route` | `access_key_id`, `secret_access_key`, `zone_id`, `hosted_zone_id` |
| ClouDNS | `cloudns` | `auth_id`, `auth_password`, `zone_name`, `zone_id` |
| 自建 DNS | `self-hosted` | `dns_ip`, `dns_port` |

#### 4.2.5 DNSPod 套餐类型

| 套餐 | 标识 |
|------|------|
| 国际版专业版 | `intl_professional` |
| 国际版企业版 | `intl_enterprise` |
| 国际版旗舰版 | `intl_ultimate` |
| 免费版 | `free` |
|  Plus 版 | `plus` |
| 专家/旗舰版 | `expert_ultra` |

---

### 4.3 DNS 提供商 (DNS Providers)

#### 4.3.1 模块概述

DNS 提供商模块用于管理和配置 DNS 服务提供商的集成。

#### 4.3.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/dns_providers` | 列出所有自定义 DNS 提供商 |
| POST | `/dns_providers` | 创建新的 DNS 提供商配置 |
| GET | `/dns_providers/{uuid}` | 获取单个 DNS 提供商详情 |
| PUT | `/dns_providers/{uuid}` | 更新 DNS 提供商配置 |
| DELETE | `/dns_providers/{uuid}` | 删除 DNS 提供商配置 |
| POST | `/dns_providers/filter` | 按条件筛选 DNS 提供商 |
| POST | `/dns_providers/test_integrations` | 测试提供商集成 |
| POST | `/system_dns_providers` | 列出系统 DNS 提供商 |

#### 4.3.3 调用示例

**示例 1：列出所有 DNS 提供商**

```python
def list_dns_providers(page=1, per_page=20):
    """
    列出所有 DNS 提供商配置
    
    Args:
        page: 页码
        per_page: 每页数量
    
    Returns:
        提供商列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(
        f"{API_URL}/dns_providers",
        headers=headers,
        params=params
    )
    
    return response.json()

# 调用示例
result = list_dns_providers()
print(result)
```

**示例 2：创建 DNS 提供商配置**

```python
def create_dns_provider(name, provider_type, zone_configs, description=""):
    """
    创建 DNS 提供商配置
    
    Args:
        name: 提供商名称
        provider_type: 提供商类型
        zone_configs: 区域配置列表
        description: 描述
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "description": description,
        "provider_type": provider_type,
        "zone_configs": zone_configs
    }
    
    response = requests.post(
        f"{API_URL}/dns_providers",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建 Cloudflare 提供商配置
cloudflare_zones = [
    {
        "zone_name": "example.com",
        "zone_id": "zone-id-1",
        "api_token": "your-api-token"
    }
]

result = create_dns_provider(
    name="我的 Cloudflare 账户",
    provider_type="cloudflare",
    zone_configs=cloudflare_zones,
    description="主 Cloudflare 账户"
)
print(result)
```

**示例 3：列出系统 DNS 提供商**

```python
def list_system_dns_providers(keyword=None, provider_type=None):
    """
    列出系统 DNS 提供商
    
    Args:
        keyword: 关键词搜索
        provider_type: 提供商类型过滤
    
    Returns:
        系统提供商列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {}
    
    if keyword:
        payload["keyword"] = keyword
    if provider_type:
        payload["provider_type"] = {"equal": [provider_type]}
    
    response = requests.post(
        f"{API_URL}/system_dns_providers",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 获取所有系统提供商
result = list_system_dns_providers()
print(result)
```

**示例 4：测试提供商集成**

```python
def test_provider_integration(provider_type, zone_config):
    """
    测试 DNS 提供商集成配置
    
    Args:
        provider_type: 提供商类型
        zone_config: 区域配置
    
    Returns:
        测试结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "provider_type": provider_type,
        "zone_config": zone_config
    }
    
    response = requests.post(
        f"{API_URL}/dns_providers/test_integrations",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()
```

**示例 5：获取和更新 DNS 提供商**

```python
def get_dns_provider(uuid):
    """
    获取 DNS 提供商详情
    
    Args:
        uuid: 提供商 UUID
    
    Returns:
        提供商详情
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/dns_providers/{uuid}",
        headers=headers
    )
    
    return response.json()

def update_dns_provider(uuid, updates):
    """
    更新 DNS 提供商配置
    
    Args:
        uuid: 提供商 UUID
        updates: 更新字段
    
    Returns:
        更新结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_URL}/dns_providers/{uuid}",
        headers=headers,
        data=json.dumps(updates)
    )
    
    return response.json()

# 获取提供商详情
provider_uuid = "provider-uuid"
provider = get_dns_provider(provider_uuid)
print("提供商详情:", provider)

# 更新提供商名称
updates = {
    "name": "更新后的提供商名称"
}
result = update_dns_provider(provider_uuid, updates)
print("更新结果:", result)
```

---

### 4.4 DNS 记录 (DNS Records)

#### 4.4.1 模块概述

DNS 记录模块用于查看和管理由 DNS 路由规则生成的 DNS 记录。

#### 4.4.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/dns_records` | 列出所有 DNS 记录 |
| GET | `/dns_records/{uuid}` | 获取单个 DNS 记录详情 |
| POST | `/dns_records/filter` | 按条件筛选 DNS 记录 |

#### 4.4.3 调用示例

**示例 1：列出所有 DNS 记录**

```python
def list_dns_records(page=1, per_page=20):
    """
    列出所有 DNS 记录
    
    Args:
        page: 页码
        per_page: 每页数量
    
    Returns:
        DNS 记录列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    response = requests.get(
        f"{API_URL}/dns_records",
        headers=headers,
        params=params
    )
    
    return response.json()

# 调用示例
result = list_dns_records()
print(result)
```

**示例 2：按条件筛选 DNS 记录**

```python
def filter_dns_records(rule_uuid=None, content=None, geo_isp=None):
    """
    按条件筛选 DNS 记录
    
    Args:
        rule_uuid: 规则 UUID 过滤
        content: 记录内容过滤
        geo_isp: 地理位置过滤
    
    Returns:
        筛选结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {}
    
    if rule_uuid:
        payload["dns_rule_uuid"] = {"in": [rule_uuid]}
    if content:
        payload["content"] = {"contains": [content]}
    if geo_isp:
        payload["geo_isp"] = {"equal": [geo_isp]}
    
    response = requests.post(
        f"{API_URL}/dns_records/filter",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 筛选特定规则的 DNS 记录
result = filter_dns_records(rule_uuid="rule-uuid")
print(result)
```

**示例 3：获取 DNS 记录详情**

```python
def get_dns_record(uuid):
    """
    获取单个 DNS 记录详情
    
    Args:
        uuid: 记录 UUID
    
    Returns:
        记录详情
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/dns_records/{uuid}",
        headers=headers
    )
    
    return response.json()

# 获取记录详情
result = get_dns_record("record-uuid")
print(result)
```

#### 4.4.4 DNS 记录字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `uuid` | string | 记录 UUID |
| `domain` | string | 域名 |
| `type` | string | 记录类型 (A/CNAME) |
| `content` | string | 记录内容 (IP 或 CNAME) |
| `ttl` | integer | TTL 值（秒） |
| `geo_isp` | string | 地理位置/ISP |
| `dns_rule_uuid` | string | 关联的 DNS 规则 UUID |
| `sync_status` | string | 同步状态 |
| `latency` | integer | 延迟（毫秒） |
| `fallback` | boolean | 是否为备用记录 |

---

### 4.5 集群 (Clusters)

#### 4.5.1 模块概述

集群模块用于管理边缘节点集群的创建、配置和生命周期管理。

#### 4.5.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/clusters` | 列出所有集群 |
| POST | `/clusters` | 创建新集群 |
| GET | `/clusters/{uuid}` | 获取单个集群详情 |
| PUT | `/clusters/{uuid}` | 更新集群配置 |
| DELETE | `/clusters/{uuid}` | 删除集群 |

#### 4.5.3 调用示例

**示例 1：列出所有集群**

```python
def list_clusters(name=None, page=1, per_page=20):
    """
    列出所有集群
    
    Args:
        name: 集群名称过滤（可选）
        page: 页码
        per_page: 每页数量
    
    Returns:
        集群列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if name:
        params["name"] = name
    
    response = requests.get(
        f"{API_URL}/clusters",
        headers=headers,
        params=params
    )
    
    return response.json()

# 列出所有集群
result = list_clusters()
print(result)

# 按名称搜索
result = list_clusters(name="生产环境")
print(result)
```

**示例 2：创建新集群**

```python
def create_cluster(name, description=""):
    """
    创建新集群
    
    Args:
        name: 集群名称
        description: 集群描述
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "description": description
    }
    
    response = requests.post(
        f"{API_URL}/clusters",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建生产环境集群
result = create_cluster(
    name="生产环境集群",
    description="生产环境边缘节点集群"
)
print(result)
```

**示例 3：获取和更新集群**

```python
def get_cluster(uuid):
    """
    获取集群详情
    
    Args:
        uuid: 集群 UUID
    
    Returns:
        集群详情
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/clusters/{uuid}",
        headers=headers
    )
    
    return response.json()

def update_cluster(uuid, updates):
    """
    更新集群配置
    
    Args:
        uuid: 集群 UUID
        updates: 更新字段
    
    Returns:
        更新结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_URL}/clusters/{uuid}",
        headers=headers,
        data=json.dumps(updates)
    )
    
    return response.json()

# 获取集群详情
cluster_uuid = "cluster-uuid"
cluster = get_cluster(cluster_uuid)
print("集群详情:", cluster)

# 更新集群描述
updates = {
    "description": "更新后的集群描述"
}
result = update_cluster(cluster_uuid, updates)
print("更新结果:", result)
```

**示例 4：删除集群**

```python
def delete_cluster(uuid):
    """
    删除集群
    
    Args:
        uuid: 集群 UUID
    
    Returns:
        删除结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"{API_URL}/clusters/{uuid}",
        headers=headers
    )
    
    return response.json()

# 删除集群
result = delete_cluster("cluster-uuid")
print(result)
```

---

### 4.6 边缘节点 (Edges)

#### 4.6.1 模块概述

边缘节点模块用于管理边缘节点的部署、配置、升级和监控。

#### 4.6.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/edges` | 列出所有边缘节点 |
| POST | `/edges` | 创建新的边缘节点 |
| GET | `/edges/{uuid}` | 获取单个边缘节点详情 |
| PUT | `/edges/{uuid}` | 更新边缘节点配置 |
| DELETE | `/edges/{uuid}` | 删除边缘节点 |
| GET | `/edges/deployment_configurations` | 获取部署配置 |
| POST | `/edges/deployment_configurations` | 创建部署配置 |
| GET | `/edges/{uuid}/upgrades` | 获取升级信息 |
| PATCH | `/edges/upgrades` | 批量升级边缘节点 |
| POST | `/edges/{uuid}/api_token` | 创建 API Token |
| PUT | `/edges/{uuid}/heartbeat` | 心跳和更新元数据 |

#### 4.6.3 调用示例

**示例 1：列出所有边缘节点**

```python
def list_edges(cluster_uuid=None, name=None, uuids=None, page=1, per_page=20):
    """
    列出所有边缘节点
    
    Args:
        cluster_uuid: 集群 UUID 过滤
        name: 节点名称过滤
        uuids: 多个 UUID 过滤（逗号分隔）
        page: 页码
        per_page: 每页数量
    
    Returns:
        边缘节点列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if cluster_uuid:
        params["cluster_uuid"] = cluster_uuid
    if name:
        params["name"] = name
    if uuids:
        params["uuids"] = uuids
    
    response = requests.get(
        f"{API_URL}/edges",
        headers=headers,
        params=params
    )
    
    return response.json()

# 列出所有边缘节点
result = list_edges()
print(result)

# 列出特定集群的节点
result = list_edges(cluster_uuid="cluster-uuid")
print(result)

# 按 UUID 批量查询
result = list_edges(uuids="uuid1,uuid2,uuid3")
print(result)
```

**示例 2：创建边缘节点**

```python
def create_edge(name, cluster_uuid, description=""):
    """
    创建新的边缘节点
    
    Args:
        name: 节点名称
        cluster_uuid: 所属集群 UUID
        description: 节点描述
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "cluster_uuid": cluster_uuid,
        "description": description
    }
    
    response = requests.post(
        f"{API_URL}/edges",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建边缘节点
result = create_edge(
    name="北京节点-01",
    cluster_uuid="cluster-uuid",
    description="北京地区边缘节点"
)
print(result)
```

**示例 3：创建部署配置（单节点）**

```python
def create_deployment_config_single(edge_uuid, deploy_type="single"):
    """
    创建单节点部署配置
    
    Args:
        edge_uuid: 边缘节点 UUID
        deploy_type: 部署类型
    
    Returns:
        部署配置
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "deploy_type": deploy_type,
        "single_deployment_configuration": {
            "edge_uuid": edge_uuid
        }
    }
    
    response = requests.post(
        f"{API_URL}/edges/deployment_configurations",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建单节点部署配置
result = create_deployment_config_single("edge-uuid")
print("部署配置:", result)
```

**示例 4：创建批量部署配置**

```python
def create_deployment_config_bulk(cluster_uuid, quantity=1):
    """
    创建批量部署配置
    
    Args:
        cluster_uuid: 集群 UUID
        quantity: 部署数量
    
    Returns:
        部署配置
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "deploy_type": "bulk",
        "bulk_deployment_configuration": {
            "cluster_uuid": cluster_uuid,
            "quantity": quantity
        }
    }
    
    response = requests.post(
        f"{API_URL}/edges/deployment_configurations",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建批量部署配置
result = create_deployment_config_bulk(
    cluster_uuid="cluster-uuid",
    quantity=5
)
print("批量部署配置:", result)
```

**示例 5：获取部署配置列表**

```python
def get_deployment_configs():
    """
    获取所有部署配置
    
    Returns:
        部署配置列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/edges/deployment_configurations",
        headers=headers
    )
    
    return response.json()

# 获取部署配置
result = get_deployment_configs()
print(result)
```

**示例 6：获取边缘节点升级信息**

```python
def get_edge_upgrade_info(edge_uuid):
    """
    获取边缘节点升级信息
    
    Args:
        edge_uuid: 边缘节点 UUID
    
    Returns:
        升级信息
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/edges/{edge_uuid}/upgrades",
        headers=headers
    )
    
    return response.json()

# 获取升级信息
result = get_edge_upgrade_info("edge-uuid")
print("升级信息:", result)
```

**示例 7：批量升级边缘节点**

```python
def upgrade_edges(edge_uuids, version=None):
    """
    批量升级边缘节点到最新版本
    
    Args:
        edge_uuids: 边缘节点 UUID 列表
        version: 指定版本（可选，默认为最新）
    
    Returns:
        升级结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "edge_uuids": edge_uuids
    }
    
    if version:
        payload["version"] = version
    
    response = requests.patch(
        f"{API_URL}/edges/upgrades",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 批量升级节点
result = upgrade_edges(
    edge_uuids=["uuid1", "uuid2", "uuid3"]
)
print("升级结果:", result)
```

**示例 8：发送心跳和更新元数据**

```python
def send_heartbeat(edge_uuid, metadata):
    """
    发送心跳并更新边缘节点元数据
    
    Args:
        edge_uuid: 边缘节点 UUID
        metadata: 元数据
    
    Returns:
        心跳结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_URL}/edges/{edge_uuid}/heartbeat",
        headers=headers,
        data=json.dumps(metadata)
    )
    
    return response.json()

# 发送心跳
metadata = {
    "status": "healthy",
    "cpu_usage": 25,
    "memory_usage": 60,
    "version": "1.0.0"
}

result = send_heartbeat("edge-uuid", metadata)
print("心跳结果:", result)
```

**示例 9：为边缘节点创建 API Token**

```python
def create_edge_api_token(edge_uuid, deploy_token):
    """
    使用部署 Token 创建边缘节点 API Token
    
    Args:
        edge_uuid: 边缘节点 UUID
        deploy_token: 部署 Token
    
    Returns:
        API Token
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "deploy_token": deploy_token
    }
    
    response = requests.post(
        f"{API_URL}/edges/{edge_uuid}/api_token",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建 API Token
result = create_edge_api_token(
    edge_uuid="edge-uuid",
    deploy_token="your-deploy-token"
)
print("API Token:", result)
```

---

### 4.7 计费 (Billing)

#### 4.7.1 模块概述

计费模块用于管理订阅计划、发票、支付方式等计费相关功能。

#### 4.7.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/billing/plans` | 列出可订阅的计划 |
| POST | `/billing/sessions` | 创建客户会话（订阅/支付方式更新） |
| GET | `/billing/subscriptions` | 列出订阅 |
| PUT | `/billing/subscriptions/{uuid}` | 更新订阅信息 |
| GET | `/billing/invoices` | 列出发票 |
| POST | `/billing/webhooks` | Stripe Webhook 回调 |

#### 4.7.3 调用示例

**示例 1：获取可订阅的计划列表**

```python
def list_subscription_plans():
    """
    获取所有可订阅的计划
    
    Returns:
        计划列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/billing/plans",
        headers=headers
    )
    
    return response.json()

# 获取计划列表
plans = list_subscription_plans()
print("可订阅计划:", plans)
```

**示例 2：创建结账会话（新订阅）**

```python
def create_checkout_session(success_url, cancel_url, plan_uuid, quantity=1):
    """
    创建结账会话（用于新订阅）
    
    Args:
        success_url: 支付成功后跳转 URL
        cancel_url: 取消支付后跳转 URL
        plan_uuid: 计划 UUID
        quantity: 订阅数量
    
    Returns:
        结账会话
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "type": "checkout",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "subscription_info": {
            "plan_uuid": plan_uuid,
            "quantity": quantity
        }
    }
    
    response = requests.post(
        f"{API_URL}/billing/sessions",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建结账会话
result = create_checkout_session(
    success_url="https://your-app.com/success",
    cancel_url="https://your-app.com/cancel",
    plan_uuid="plan-uuid",
    quantity=1
)
print("结账会话:", result)
# result 中会包含 checkout_url，用户需要访问该 URL 完成支付
```

**示例 3：创建门户会话（更新支付方式）**

```python
def create_portal_session(return_url):
    """
    创建客户门户会话（用于更新支付方式）
    
    Args:
        return_url: 返回 URL
    
    Returns:
        门户会话
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "type": "portal",
        "return_url": return_url
    }
    
    response = requests.post(
        f"{API_URL}/billing/sessions",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建门户会话
result = create_portal_session(
    return_url="https://your-app.com/settings"
)
print("门户会话:", result)
```

**示例 4：列出订阅**

```python
def list_subscriptions(status=None):
    """
    列出订阅
    
    Args:
        status: 订阅状态过滤
    
    Returns:
        订阅列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {}
    if status:
        params["status"] = status
    
    response = requests.get(
        f"{API_URL}/billing/subscriptions",
        headers=headers,
        params=params
    )
    
    return response.json()

# 列出所有订阅
result = list_subscriptions()
print("订阅列表:", result)

# 只列出活跃订阅
result = list_subscriptions(status="active")
print("活跃订阅:", result)
```

**示例 5：更新订阅（升级/降级/改数量）**

```python
def update_subscription(uuid, action, plan_uuid=None, quantity=None):
    """
    更新订阅
    
    Args:
        uuid: 订阅 UUID
        action: 操作类型 (upgrade/downgrade/change_quantity/cancel/revoke_cancel/revoke_downgrade/revoke_decrease)
        plan_uuid: 新计划 UUID（升级/降级时需要）
        quantity: 新数量（改数量时需要）
    
    Returns:
        更新结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "action": action
    }
    
    if plan_uuid:
        payload["plan_uuid"] = plan_uuid
    if quantity:
        payload["quantity"] = quantity
    
    response = requests.put(
        f"{API_URL}/billing/subscriptions/{uuid}",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 升级订阅
result = update_subscription(
    uuid="subscription-uuid",
    action="upgrade",
    plan_uuid="new-plan-uuid"
)
print("升级结果:", result)

# 更改订阅数量
result = update_subscription(
    uuid="subscription-uuid",
    action="change_quantity",
    quantity=5
)
print("改数量结果:", result)

# 取消订阅
result = update_subscription(
    uuid="subscription-uuid",
    action="cancel"
)
print("取消结果:", result)
```

**示例 6：列出发票**

```python
def list_invoices(status=None, subscription_id=None, limit=10, page=None):
    """
    列出发票
    
    Args:
        status: 发票状态 (draft/open/paid/uncollectible/void)
        subscription_id: Stripe 订阅 ID
        limit: 返回数量限制 (1-100)
        page: 分页游标
    
    Returns:
        发票列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "limit": limit
    }
    
    if status:
        params["status"] = status
    if subscription_id:
        params["subscription"] = subscription_id
    if page:
        params["page"] = page
    
    response = requests.get(
        f"{API_URL}/billing/invoices",
        headers=headers,
        params=params
    )
    
    return response.json()

# 列出已支付的发票
result = list_invoices(status="paid", limit=50)
print("已支付发票:", result)

# 按时间范围筛选
result = list_invoices(
    created_gte="1700000000",
    created_lte="1710000000"
)
print("时间范围内发票:", result)
```

#### 4.7.4 订阅状态

| 状态 | 描述 |
|------|------|
| `incomplete` | 未完成 |
| `incomplete_expired` | 已过期未完成 |
| `trialing` | 试用中 |
| `past_due` | 逾期 |
| `canceled` | 已取消 |
| `unpaid` | 未支付 |
| `paused` | 已暂停 |
| `complete` | 已完成 |
| `active` | 活跃 |

#### 4.7.5 发票状态

| 状态 | 描述 |
|------|------|
| `draft` | 草稿 |
| `open` | 待支付 |
| `paid` | 已支付 |
| `uncollectible` | 无法收回 |
| `void` | 已作废 |

---

### 4.8 工作负载标识 (Workload Identity)

#### 4.8.1 模块概述

工作负载标识模块用于管理客户端工作负载的身份识别配置。

#### 4.8.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/workload_identity` | 列出工作负载标识 |
| POST | `/workload_identity` | 创建工作负载标识 |
| GET | `/workload_identity/{uuid}` | 获取单个工作负载标识 |
| PUT | `/workload_identity/{uuid}` | 更新工作负载标识 |
| DELETE | `/workload_identity/{uuid}` | 删除工作负载标识 |

#### 4.8.3 调用示例

**示例 1：列出工作负载标识**

```python
def list_workload_identities(keyword=None, page=1, per_page=20):
    """
    列出工作负载标识
    
    Args:
        keyword: 关键词搜索
        page: 页码
        per_page: 每页数量
    
    Returns:
        工作负载标识列表
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if keyword:
        params["keyword"] = keyword
    
    response = requests.get(
        f"{API_URL}/workload_identity",
        headers=headers,
        params=params
    )
    
    return response.json()

# 列出所有工作负载标识
result = list_workload_identities()
print(result)

# 搜索包含 "sdk" 的标识
result = list_workload_identities(keyword="sdk integrated")
print(result)
```

**示例 2：创建工作负载标识**

```python
def create_workload_identity(name, config, description=""):
    """
    创建工作负载标识
    
    Args:
        name: 名称
        config: 配置
        description: 描述
    
    Returns:
        创建结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "description": description,
        "client_workload_conf": config
    }
    
    response = requests.post(
        f"{API_URL}/workload_identity",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()

# 创建工作负载标识
config = {
    "type": "api_key",
    "settings": {
        "rotation_days": 90
    }
}

result = create_workload_identity(
    name="移动端 SDK 集成",
    config=config,
    description="移动端应用的工作负载标识"
)
print(result)
```

**示例 3：获取、更新和删除工作负载标识**

```python
def get_workload_identity(uuid):
    """
    获取工作负载标识详情
    
    Args:
        uuid: 标识 UUID
    
    Returns:
        标识详情
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_URL}/workload_identity/{uuid}",
        headers=headers
    )
    
    return response.json()

def update_workload_identity(uuid, updates):
    """
    更新工作负载标识
    
    Args:
        uuid: 标识 UUID
        updates: 更新字段
    
    Returns:
        更新结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        f"{API_URL}/workload_identity/{uuid}",
        headers=headers,
        data=json.dumps(updates)
    )
    
    return response.json()

def delete_workload_identity(uuid):
    """
    删除工作负载标识
    
    Args:
        uuid: 标识 UUID
    
    Returns:
        删除结果
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"{API_URL}/workload_identity/{uuid}",
        headers=headers
    )
    
    return response.json()

# 获取详情
uuid = "workload-uuid"
identity = get_workload_identity(uuid)
print("标识详情:", identity)

# 更新
updates = {"description": "更新后的描述"}
result = update_workload_identity(uuid, updates)
print("更新结果:", result)

# 删除
result = delete_workload_identity(uuid)
print("删除结果:", result)
```

---

### 4.9 包管理 (Packages)

#### 4.9.1 模块概述

包管理模块用于查询和下载 AxisNow 相关的软件包。

#### 4.9.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/packages/{package_identifier}` | 获取包信息 |
| GET | `/packages/{package_identifier}/versions` | 获取包版本列表 |

#### 4.9.3 调用示例

**示例 1：获取包信息**

```python
def get_package_info(package_identifier, version="latest", arch=None, pkg_type=None):
    """
    获取包信息
    
    Args:
        package_identifier: 包标识 (edge/headless-client/edge-headless-client/agentsdk)
        version: 版本号或 "latest"
        arch: 架构 (x86_64/aarch64)
        pkg_type: 包类型 (deb/rpm)
    
    Returns:
        包信息
    """
    params = {
        "version": version
    }
    
    if arch:
        params["arch"] = arch
    if pkg_type:
        params["type"] = pkg_type
    
    response = requests.get(
        f"{API_URL}/packages/{package_identifier}",
        params=params
    )
    
    return response.json()

# 获取 Edge 包最新版本
result = get_package_info("edge", version="latest")
print("Edge 包信息:", result)

# 获取特定版本和架构的 Edge 包
result = get_package_info(
    package_identifier="edge",
    version="1.0.0",
    arch="x86_64",
    pkg_type="deb"
)
print("特定版本包信息:", result)

# 获取 AgentSDK 包
result = get_package_info("agentsdk", version="latest")
print("AgentSDK 包信息:", result)
```

**示例 2：获取包版本列表**

```python
def get_package_versions(package_identifier):
    """
    获取包的所有可用版本
    
    Args:
        package_identifier: 包标识
    
    Returns:
        版本列表
    """
    response = requests.get(
        f"{API_URL}/packages/{package_identifier}/versions"
    )
    
    return response.json()

# 获取 Edge 包的所有版本
result = get_package_versions("edge")
print("Edge 版本列表:", result)
```

#### 4.9.4 包标识符

| 标识符 | 描述 |
|--------|------|
| `edge` | Edge 节点包 |
| `headless-client` | 无头客户端包 |
| `edge-headless-client` | Edge 无头客户端包 |
| `agentsdk` | Agent SDK 包 |

#### 4.9.5 架构类型

| 架构 | 描述 |
|------|------|
| `x86_64` | x86_64 (AMD64) 架构 |
| `aarch64` | ARM64 架构 |

#### 4.9.6 包类型

| 类型 | 描述 |
|------|------|
| `deb` | Debian/Ubuntu 包格式 |
| `rpm` | RHEL/CentOS 包格式 |

---

### 4.10 环境 (Environments)

#### 4.10.1 模块概述

环境模块用于获取当前环境的信息。

#### 4.10.2 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/environments/current` | 获取当前环境信息 |

#### 4.10.3 调用示例

**示例 1：获取当前环境信息**

```python
def get_current_environment():
    """
    获取当前环境信息（无需认证）
    
    Returns:
        环境信息
    """
    response = requests.get(
        f"{API_URL}/environments/current"
    )
    
    return response.json()

# 获取环境信息
result = get_current_environment()
print("环境信息:", result)
```

---

## 5. 完整模块列表

AxisNow Client API 包含以下完整的模块：

### 5.1 核心业务模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| DNS 路由规则 | DNS Routing Rules | 智能 DNS 路由规则管理 |
| DNS 路由域名 | DNS Routing Domains | DNS 域名集成管理 |
| DNS 提供商 | DNS Providers | DNS 服务提供商配置 |
| DNS 记录 | DNS Records | DNS 记录查看和管理 |
| 集群 | Clusters | 边缘节点集群管理 |
| 边缘节点 | Edges | 边缘节点生命周期管理 |
| 边缘节点部署 | Edges Deployment | 边缘节点部署配置 |
| 边缘节点元数据 | Edges Metadata | 边缘节点心跳和元数据 |
| 边缘探测任务 | Edge Probe Tasks | 边缘节点探测任务 |
| 边缘探测模板 | Edge Probe Templates | 探测模板管理 |

### 5.2 安全和认证模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| API Token | API Tokens | API 访问令牌管理 |
| 认证方法 | Authentication Methods | 认证方式配置 |
| 角色 | Roles | 角色权限管理 |
| 租户用户 | Tenant Users | 租户用户管理 |
| 租户实体 | Tenant Entities | 租户实体管理 |
| 信任提供商 | Trust Providers | 信任关系管理 |
| 凭证提供商 | Credential Providers | 凭证管理 |

### 5.3 网络和流量模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| 负载均衡对象 | Load Balancing Objects | 负载均衡配置 |
| 策略插件 | Policy Plugins | 流量策略插件 |
| 策略插件规则 | Policy Plugins Rules | 插件规则管理 |
| 策略对象 | Policy Objects | 策略对象管理 |
| 策略元数据 | Policy Metadatas | 策略元数据 |
| 条件 | Conditions | 条件表达式管理 |
| 条件组 | Condition Groups | 条件分组管理 |
| EIPs | EIPs | 弹性 IP 管理 |

### 5.4 缓存和加速模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| 缓存 Key | Cache Key | 缓存键配置 |
| 缓存清除 | Cache Purge | 缓存清除操作 |
| 缓存预热 | Cache Warming | 缓存预热 |
| 证书 | Certificates | SSL/TLS 证书管理 |
| TLS 解密 | TLS Decrypt | TLS 流量解密 |

### 5.5 可观测性模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| 事件 | Events | 事件日志 |
| 日志浏览器 | Log Explorer | 日志查询 |
| 日志格式 | Log Format | 日志格式配置 |
| 日志接收器 | Log Receiver | 日志接收配置 |
| 审计日志 | Audit Log | 审计日志 |
| 见解 | Insights | 数据分析见解 |
| 告警回调 | Alert Callback | 告警通知配置 |
| 通知通道 | Notification Channel | 通知渠道管理 |
| 错误码 | ErrorCode | 错误码定义 |

### 5.6 应用和部署模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| 部署 | Deployments | 部署管理 |
| 设备 | Devices | 设备管理 |
| 配置文件 | Profiles | 配置文件管理 |
| 别名对象 | Alias Objects | 别名管理 |
| 资源 | Resource | 资源管理 |
| 标签 | Tags | 标签管理 |
| 实体版本 | Entity Version | 实体版本控制 |

### 5.7 集成和 AI 模块

| 模块名称 | 英文标识 | 描述 |
|----------|----------|------|
| AI 助手 | AI Assistant | AI 智能助手 |
| OIDC 模块 | OIDC Module | OpenID Connect 集成 |
| 验证码提供商 | Captcha Providers | 验证码服务集成 |
| 分发商实体 | Distributor Entities | 分发商管理 |

---

## 6. 错误处理

### 6.1 HTTP 状态码

| 状态码 | 描述 |
|--------|------|
| `200` | 请求成功 |
| `201` | 资源创建成功 |
| `4XX` | 客户端错误 |
| `5XX` | 服务器错误 |

### 6.2 错误响应格式

```json
{
  "success": false,
  "messages": [
    {
      "code": "VALIDATION_ERROR",
      "message": "请求参数验证失败"
    }
  ],
  "errors": []
}
```

### 6.3 常见错误处理

```python
import requests

def handle_api_response(response):
    """
    处理 API 响应
    
    Args:
        response: requests Response 对象
    
    Returns:
        解析后的响应数据
    
    Raises:
        Exception: API 调用失败时抛出
    """
    try:
        data = response.json()
    except ValueError:
        raise Exception(f"无效的 JSON 响应: {response.text}")
    
    if response.status_code >= 400:
        messages = data.get("messages", [])
        error_msg = " ; ".join([m.get("message", str(m)) for m in messages])
        raise Exception(f"API 错误 ({response.status_code}): {error_msg}")
    
    if not data.get("success", True):
        messages = data.get("messages", [])
        error_msg = " ; ".join([m.get("message", str(m)) for m in messages])
        raise Exception(f"操作失败: {error_msg}")
    
    return data

# 使用示例
try:
    response = requests.get(f"{API_URL}/dns_routing_rules", headers=headers)
    data = handle_api_response(response)
    print("成功:", data)
except Exception as e:
    print(f"错误: {e}")
```

### 6.4 重试策略

```python
import time
import requests

def api_call_with_retry(method, url, max_retries=3, **kwargs):
    """
    带重试机制的 API 调用
    
    Args:
        method: HTTP 方法
        url: 请求 URL
        max_retries: 最大重试次数
        **kwargs: 其他请求参数
    
    Returns:
        请求响应
    """
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, **kwargs)
            if response.status_code < 500:
                return response
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    
    return response

# 使用示例
response = api_call_with_retry(
    "GET",
    f"{API_URL}/dns_routing_rules",
    headers=headers,
    max_retries=3
)
```

---

## 7. curl 命令示例 (Windows CMD/PowerShell)

本章节提供使用 curl 命令直接测试 API 的示例。您可以在 Windows CMD、PowerShell 或 Git Bash 中直接运行这些命令。

### 7.1 基础配置

首先设置环境变量（避免每次都写完整的 Token）：

**Windows CMD:**
```cmd
set API_URL=https://api.axisnow.io/client/v1
set API_TOKEN=your-api-token-here
```

**PowerShell:**
```powershell
$API_URL = "https://api.axisnow.io/client/v1"
$API_TOKEN = "your-api-token-here"
```

**Git Bash / WSL:**
```bash
export API_URL="https://api.axisnow.io/client/v1"
export API_TOKEN="your-api-token-here"
```

### 7.2 无需认证的 API

#### 7.2.1 获取当前环境信息

**CMD:**
```cmd
curl -X GET "%API_URL%/environments/current"
```

**PowerShell:**
```powershell
curl.exe -X GET "$API_URL/environments/current"
```

**Git Bash:**
```bash
curl -X GET "$API_URL/environments/current"
```

#### 7.2.2 获取包信息

**获取 Edge 最新版本:**
```cmd
curl -X GET "%API_URL%/packages/edge?version=latest"
```

**获取指定版本和架构:**
```cmd
curl -X GET "%API_URL%/packages/edge?version=1.0.0&arch=x86_64&type=deb"
```

**获取包版本列表:**
```cmd
curl -X GET "%API_URL%/packages/edge/versions"
```

### 7.3 DNS 路由规则

#### 7.3.1 列出所有 DNS 路由规则

**CMD:**
```cmd
curl -X GET "%API_URL%/dns_routing_rules?page=1&per_page=20" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

**PowerShell:**
```powershell
curl.exe -X GET "$API_URL/dns_routing_rules?page=1&per_page=20" `
  -H "Authorization: Bearer $API_TOKEN" `
  -H "Content-Type: application/json"
```

#### 7.3.2 创建 DNS 路由规则 (A 记录)

**CMD:**
```cmd
curl -X POST "%API_URL%/dns_routing_rules" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"domain\":\"example.com\",\"name\":\"我的服务-A\",\"record_type\":\"a\",\"address_pool\":[{\"addresses\":[\"1.2.3.4\",\"5.6.7.8\"],\"geo_isp\":\"CN\"}],\"response_strategy\":\"quality_optimized\",\"status\":\"enabled\"}"
```

**PowerShell:**
```powershell
$body = '{"domain":"example.com","name":"我的服务-A","record_type":"a","address_pool":[{"addresses":["1.2.3.4","5.6.7.8"],"geo_isp":"CN"}],"response_strategy":"quality_optimized","status":"enabled"}'

curl.exe -X POST "$API_URL/dns_routing_rules" `
  -H "Authorization: Bearer $API_TOKEN" `
  -H "Content-Type: application/json" `
  -d $body
```

**使用文件保存 JSON (推荐):**

创建文件 `create_rule.json`:
```json
{
  "domain": "example.com",
  "name": "我的服务-A",
  "record_type": "a",
  "address_pool": [
    {
      "addresses": ["1.2.3.4", "5.6.7.8"],
      "geo_isp": "CN"
    }
  ],
  "response_strategy": "quality_optimized",
  "status": "enabled"
}
```

然后执行:
```cmd
curl -X POST "%API_URL%/dns_routing_rules" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_rule.json"
```

#### 7.3.3 创建 DNS 路由规则 (CNAME 记录)

创建文件 `create_cname.json`:
```json
{
  "domain": "example.com",
  "name": "CNAME 规则",
  "record_type": "cname",
  "cname_address_pool": [
    {
      "addresses": ["origin.example.com"],
      "weight": 100
    }
  ],
  "response_strategy": "priority_order",
  "status": "enabled"
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_routing_rules" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_cname.json"
```

#### 7.3.4 获取单个 DNS 路由规则

```cmd
curl -X GET "%API_URL%/dns_routing_rules/d7b0d7a9-0e91-428f-a33d-1cf74218b341" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.3.5 更新 DNS 路由规则

创建文件 `update_rule.json`:
```json
{
  "name": "更新后的规则名称",
  "description": "这是更新后的描述"
}
```

执行:
```cmd
curl -X PUT "%API_URL%/dns_routing_rules/d7b0d7a9-0e91-428f-a33d-1cf74218b341" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@update_rule.json"
```

#### 7.3.6 删除 DNS 路由规则

```cmd
curl -X DELETE "%API_URL%/dns_routing_rules/d7b0d7a9-0e91-428f-a33d-1cf74218b341" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.3.7 按条件筛选 DNS 路由规则

创建文件 `filter_rules.json`:
```json
{
  "status": {
    "equal": ["enabled"]
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_routing_rules/filter" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@filter_rules.json"
```

### 7.4 DNS 路由域名

#### 7.4.1 列出所有 DNS 路由域名

```cmd
curl -X GET "%API_URL%/dns_routing_domains?page=1&per_page=20" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.4.2 创建 Cloudflare 域名集成

创建文件 `create_cloudflare.json`:
```json
{
  "domain": "example.com",
  "type": "zone",
  "source": "custom",
  "provider_type": "cloudflare",
  "zone_config": {
    "api_token": "your-cloudflare-api-token",
    "zone_id": "your-zone-id"
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_routing_domains" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_cloudflare.json"
```

#### 7.4.3 创建阿里云域名集成

创建文件 `create_alibaba.json`:
```json
{
  "domain": "example.com",
  "type": "zone",
  "source": "custom",
  "provider_type": "alibaba-cloud",
  "zone_config": {
    "access_key_id": "your-access-key-id",
    "access_key_secret": "your-access-key-secret",
    "zone_id": "your-zone-id"
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_routing_domains" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_alibaba.json"
```

#### 7.4.4 测试域名集成配置

创建文件 `test_integration.json`:
```json
{
  "provider_type": "cloudflare",
  "zone_config": {
    "api_token": "your-cloudflare-token",
    "zone_id": "your-zone-id"
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_routing_domains/test_integrations" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@test_integration.json"
```

#### 7.4.5 获取第三方 DNS 记录

创建文件 `get_3rd_records.json`:
```json
{
  "dns_routing_domain_uuid": "domain-uuid"
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_routing_domains/3rd_records" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@get_3rd_records.json"
```

### 7.5 DNS 提供商

#### 7.5.1 列出所有 DNS 提供商

```cmd
curl -X GET "%API_URL%/dns_providers?page=1&per_page=20" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.5.2 列出系统 DNS 提供商

创建文件 `list_system_providers.json`:
```json
{}
```

执行:
```cmd
curl -X POST "%API_URL%/system_dns_providers" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@list_system_providers.json"
```

#### 7.5.3 创建 DNS 提供商配置

创建文件 `create_provider.json`:
```json
{
  "name": "我的 Cloudflare 账户",
  "description": "主 Cloudflare 账户",
  "provider_type": "cloudflare",
  "zone_configs": [
    {
      "zone_name": "example.com",
      "zone_id": "zone-id-1",
      "api_token": "your-api-token"
    }
  ]
}
```

执行:
```cmd
curl -X POST "%API_URL%/dns_providers" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_provider.json"
```

### 7.6 集群管理

#### 7.6.1 列出所有集群

```cmd
curl -X GET "%API_URL%/clusters?page=1&per_page=20" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.6.2 按名称搜索集群

```cmd
curl -X GET "%API_URL%/clusters?name=生产环境" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.6.3 创建新集群

创建文件 `create_cluster.json`:
```json
{
  "name": "生产环境集群",
  "description": "生产环境边缘节点集群"
}
```

执行:
```cmd
curl -X POST "%API_URL%/clusters" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_cluster.json"
```

#### 7.6.4 获取集群详情

```cmd
curl -X GET "%API_URL%/clusters/f7b0d7a9-0e91-428f-a33d-1cf74218b342" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.6.5 更新集群

创建文件 `update_cluster.json`:
```json
{
  "description": "更新后的集群描述"
}
```

执行:
```cmd
curl -X PUT "%API_URL%/clusters/f7b0d7a9-0e91-428f-a33d-1cf74218b342" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@update_cluster.json"
```

#### 7.6.6 删除集群

```cmd
curl -X DELETE "%API_URL%/clusters/f7b0d7a9-0e91-428f-a33d-1cf74218b342" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

### 7.7 边缘节点管理

#### 7.7.1 列出所有边缘节点

```cmd
curl -X GET "%API_URL%/edges?page=1&per_page=20" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.7.2 列出特定集群的节点

```cmd
curl -X GET "%API_URL%/edges?cluster_uuid=cluster-uuid" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.7.3 按 UUID 批量查询

```cmd
curl -X GET "%API_URL%/edges?uuids=uuid1,uuid2,uuid3" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.7.4 创建边缘节点

创建文件 `create_edge.json`:
```json
{
  "name": "北京节点-01",
  "cluster_uuid": "cluster-uuid",
  "description": "北京地区边缘节点"
}
```

执行:
```cmd
curl -X POST "%API_URL%/edges" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_edge.json"
```

#### 7.7.5 获取部署配置

```cmd
curl -X GET "%API_URL%/edges/deployment_configurations" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.7.6 创建单节点部署配置

创建文件 `deploy_single.json`:
```json
{
  "deploy_type": "single",
  "single_deployment_configuration": {
    "edge_uuid": "edge-uuid"
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/edges/deployment_configurations" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@deploy_single.json"
```

#### 7.7.7 创建批量部署配置

创建文件 `deploy_bulk.json`:
```json
{
  "deploy_type": "bulk",
  "bulk_deployment_configuration": {
    "cluster_uuid": "cluster-uuid",
    "quantity": 5
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/edges/deployment_configurations" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@deploy_bulk.json"
```

#### 7.7.8 获取边缘节点升级信息

```cmd
curl -X GET "%API_URL%/edges/edge-uuid/upgrades" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.7.9 批量升级边缘节点

创建文件 `upgrade_edges.json`:
```json
{
  "edge_uuids": ["uuid1", "uuid2", "uuid3"]
}
```

执行:
```cmd
curl -X PATCH "%API_URL%/edges/upgrades" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@upgrade_edges.json"
```

#### 7.7.10 发送心跳

创建文件 `heartbeat.json`:
```json
{
  "status": "healthy",
  "cpu_usage": 25,
  "memory_usage": 60,
  "version": "1.0.0"
}
```

执行:
```cmd
curl -X PUT "%API_URL%/edges/edge-uuid/heartbeat" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@heartbeat.json"
```

### 7.8 计费管理

#### 7.8.1 获取可订阅的计划

```cmd
curl -X GET "%API_URL%/billing/plans" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.8.2 列出订阅

```cmd
curl -X GET "%API_URL%/billing/subscriptions" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.8.3 只列出活跃订阅

```cmd
curl -X GET "%API_URL%/billing/subscriptions?status=active" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.8.4 创建结账会话（新订阅）

创建文件 `checkout_session.json`:
```json
{
  "type": "checkout",
  "success_url": "https://your-app.com/success",
  "cancel_url": "https://your-app.com/cancel",
  "subscription_info": {
    "plan_uuid": "plan-uuid",
    "quantity": 1
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/billing/sessions" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@checkout_session.json"
```

#### 7.8.5 创建门户会话（更新支付方式）

创建文件 `portal_session.json`:
```json
{
  "type": "portal",
  "return_url": "https://your-app.com/settings"
}
```

执行:
```cmd
curl -X POST "%API_URL%/billing/sessions" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@portal_session.json"
```

#### 7.8.6 升级订阅

创建文件 `upgrade_subscription.json`:
```json
{
  "action": "upgrade",
  "plan_uuid": "new-plan-uuid"
}
```

执行:
```cmd
curl -X PUT "%API_URL%/billing/subscriptions/subscription-uuid" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@upgrade_subscription.json"
```

#### 7.8.7 更改订阅数量

创建文件 `change_quantity.json`:
```json
{
  "action": "change_quantity",
  "quantity": 5
}
```

执行:
```cmd
curl -X PUT "%API_URL%/billing/subscriptions/subscription-uuid" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@change_quantity.json"
```

#### 7.8.8 取消订阅

创建文件 `cancel_subscription.json`:
```json
{
  "action": "cancel"
}
```

执行:
```cmd
curl -X PUT "%API_URL%/billing/subscriptions/subscription-uuid" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@cancel_subscription.json"
```

#### 7.8.9 列出已支付的发票

```cmd
curl -X GET "%API_URL%/billing/invoices?status=paid&limit=50" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

### 7.9 工作负载标识

#### 7.9.1 列出工作负载标识

```cmd
curl -X GET "%API_URL%/workload_identity?page=1&per_page=20" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.9.2 搜索工作负载标识

```cmd
curl -X GET "%API_URL%/workload_identity?keyword=sdk%20integrated" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

#### 7.9.3 创建工作负载标识

创建文件 `create_workload.json`:
```json
{
  "name": "移动端 SDK 集成",
  "description": "移动端应用的工作负载标识",
  "client_workload_conf": {
    "type": "api_key",
    "settings": {
      "rotation_days": 90
    }
  }
}
```

执行:
```cmd
curl -X POST "%API_URL%/workload_identity" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json" ^
  --data-binary "@create_workload.json"
```

#### 7.9.4 删除工作负载标识

```cmd
curl -X DELETE "%API_URL%/workload_identity/workload-uuid" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
```

### 7.10 Windows CMD 批处理脚本示例

创建文件 `api_test.bat`:

```batch
@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM AxisNow API 测试脚本 (Windows CMD)
REM ============================================================

set API_URL=https://api.axisnow.io/client/v1
set API_TOKEN=your-api-token-here

echo.
echo ========================================
echo AxisNow API 测试脚本
echo ========================================
echo.

REM 1. 测试环境信息（无需认证）
echo [1/5] 测试环境信息...
curl -s -X GET "%API_URL%/environments/current"
echo.
echo.

REM 2. 获取 Edge 包信息
echo [2/5] 获取 Edge 包最新版本...
curl -s -X GET "%API_URL%/packages/edge?version=latest"
echo.
echo.

REM 3. 列出 DNS 路由规则
echo [3/5] 列出 DNS 路由规则...
curl -s -X GET "%API_URL%/dns_routing_rules?page=1&per_page=5" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

REM 4. 列出集群
echo [4/5] 列出集群...
curl -s -X GET "%API_URL%/clusters?page=1&per_page=10" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

REM 5. 列出边缘节点
echo [5/5] 列出边缘节点...
curl -s -X GET "%API_URL%/edges?page=1&per_page=10" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -H "Content-Type: application/json"
echo.
echo.

echo ========================================
echo 测试完成
echo ========================================
echo.

pause
```

运行方法:
```cmd
api_test.bat
```

### 7.11 PowerShell 脚本示例

创建文件 `api_test.ps1`:

```powershell
# ============================================================
# AxisNow API 测试脚本 (PowerShell)
# ============================================================

$API_URL = "https://api.axisnow.io/client/v1"
$API_TOKEN = "your-api-token-here"

$headers = @{
    "Authorization" = "Bearer $API_TOKEN"
    "Content-Type" = "application/json"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AxisNow API 测试脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 测试环境信息（无需认证）
Write-Host "[1/5] 测试环境信息..." -ForegroundColor Yellow
$envResponse = Invoke-RestMethod -Uri "$API_URL/environments/current" -Method Get
$envResponse | ConvertTo-Json -Depth 10
Write-Host ""

# 2. 获取 Edge 包信息
Write-Host "[2/5] 获取 Edge 包最新版本..." -ForegroundColor Yellow
$packageResponse = Invoke-RestMethod -Uri "$API_URL/packages/edge?version=latest" -Method Get
$packageResponse | ConvertTo-Json -Depth 10
Write-Host ""

# 3. 列出 DNS 路由规则
Write-Host "[3/5] 列出 DNS 路由规则..." -ForegroundColor Yellow
$dnsResponse = Invoke-RestMethod -Uri "$API_URL/dns_routing_rules?page=1&per_page=5" -Method Get -Headers $headers
$dnsResponse | ConvertTo-Json -Depth 10
Write-Host ""

# 4. 列出集群
Write-Host "[4/5] 列出集群..." -ForegroundColor Yellow
$clusterResponse = Invoke-RestMethod -Uri "$API_URL/clusters?page=1&per_page=10" -Method Get -Headers $headers
$clusterResponse | ConvertTo-Json -Depth 10
Write-Host ""

# 5. 列出边缘节点
Write-Host "[5/5] 列出边缘节点..." -ForegroundColor Yellow
$edgeResponse = Invoke-RestMethod -Uri "$API_URL/edges?page=1&per_page=10" -Method Get -Headers $headers
$edgeResponse | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "测试完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
```

运行方法:
```powershell
.\api_test.ps1
```

### 7.12 curl 使用技巧

#### 7.12.1 格式化 JSON 输出

使用 `jq` 工具格式化输出（需要先安装 jq）:

```cmd
curl -X GET "%API_URL%/environments/current" | jq .
```

#### 7.12.2 保存响应到文件

```cmd
curl -X GET "%API_URL%/dns_routing_rules" ^
  -H "Authorization: Bearer %API_TOKEN%" ^
  -o "response.json"
```

#### 7.12.3 显示详细请求信息

```cmd
curl -v -X GET "%API_URL%/environments/current"
```

#### 7.12.4 只显示响应头

```cmd
curl -I -X GET "%API_URL%/environments/current"
```

#### 7.12.5 显示响应头和响应体

```cmd
curl -i -X GET "%API_URL%/environments/current"
```

#### 7.12.6 忽略 SSL 证书验证（不推荐）

```cmd
curl -k -X GET "%API_URL%/environments/current"
```

### 7.13 常见问题

#### Q: Windows CMD 中 JSON 字符串如何转义双引号？

A: 在 CMD 中，双引号需要用反斜杠转义，或者使用 `--data-binary "@file.json"` 从文件读取。

**错误示例:**
```cmd
REM 错误：双引号未转义
curl -X POST ... -d "{"name":"test"}"
```

**正确示例:**
```cmd
REM 方法1：转义双引号
curl -X POST ... -d "{\"name\":\"test\"}"

REM 方法2：从文件读取（推荐）
curl -X POST ... --data-binary "@data.json"
```

#### Q: PowerShell 中 `curl` 不是 curl.exe？

A: PowerShell 中的 `curl` 是 `Invoke-WebRequest` 的别名。请使用 `curl.exe` 或 `Invoke-RestMethod`。

```powershell
# 使用 curl.exe
curl.exe -X GET "..."

# 或者使用 PowerShell 原生命令
Invoke-RestMethod -Uri "..." -Method Get
```

#### Q: 特殊字符如何处理？

A: URL 中的特殊字符需要 URL 编码：

| 字符 | 编码 |
|------|------|
| 空格 | %20 或 + |
| & | %26 |
| = | %3D |
| ? | %3F |

---

## 8. Python 客户端示例

### 8.1 完整的 Python 客户端封装

```python
import requests
import json
from typing import Optional, Dict, Any, List

class AxisNowClient:
    """
    AxisNow API 客户端封装类
    """
    
    def __init__(self, api_token: str, base_url: str = "https://api.axisnow.io/client/v1"):
        """
        初始化客户端
        
        Args:
            api_token: API 访问令牌
            base_url: API 基础 URL
        """
        self.api_token = api_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        内部请求方法
        
        Args:
            method: HTTP 方法
            path: API 路径
            **kwargs: 其他参数
        
        Returns:
            响应数据
        """
        url = f"{self.base_url}{path}"
        
        if "json" in kwargs:
            kwargs["data"] = json.dumps(kwargs.pop("json"))
        
        response = self.session.request(method, url, **kwargs)
        
        try:
            data = response.json()
        except ValueError:
            raise Exception(f"无效的 JSON 响应: {response.text}")
        
        if response.status_code >= 400:
            messages = data.get("messages", [])
            error_msg = " ; ".join([m.get("message", str(m)) for m in messages])
            raise Exception(f"API 错误 ({response.status_code}): {error_msg}")
        
        return data
    
    # ========== DNS 路由规则 ==========
    
    def list_dns_rules(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        列出 DNS 路由规则
        """
        return self._request("GET", "/dns_routing_rules", params={
            "page": page,
            "per_page": per_page
        })
    
    def create_dns_rule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建 DNS 路由规则
        """
        return self._request("POST", "/dns_routing_rules", json=payload)
    
    def get_dns_rule(self, uuid: str) -> Dict[str, Any]:
        """
        获取 DNS 路由规则详情
        """
        return self._request("GET", f"/dns_routing_rules/{uuid}")
    
    def update_dns_rule(self, uuid: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新 DNS 路由规则
        """
        return self._request("PUT", f"/dns_routing_rules/{uuid}", json=payload)
    
    def delete_dns_rule(self, uuid: str) -> Dict[str, Any]:
        """
        删除 DNS 路由规则
        """
        return self._request("DELETE", f"/dns_routing_rules/{uuid}")
    
    def filter_dns_rules(self, filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        筛选 DNS 路由规则
        """
        return self._request("POST", "/dns_routing_rules/filter", json=filter_params)
    
    # ========== DNS 路由域名 ==========
    
    def list_dns_domains(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        列出 DNS 路由域名
        """
        return self._request("GET", "/dns_routing_domains", params={
            "page": page,
            "per_page": per_page
        })
    
    def create_dns_domain(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建 DNS 路由域名
        """
        return self._request("POST", "/dns_routing_domains", json=payload)
    
    def test_domain_integration(self, provider_type: str, zone_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试域名集成
        """
        return self._request("POST", "/dns_routing_domains/test_integrations", json={
            "provider_type": provider_type,
            "zone_config": zone_config
        })
    
    # ========== 集群管理 ==========
    
    def list_clusters(self, name: Optional[str] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        列出集群
        """
        params = {"page": page, "per_page": per_page}
        if name:
            params["name"] = name
        return self._request("GET", "/clusters", params=params)
    
    def create_cluster(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        创建集群
        """
        return self._request("POST", "/clusters", json={
            "name": name,
            "description": description
        })
    
    # ========== 边缘节点 ==========
    
    def list_edges(self, cluster_uuid: Optional[str] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        列出边缘节点
        """
        params = {"page": page, "per_page": per_page}
        if cluster_uuid:
            params["cluster_uuid"] = cluster_uuid
        return self._request("GET", "/edges", params=params)
    
    def create_edge(self, name: str, cluster_uuid: str, description: str = "") -> Dict[str, Any]:
        """
        创建边缘节点
        """
        return self._request("POST", "/edges", json={
            "name": name,
            "cluster_uuid": cluster_uuid,
            "description": description
        })
    
    # ========== 计费 ==========
    
    def list_plans(self) -> Dict[str, Any]:
        """
        列出可订阅计划
        """
        return self._request("GET", "/billing/plans")
    
    def list_subscriptions(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        列出订阅
        """
        params = {}
        if status:
            params["status"] = status
        return self._request("GET", "/billing/subscriptions", params=params)
    
    def list_invoices(self, status: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        列出发票
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/billing/invoices", params=params)
    
    # ========== 包管理 ==========
    
    def get_package_info(self, package_identifier: str, version: str = "latest") -> Dict[str, Any]:
        """
        获取包信息（无需认证）
        """
        response = requests.get(
            f"{self.base_url}/packages/{package_identifier}",
            params={"version": version}
        )
        return response.json()
    
    def get_package_versions(self, package_identifier: str) -> Dict[str, Any]:
        """
        获取包版本列表（无需认证）
        """
        response = requests.get(
            f"{self.base_url}/packages/{package_identifier}/versions"
        )
        return response.json()
    
    # ========== 环境信息 ==========
    
    def get_current_environment(self) -> Dict[str, Any]:
        """
        获取当前环境信息（无需认证）
        """
        response = requests.get(f"{self.base_url}/environments/current")
        return response.json()


# ========== 使用示例 ==========

def main():
    """
    客户端使用示例
    """
    API_TOKEN = "your-api-token"
    
    # 初始化客户端
    client = AxisNowClient(API_TOKEN)
    
    try:
        # 1. 获取环境信息
        print("=" * 50)
        print("环境信息:")
        env = client.get_current_environment()
        print(json.dumps(env, indent=2, ensure_ascii=False))
        
        # 2. 列出 DNS 路由规则
        print("\n" + "=" * 50)
        print("DNS 路由规则列表:")
        rules = client.list_dns_rules(page=1, per_page=10)
        print(json.dumps(rules, indent=2, ensure_ascii=False))
        
        # 3. 列出集群
        print("\n" + "=" * 50)
        print("集群列表:")
        clusters = client.list_clusters()
        print(json.dumps(clusters, indent=2, ensure_ascii=False))
        
        # 4. 获取 Edge 包信息
        print("\n" + "=" * 50)
        print("Edge 包最新版本:")
        package_info = client.get_package_info("edge", "latest")
        print(json.dumps(package_info, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
```

### 7.2 快速开始指南

```python
"""
AxisNow API 快速开始
"""

import requests
import json

# 配置
API_URL = "https://api.axisnow.io/client/v1"
API_TOKEN = "your-api-token"  # 请替换为你的 API Token

# 公共请求头
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def quick_start():
    """
    快速开始示例
    """
    
    # 1. 首先检查环境
    print("1. 检查环境...")
    env_response = requests.get(f"{API_URL}/environments/current")
    print(f"环境: {env_response.json()}")
    
    # 2. 列出可用的 DNS 路由规则
    print("\n2. 列出 DNS 路由规则...")
    rules_response = requests.get(
        f"{API_URL}/dns_routing_rules",
        headers=HEADERS,
        params={"page": 1, "per_page": 10}
    )
    rules = rules_response.json()
    print(f"找到 {len(rules.get('result', {}).get('items', []))} 条规则")
    
    # 3. 列出集群
    print("\n3. 列出集群...")
    clusters_response = requests.get(
        f"{API_URL}/clusters",
        headers=HEADERS
    )
    clusters = clusters_response.json()
    print(f"找到 {len(clusters.get('result', {}).get('items', []))} 个集群")
    
    # 4. 获取包版本信息
    print("\n4. 获取 Edge 包信息...")
    package_response = requests.get(
        f"{API_URL}/packages/edge",
        params={"version": "latest"}
    )
    package = package_response.json()
    print(f"最新 Edge 版本信息获取成功")
    
    print("\n" + "=" * 50)
    print("快速开始完成！")
    print("=" * 50)


if __name__ == "__main__":
    quick_start()
```

---

## 附录

### A. 术语表

| 术语 | 英文 | 描述 |
|------|------|------|
| DNS 路由规则 | DNS Routing Rule | 定义 DNS 流量如何路由的规则 |
| DNS 提供商 | DNS Provider | 第三方 DNS 服务提供商 |
| 边缘节点 | Edge Node | 部署在边缘位置的计算节点 |
| 集群 | Cluster | 边缘节点的逻辑分组 |
| 工作负载标识 | Workload Identity | 客户端应用的身份标识 |

### B. 支持的 DNS 提供商完整列表

1. **Cloudflare** - 全球 CDN 和 DNS 服务
2. **阿里云 (Alibaba Cloud)** - 阿里云 DNS 解析
3. **DNSPod** - 腾讯云 DNS 服务
4. **华为云 (Huawei Cloud)** - 华为云 DNS
5. **AWS Route 53** - Amazon DNS 服务
6. **ClouDNS** - 欧洲 DNS 服务
7. **自建 DNS (Self-hosted)** - 自定义 DNS 服务器

### C. 常见问题

**Q: 如何获取 API Token？**
A: 请登录 AxisNow 控制台，在设置页面创建 API Token。

**Q: API 请求有频率限制吗？**
A: 是的，具体限制取决于您的订阅计划。请参考计费模块获取详细信息。

**Q: 支持哪些编程语言？**
A: API 是 RESTful 风格，支持任何可以发送 HTTP 请求的编程语言。本手册提供了 Python 示例。

**Q: 如何处理分页？**
A: 使用 `page` 和 `per_page` 参数进行分页。响应中的 `result_info` 字段包含分页信息。

---

**文档版本**: 1.0  
**最后更新**: 2026-06-06  
**API 版本**: 0.0.1
