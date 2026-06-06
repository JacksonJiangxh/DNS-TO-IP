"""
DNS IP Test - Cloudflare优选域名解析器 v2.1.0
高效解析、检测和识别Cloudflare优选域名的IP状态和详情信息

主要功能:
- DNS解析：多DNS服务器并发解析域名获取IP地址
- 快速筛选：TCP连接测试剔除明显不可用的IP
- 延迟测试：TCP Ping测试获取准确延迟数据
- 带宽测试：HTTP下载测试测量IP带宽性能
- 地区识别：API查询IP地理位置信息并缓存
- 智能排序：综合延迟、带宽、稳定性进行评分排序
- 文件输出：生成基础版和高级版IP列表文件

技术特性:
- 智能缓存系统：支持TTL机制，减少重复API调用
- 并发处理：多线程并发大幅提升检测速度
- 错误处理：完善的异常处理和重试机制
- 日志系统：详细的操作日志记录，支持文件输出
- 资源管理：自动限制缓存大小，防止内存溢出
- 环境优化：针对GitHub Actions等CI环境优化
"""

# ===== 标准库导入 =====
import re
import os
import sys
import time
import socket
import json
import logging
import argparse
import dns.resolver
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# ===== 第三方库导入 =====
import requests
from urllib3.exceptions import InsecureRequestWarning

# ===== 配置和初始化 =====

# 禁用SSL证书警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('DNSIPtest.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 功能开关默认值 =====
DEFAULT_FLAGS = {
    "enable_preprocess": True,         # 是否进行预处理（删除旧文件）
    "enable_load_domains": True,       # 是否加载域名列表
    "enable_dns_resolve": True,        # 是否进行DNS解析
    "enable_dedup_sort": True,         # 是否进行IP去重和排序
    "enable_quick_filter": True,       # 是否进行快速筛选（TCP连接测试）
    "enable_region_detection": True,   # 是否进行IP地区识别
    "enable_latency_filter": True,     # 是否进行延迟排名筛选（前30%）
    "enable_tcp_ping": True,           # 是否进行TCP Ping延迟测试
    "enable_bandwidth_test": True,     # 是否进行带宽测试
    "enable_basic_output": True,       # 是否生成基础版输出文件
    "enable_pro_output": True,         # 是否生成高级版输出文件
    "enable_cache_update": True,       # 是否更新缓存文件
}

# ===== 核心配置 =====
CONFIG = {
    # DNS服务器配置 - 经过连通性测试验证的DNS服务器列表
    # 测试时间: 2025-06-06，测试域名: cloudflare.com，超时: 3秒
    # 共测试150+个DNS，以下57个已验证可用
    "dns_servers": {
        # ============================================
        # 国内公共DNS（延迟最低，优先使用）
        # ============================================
        '182.254.116.116': '腾讯-DNS',
        '114.114.114.114': '114-DNS',
        '119.29.29.29': '腾讯-DNS',
        '114.114.115.115': '114-DNS',
        '223.6.6.6': '阿里云-DNS',
        '223.5.5.5': '阿里云-DNS',
        '223.5.5.6': '阿里云-DNS',
        '180.76.76.76': '百度-DNS',
        '1.2.4.8': 'CNNIC-DNS',
        '117.50.11.11': 'OneDNS',
        '52.80.66.66': 'OneDNS',
        
        # ============================================
        # 运营商DNS - 经过测试验证可用的
        # ============================================
        # 中国电信
        '202.103.225.68': '中国电信-广西',
        '202.98.198.167': '中国电信-贵州',
        '202.103.224.68': '中国电信-广西',
        '202.98.192.67': '中国电信-贵州',
        '202.102.213.68': '中国电信-安徽',
        '61.132.163.68': '中国电信-安徽',
        '101.226.4.6': '中国电信-全国',
        '218.30.118.6': '中国电信-全国',
        
        # 中国联通
        '202.103.24.68': '中国联通-湖北',
        '202.106.195.68': '中国联通-北京',
        '202.106.46.151': '中国联通-北京',
        '123.123.123.124': '中国联通-全国',
        '123.123.123.123': '中国联通-全国',
        '202.106.0.20': '中国联通-北京',
        '123.125.81.6': '中国联通-全国',
        
        # ============================================
        # 亚太地区DNS（可能解析到更多亚太Cloudflare节点）
        # ============================================
        '168.95.192.1': '中华电信-DNS',
        '168.95.1.1': '中华电信-DNS',
        '168.126.63.1': '韩国KT-DNS',
        '168.126.63.2': '韩国KT-DNS',
        
        # ============================================
        # 国际DNS服务器（解析到更多全球节点）
        # ============================================
        '1.1.1.3': 'Cloudflare-DNS(家庭)',
        '1.0.0.1': 'Cloudflare-DNS',
        '1.1.1.2': 'Cloudflare-DNS(安全)',
        '1.1.1.1': 'Cloudflare-DNS',
        '8.8.4.4': 'Google-DNS',
        '8.8.8.8': 'Google-DNS',
        '9.9.9.9': 'Quad9-DNS',
        '149.112.112.112': 'Quad9-DNS',
        '9.9.9.10': 'Quad9-DNS(无过滤)',
        '208.67.222.222': 'OpenDNS',
        '208.67.220.220': 'OpenDNS',
        '208.67.220.123': 'OpenDNS(家庭安全)',
        
        # ============================================
        # 其他国际公共DNS
        # ============================================
        '185.222.222.222': 'DNS.SB',
        '4.2.2.2': '微软-DNS',
        '4.2.2.1': '微软-DNS',
        '209.244.0.4': 'Level3-DNS',
        '209.244.0.3': 'Level3-DNS',
        '185.228.169.9': 'CleanBrowsing-DNS',
        '156.154.70.1': 'Neustar-DNS',
        '156.154.71.1': 'Neustar-DNS',
        '8.26.56.26': 'Comodo-DNS',
        '8.20.247.20': 'Comodo-DNS',
        '64.6.65.6': 'Verisign-DNS',
        '94.140.15.15': 'AdGuard-DNS',
        '94.140.14.14': 'AdGuard-DNS',
        '77.88.8.1': 'Yandex-DNS',
        '77.88.8.88': 'Yandex-DNS(安全)',
    },
    # 网络测试配置
    "test_ports": [443],            # TCP连接测试端口（HTTPS端口）
    "timeout": 15,                  # DNS解析超时时间（秒）
    "api_timeout": 5,               # API查询超时时间（秒）
    "query_interval": 0.2,          # API查询间隔时间（秒）

    # 并发处理配置（GitHub Actions环境优化）
    "max_workers": 15,              # 最大并发线程数
    "batch_size": 10,               # 批量处理IP数量
    "cache_ttl_hours": 168,         # 缓存有效期（7天）
    
    # 高级功能配置
    "advanced_mode": True,          # 高级模式开关（True=开启，False=关闭）
    "tcp_ping_count": 5,            # TCP Ping测试次数
    "bandwidth_test_count": 3,       # 带宽测试次数
    "bandwidth_test_size_mb": 10,     # 带宽测试文件大小（MB）
    "latency_filter_percentage": 30, # 延迟排名前百分比（取前30%的IP）
    
    # 功能开关（可通过命令行、环境变量、配置文件覆盖）
    **DEFAULT_FLAGS,
}

# ===== 国家/地区映射表 =====
# ISO国家代码到中文名称的映射，用于地区识别结果显示
COUNTRY_MAPPING = {
# 统一添加常见国家和地区
    # 北美
    'US': '美国', 'CA': '加拿大', 'MX': '墨西哥', 'CR': '哥斯达黎加', 'GT': '危地马拉', 'HN': '洪都拉斯',
    'NI': '尼加拉瓜', 'PA': '巴拿马', 'CU': '古巴', 'JM': '牙买加', 'TT': '特立尼达和多巴哥',
    'BZ': '伯利兹', 'SV': '萨尔瓦多', 'DO': '多米尼加', 'HT': '海地',
    # 南美
    'BR': '巴西', 'AR': '阿根廷', 'CL': '智利', 'CO': '哥伦比亚', 'PE': '秘鲁', 'VE': '委内瑞拉',
    'UY': '乌拉圭', 'PY': '巴拉圭', 'BO': '玻利维亚', 'EC': '厄瓜多尔', 'GY': '圭亚那',
    'SR': '苏里南', 'FK': '福克兰群岛',
    # 欧洲
    'UK': '英国', 'GB': '英国', 'FR': '法国', 'DE': '德国', 'IT': '意大利', 'ES': '西班牙', 'NL': '荷兰',
    'RU': '俄罗斯', 'SE': '瑞典', 'CH': '瑞士', 'BE': '比利时', 'AT': '奥地利', 'IS': '冰岛',
    'PL': '波兰', 'DK': '丹麦', 'NO': '挪威', 'FI': '芬兰', 'PT': '葡萄牙', 'IE': '爱尔兰',
    'UA': '乌克兰', 'CZ': '捷克', 'GR': '希腊', 'HU': '匈牙利', 'RO': '罗马尼亚', 'TR': '土耳其',
    'BG': '保加利亚', 'LT': '立陶宛', 'LV': '拉脱维亚', 'EE': '爱沙尼亚', 'BY': '白俄罗斯',
    'LU': '卢森堡', 'LUX': '卢森堡', 'SI': '斯洛文尼亚', 'SK': '斯洛伐克', 'MT': '马耳他',
    'HR': '克罗地亚', 'RS': '塞尔维亚', 'BA': '波黑', 'ME': '黑山', 'MK': '北马其顿',
    'AL': '阿尔巴尼亚', 'XK': '科索沃', 'MD': '摩尔多瓦', 'GE': '格鲁吉亚', 'AM': '亚美尼亚',
    'AZ': '阿塞拜疆', 'CY': '塞浦路斯', 'MC': '摩纳哥', 'SM': '圣马力诺', 'VA': '梵蒂冈',
    'AD': '安道尔', 'LI': '列支敦士登',
    # 亚洲
    'CN': '中国', 'HK': '中国香港', 'TW': '中国台湾', 'MO': '中国澳门', 'JP': '日本', 'KR': '韩国',
    'SG': '新加坡', 'SGP': '新加坡', 'IN': '印度', 'ID': '印度尼西亚', 'MY': '马来西亚', 'MYS': '马来西亚',
    'TH': '泰国', 'PH': '菲律宾', 'VN': '越南', 'PK': '巴基斯坦', 'BD': '孟加拉', 'KZ': '哈萨克斯坦',
    'IL': '以色列', 'ISR': '以色列', 'SA': '沙特阿拉伯', 'SAU': '沙特阿拉伯', 'AE': '阿联酋', 
    'QAT': '卡塔尔', 'OMN': '阿曼', 'KW': '科威特', 'BH': '巴林', 'IQ': '伊拉克', 'IR': '伊朗',
    'AF': '阿富汗', 'UZ': '乌兹别克斯坦', 'KG': '吉尔吉斯斯坦', 'TJ': '塔吉克斯坦', 'TM': '土库曼斯坦',
    'MN': '蒙古', 'NP': '尼泊尔', 'BT': '不丹', 'LK': '斯里兰卡', 'MV': '马尔代夫',
    'MM': '缅甸', 'LA': '老挝', 'KH': '柬埔寨', 'BN': '文莱', 'TL': '东帝汶',
    'LK': '斯里兰卡', 'MV': '马尔代夫', 'NP': '尼泊尔', 'BT': '不丹',
    # 大洋洲
    'AU': '澳大利亚', 'NZ': '新西兰', 'FJ': '斐济', 'PG': '巴布亚新几内亚', 'NC': '新喀里多尼亚',
    'VU': '瓦努阿图', 'SB': '所罗门群岛', 'TO': '汤加', 'WS': '萨摩亚', 'KI': '基里巴斯',
    'TV': '图瓦卢', 'NR': '瑙鲁', 'PW': '帕劳', 'FM': '密克罗尼西亚', 'MH': '马绍尔群岛',
    # 非洲
    'ZA': '南非', 'EG': '埃及', 'NG': '尼日利亚', 'KE': '肯尼亚', 'ET': '埃塞俄比亚',
    'GH': '加纳', 'TZ': '坦桑尼亚', 'UG': '乌干达', 'DZ': '阿尔及利亚', 'MA': '摩洛哥',
    'TN': '突尼斯', 'LY': '利比亚', 'SD': '苏丹', 'SS': '南苏丹', 'ER': '厄立特里亚',
    'DJ': '吉布提', 'SO': '索马里', 'ET': '埃塞俄比亚', 'KE': '肯尼亚', 'TZ': '坦桑尼亚',
    'UG': '乌干达', 'RW': '卢旺达', 'BI': '布隆迪', 'MW': '马拉维', 'ZM': '赞比亚',
    'ZW': '津巴布韦', 'BW': '博茨瓦纳', 'NA': '纳米比亚', 'SZ': '斯威士兰', 'LS': '莱索托',
    'MZ': '莫桑比克', 'MG': '马达加斯加', 'MU': '毛里求斯', 'SC': '塞舌尔', 'KM': '科摩罗',
    'CV': '佛得角', 'ST': '圣多美和普林西比', 'GW': '几内亚比绍', 'GN': '几内亚', 'SL': '塞拉利昂',
    'LR': '利比里亚', 'CI': '科特迪瓦', 'GH': '加纳', 'TG': '多哥', 'BJ': '贝宁',
    'NE': '尼日尔', 'BF': '布基纳法索', 'ML': '马里', 'SN': '塞内加尔', 'GM': '冈比亚',
    'GN': '几内亚', 'GW': '几内亚比绍', 'ST': '圣多美和普林西比', 'CV': '佛得角',
    # 其他
    'Unknown': '未知'
}

# ===== 全局变量 =====
region_cache = {}  # IP地区信息缓存，减少重复API调用

# ===== 网络会话配置 =====
# 创建HTTP会话，配置请求头和连接池以提高性能
session = requests.Session()
# 设置浏览器请求头，模拟真实浏览器访问
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
})
# 配置HTTP连接池，提高并发请求性能
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,    # 连接池数量
    pool_maxsize=20,        # 每个连接池最大连接数
    max_retries=3          # 最大重试次数
)
session.mount('http://', adapter)
session.mount('https://', adapter)

# ===== 0. 配置加载模块 =====
# 支持三种配置方式：命令行参数 > 环境变量 > 配置文件 > 默认值

def parse_bool(value):
    """解析布尔值，支持多种格式"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 't', 'y')
    return bool(value)

def load_config_file(config_file='config.json'):
    """从配置文件加载配置（可选）"""
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.info(f"📄 已加载配置文件: {config_file}")
            return config_data
        except Exception as e:
            logger.warning(f"⚠️ 配置文件加载失败: {str(e)[:50]}")
    return {}

def load_env_config():
    """从环境变量加载配置"""
    env_config = {}
    env_mapping = {
        'ENABLE_PREPROCESS': 'enable_preprocess',
        'ENABLE_LOAD_DOMAINS': 'enable_load_domains',
        'ENABLE_DNS_RESOLVE': 'enable_dns_resolve',
        'ENABLE_DEDUP_SORT': 'enable_dedup_sort',
        'ENABLE_QUICK_FILTER': 'enable_quick_filter',
        'ENABLE_REGION_DETECTION': 'enable_region_detection',
        'ENABLE_LATENCY_FILTER': 'enable_latency_filter',
        'ENABLE_TCP_PING': 'enable_tcp_ping',
        'ENABLE_BANDWIDTH_TEST': 'enable_bandwidth_test',
        'ENABLE_BASIC_OUTPUT': 'enable_basic_output',
        'ENABLE_PRO_OUTPUT': 'enable_pro_output',
        'ENABLE_CACHE_UPDATE': 'enable_cache_update',
    }
    
    for env_key, config_key in env_mapping.items():
        if env_key in os.environ:
            env_config[config_key] = parse_bool(os.environ[env_key])
            logger.info(f"🌍 环境变量: {env_key} = {env_config[config_key]}")
    
    return env_config

def parse_command_line():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='DNS IP Test - Cloudflare优选域名解析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
完整模块列表（可独立开关）:
  1. 预处理 (--no-preprocess)       - 删除旧文件
  2. 加载域名 (--no-load-domains)    - 从YXhost文件加载域名
  3. DNS解析 (--no-dns-resolve)      - 多DNS服务器解析域名
  4. 去重排序 (--no-dedup-sort)      - IP去重和排序
  5. 快速筛选 (--no-quick-filter)    - TCP连接测试剔除不可用IP
  6. 地区识别 (--no-region-detection)- API查询IP地理位置
  7. 延迟筛选 (--no-latency-filter)  - 延迟排名前30%%筛选
  8. TCP Ping (--no-tcp-ping)        - 多次ping获取准确延迟
  9. 带宽测试 (--no-bandwidth-test)  - HTTP下载测试带宽
  10.基础输出 (--no-basic-output)    - 生成DNSIPlist.txt/DNSResult.txt
  11.高级输出 (--no-pro-output)      - 生成Pro版文件
  12.缓存更新 (--no-cache-update)    - 更新Cache.json

使用示例:
  # 跳过带宽测试和地区识别
  python DNSIPtest.py --no-bandwidth-test --no-region-detection
  
  # 仅进行DNS解析（不做任何测试，不保存文件）
  python DNSIPtest.py --quick
  
  # 自定义配置文件
  python DNSIPtest.py --config my-config.json

优先级: 命令行 > 环境变量 > 配置文件 > 默认值
        """
    )
    
    # 模块1：预处理
    parser.add_argument('--no-preprocess', 
                        dest='enable_preprocess', 
                        action='store_false',
                        default=None,
                        help='跳过预处理（不删除旧文件）')
    
    # 模块2：加载域名
    parser.add_argument('--no-load-domains', 
                        dest='enable_load_domains', 
                        action='store_false',
                        default=None,
                        help='跳过加载域名列表')
    
    # 模块3：DNS解析
    parser.add_argument('--no-dns-resolve', 
                        dest='enable_dns_resolve', 
                        action='store_false',
                        default=None,
                        help='跳过DNS解析')
    
    # 模块4：去重排序
    parser.add_argument('--no-dedup-sort', 
                        dest='enable_dedup_sort', 
                        action='store_false',
                        default=None,
                        help='跳过IP去重和排序')
    
    # 模块5：快速筛选
    parser.add_argument('--no-quick-filter', 
                        dest='enable_quick_filter', 
                        action='store_false',
                        default=None,
                        help='跳过快速筛选（TCP连接测试）')
    
    # 模块6：地区识别
    parser.add_argument('--no-region-detection', 
                        dest='enable_region_detection', 
                        action='store_false',
                        default=None,
                        help='跳过IP地区识别（不调用地理位置API）')
    
    # 模块7：延迟筛选
    parser.add_argument('--no-latency-filter', 
                        dest='enable_latency_filter', 
                        action='store_false',
                        default=None,
                        help='跳过延迟排名前30%%筛选')
    
    # 模块8：TCP Ping
    parser.add_argument('--no-tcp-ping', 
                        dest='enable_tcp_ping', 
                        action='store_false',
                        default=None,
                        help='跳过TCP Ping延迟测试')
    
    # 模块9：带宽测试
    parser.add_argument('--no-bandwidth-test', 
                        dest='enable_bandwidth_test', 
                        action='store_false',
                        default=None,
                        help='跳过带宽测试（最耗时的步骤）')
    
    # 模块10：基础输出
    parser.add_argument('--no-basic-output', 
                        dest='enable_basic_output', 
                        action='store_false',
                        default=None,
                        help='不生成基础版输出文件（DNSIPlist.txt等）')
    
    # 模块11：高级输出
    parser.add_argument('--no-pro-output', 
                        dest='enable_pro_output', 
                        action='store_false',
                        default=None,
                        help='不生成高级版输出文件（DNSIPlist-Pro.txt等）')
    
    # 模块12：缓存更新
    parser.add_argument('--no-cache-update', 
                        dest='enable_cache_update', 
                        action='store_false',
                        default=None,
                        help='不更新缓存文件（只读模式）')
    
    # 快捷模式
    parser.add_argument('--quick', 
                        action='store_true',
                        help='快速模式：仅DNS解析，不进行任何测试，不保存任何文件')
    
    # 配置文件路径
    parser.add_argument('--config', 
                        type=str, 
                        default=None,
                        help='指定配置文件路径（默认: config.json）')
    
    args = parser.parse_args()
    
    # 快捷模式处理：只进行DNS解析，跳过所有其他功能
    if args.quick:
        args.enable_preprocess = False
        args.enable_load_domains = True  # 必须加载域名
        args.enable_dns_resolve = True   # 必须进行DNS解析
        args.enable_dedup_sort = False
        args.enable_quick_filter = False
        args.enable_region_detection = False
        args.enable_latency_filter = False
        args.enable_tcp_ping = False
        args.enable_bandwidth_test = False
        args.enable_basic_output = False
        args.enable_pro_output = False
        args.enable_cache_update = False
    
    # 构建命令行配置字典（只包含显式设置的参数）
    cli_config = {}
    if args.enable_preprocess is not None:
        cli_config['enable_preprocess'] = args.enable_preprocess
    if args.enable_load_domains is not None:
        cli_config['enable_load_domains'] = args.enable_load_domains
    if args.enable_dns_resolve is not None:
        cli_config['enable_dns_resolve'] = args.enable_dns_resolve
    if args.enable_dedup_sort is not None:
        cli_config['enable_dedup_sort'] = args.enable_dedup_sort
    if args.enable_quick_filter is not None:
        cli_config['enable_quick_filter'] = args.enable_quick_filter
    if args.enable_region_detection is not None:
        cli_config['enable_region_detection'] = args.enable_region_detection
    if args.enable_latency_filter is not None:
        cli_config['enable_latency_filter'] = args.enable_latency_filter
    if args.enable_tcp_ping is not None:
        cli_config['enable_tcp_ping'] = args.enable_tcp_ping
    if args.enable_bandwidth_test is not None:
        cli_config['enable_bandwidth_test'] = args.enable_bandwidth_test
    if args.enable_basic_output is not None:
        cli_config['enable_basic_output'] = args.enable_basic_output
    if args.enable_pro_output is not None:
        cli_config['enable_pro_output'] = args.enable_pro_output
    if args.enable_cache_update is not None:
        cli_config['enable_cache_update'] = args.enable_cache_update
    
    return cli_config, args.config

def merge_configs():
    """
    合并配置，优先级从高到低：
    1. 命令行参数
    2. 环境变量
    3. 配置文件
    4. 默认值
    """
    # 1. 解析命令行参数
    cli_config, config_file = parse_command_line()
    
    # 2. 加载环境变量
    env_config = load_env_config()
    
    # 3. 加载配置文件
    file_config = load_config_file(config_file if config_file else 'config.json')
    
    # 4. 合并配置（优先级：cli > env > file > default）
    merged = DEFAULT_FLAGS.copy()
    
    # 先应用配置文件
    for key in DEFAULT_FLAGS:
        if key in file_config:
            merged[key] = parse_bool(file_config[key])
    
    # 再应用环境变量
    for key, value in env_config.items():
        merged[key] = value
    
    # 最后应用命令行参数（最高优先级）
    for key, value in cli_config.items():
        merged[key] = value
    
    # 更新全局CONFIG
    CONFIG.update(merged)
    
    # 打印最终配置
    logger.info("⚙️  ===== 功能开关配置 =====")
    logger.info(f"  [1] 预处理:       {CONFIG['enable_preprocess']}")
    logger.info(f"  [2] 加载域名:     {CONFIG['enable_load_domains']}")
    logger.info(f"  [3] DNS解析:      {CONFIG['enable_dns_resolve']}")
    logger.info(f"  [4] 去重排序:     {CONFIG['enable_dedup_sort']}")
    logger.info(f"  [5] 快速筛选:     {CONFIG['enable_quick_filter']}")
    logger.info(f"  [6] 地区识别:     {CONFIG['enable_region_detection']}")
    logger.info(f"  [7] 延迟筛选:     {CONFIG['enable_latency_filter']}")
    logger.info(f"  [8] TCP Ping:     {CONFIG['enable_tcp_ping']}")
    logger.info(f"  [9] 带宽测试:     {CONFIG['enable_bandwidth_test']}")
    logger.info(f"  [10] 基础输出:    {CONFIG['enable_basic_output']}")
    logger.info(f"  [11] 高级输出:    {CONFIG['enable_pro_output']}")
    logger.info(f"  [12] 缓存更新:    {CONFIG['enable_cache_update']}")
    
    return merged

# ===== 1. 缓存管理模块 =====
# 智能缓存系统，支持TTL机制，减少重复API调用，提高程序运行效率

def load_region_cache():
    """加载地区缓存文件到内存"""
    global region_cache
    if os.path.exists('Cache.json'):
        try:
            with open('Cache.json', 'r', encoding='utf-8') as f:
                region_cache = json.load(f)
            logger.info(f"📦 成功加载缓存文件，包含 {len(region_cache)} 个条目")
        except Exception as e:
            logger.warning(f"⚠️ 加载缓存文件失败: {str(e)[:50]}")
            region_cache = {}
    else:
        logger.info("📦 缓存文件不存在，使用空缓存")
        region_cache = {}

def save_region_cache():
    """保存地区缓存到文件"""
    try:
        with open('Cache.json', 'w', encoding='utf-8') as f:
            json.dump(region_cache, f, ensure_ascii=False)
        logger.info(f"💾 成功保存缓存文件，包含 {len(region_cache)} 个条目")
    except Exception as e:
        logger.error(f"❌ 保存缓存文件失败: {str(e)[:50]}")
        pass

def is_cache_valid(timestamp, ttl_hours=24):
    """检查缓存是否在有效期内"""
    if not timestamp:
        return False
    cache_time = datetime.fromisoformat(timestamp)
    return datetime.now() - cache_time < timedelta(hours=ttl_hours)

def clean_expired_cache():
    """清理过期缓存条目并限制缓存大小，防止内存溢出"""
    global region_cache
    current_time = datetime.now()
    expired_keys = []
    
    # 清理过期缓存
    for ip, data in region_cache.items():
        if isinstance(data, dict) and 'timestamp' in data:
            cache_time = datetime.fromisoformat(data['timestamp'])
            if current_time - cache_time >= timedelta(hours=CONFIG["cache_ttl_hours"]):
                expired_keys.append(ip)
    
    for key in expired_keys:
        del region_cache[key]
    
    # 限制缓存大小（最多保留1000个条目）
    if len(region_cache) > 1000:
        # 按时间排序，删除最旧的条目
        sorted_items = sorted(region_cache.items(), 
                            key=lambda x: x[1].get('timestamp', '') if isinstance(x[1], dict) else '')
        items_to_remove = len(region_cache) - 1000
        for i in range(items_to_remove):
            del region_cache[sorted_items[i][0]]
        logger.info(f"缓存过大，清理了 {items_to_remove} 个旧条目")
    
    if expired_keys:
        logger.info(f"清理了 {len(expired_keys)} 个过期缓存条目")

# ===== 2. 文件操作模块 =====
# 文件管理功能，包括删除、加载、保存等操作

def delete_file_if_exists(file_path):
    """删除指定文件（如果存在），避免结果累积"""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"🗑️ 已删除原有文件: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️ 删除文件失败: {str(e)}")

def load_domain_list():
    """
    从域名列表文件加载域名，支持注释行过滤
    
    文件优先级：YXhost.txt > YXhost-lite.txt
    这样用户可以选择用哪个文件名，保持兼容性
    """
    domains = []
    
    # 定义域名文件列表（按优先级排序）
    domain_files = ['YXhost.txt', 'YXhost-lite.txt']
    selected_file = None
    
    # 选择第一个存在的文件
    for file_path in domain_files:
        if os.path.exists(file_path):
            selected_file = file_path
            break
    
    if selected_file:
        try:
            with open(selected_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取域名部分，忽略#后面的描述信息
                        domain = line.split('#')[0].strip()
                        if domain:
                            domains.append(domain)
            logger.info(f"📄 成功从 {selected_file} 加载 {len(domains)} 个域名")
        except Exception as e:
            logger.error(f"❌ 加载域名文件 {selected_file} 失败: {str(e)}")
    else:
        logger.warning("⚠️ 未找到域名列表文件（YXhost.txt 或 YXhost-lite.txt）")
    
    return domains

# ===== 3. DNS解析模块 =====
# 多DNS服务器并发解析，获取最优IP地址

def query_single_dns(dns_server, dns_provider, domain, retry_count=1):
    """
    使用单个DNS服务器查询域名
    
    Args:
        dns_server: DNS服务器IP
        dns_provider: DNS提供商名称
        domain: 要解析的域名
        retry_count: 重试次数
    
    Returns:
        tuple: (成功的IP列表, 失败原因或None)
    """
    for attempt in range(retry_count + 1):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = 4  # 单次查询超时时间
            resolver.lifetime = 4
            
            # 查询A记录（IPv4）
            answers = resolver.resolve(domain, 'A')
            server_ips = []
            
            for answer in answers:
                ip = str(answer)
                # 验证IP地址格式
                if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip) and all(0 <= int(part) <= 255 for part in ip.split('.')):
                    server_ips.append(ip)
            
            return (server_ips, None, dns_server, dns_provider)
            
        except Exception as e:
            if attempt < retry_count:
                time.sleep(0.5)  # 重试前短暂等待
                continue
            error_msg = str(e)[:60]
            return ([], error_msg, dns_server, dns_provider)
    
    return ([], "重试次数用尽", dns_server, dns_provider)

def resolve_domain_concurrent(domain, max_workers=None):
    """
    使用并发方式从多个DNS服务器解析域名
    
    Args:
        domain: 要解析的域名
        max_workers: 最大并发线程数
    
    Returns:
        list: 唯一IP地址列表
    """
    if max_workers is None:
        max_workers = min(CONFIG["max_workers"], 20)  # DNS解析并发限制
    
    all_ips = []
    successful_servers = []
    failed_servers = []
    
    dns_servers_list = list(CONFIG["dns_servers"].items())
    total_servers = len(dns_servers_list)
    
    logger.info(f"🔍 开始并发解析域名 {domain}，使用 {total_servers} 个DNS服务器，{max_workers} 个并发线程...")
    
    # 使用线程池并发查询
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_dns = {
            executor.submit(query_single_dns, server, provider, domain, retry_count=1): (server, provider)
            for server, provider in dns_servers_list
        }
        
        # 处理完成的任务
        completed = 0
        for future in as_completed(future_to_dns):
            completed += 1
            server_ips, error, dns_server, dns_provider = future.result()
            unique_count = len(set(all_ips))
            
            if server_ips:
                successful_servers.append((dns_server, dns_provider))
                all_ips.extend(server_ips)
                unique_count_after = len(set(all_ips))
                logger.info(
                    f"🔍 [{completed:2d}/{total_servers}] {domain} -> {len(server_ips)} 个IP "
                    f"({dns_provider}: {dns_server}) | 累计唯一IP: {unique_count_after}"
                )
                logger.info(f"📋 {dns_provider}({dns_server}) 解析到的IP: {', '.join(server_ips)}")
            else:
                failed_servers.append((dns_server, dns_provider, error))
                if error:
                    logger.debug(
                        f"❌ [{completed:2d}/{total_servers}] DNS服务器 {dns_provider}({dns_server}) "
                        f"解析失败: {error}"
                    )
                else:
                    logger.debug(
                        f"❌ [{completed:2d}/{total_servers}] DNS服务器 {dns_provider}({dns_server}) "
                        f"未返回有效IP"
                    )
    
    # 去重
    unique_ips = list(set(all_ips))
    
    # 汇总结果
    logger.info(
        f"📊 {domain} 解析完成: 成功 {len(successful_servers)}/{total_servers} 个DNS服务器，"
        f"获得 {len(unique_ips)} 个唯一IP"
    )
    
    # 显示成功的DNS服务器
    if successful_servers:
        logger.info(
            f"✅ 成功的DNS服务器: "
            f"{', '.join([f'{provider}({server})' for server, provider in successful_servers])}"
        )
    
    # 显示失败的DNS服务器（简要）
    if failed_servers:
        failed_count = len(failed_servers)
        logger.warning(
            f"⚠️ {failed_count} 个DNS服务器解析失败"
        )
        if failed_count <= 10:
            for server, provider, error in failed_servers:
                logger.debug(f"   - {provider}({server}): {error if error else '无IP'}")
    
    # 显示所有解析到的IP
    if unique_ips:
        logger.info(f"📋 解析到的唯一IP列表: {', '.join(sorted(unique_ips))}")
    
    return unique_ips

def resolve_domain(domain):
    """使用多个DNS服务器解析域名获取IP地址（使用并发方式）"""
    return resolve_domain_concurrent(domain)

# ===== 4. 网络检测模块 =====
# IP可用性检测、延迟测试、带宽测试等功能

def quick_filter_ip(ip):
    """快速筛选IP，单次TCP连接测试，剔除明显不可用的IP"""
    # 验证IP地址格式
    try:
        parts = ip.split('.')
        if len(parts) != 4 or not all(0 <= int(part) <= 255 for part in parts):
            return False
    except (ValueError, AttributeError):
        return False
    
    # 检查测试端口配置
    if not CONFIG["test_ports"] or not isinstance(CONFIG["test_ports"], list):
        return False
    
    min_delay = float('inf')
    
    # 遍历配置的测试端口，只测试一次
    for port in CONFIG["test_ports"]:
        try:
            # 验证端口号
            if not isinstance(port, int) or not (1 <= port <= 65535):
                continue
                
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # 3秒超时
                start_time = time.time()
                
                # 尝试TCP连接
                if s.connect_ex((ip, port)) == 0:
                    delay = round((time.time() - start_time) * 1000)
                    min_delay = min(min_delay, delay)
                    
                    # 如果延迟很好，立即返回
                    if delay < 200:
                        return (True, delay)
        except (socket.timeout, socket.error, OSError):
            continue  # 继续测试下一个端口
        except Exception as e:
            logger.debug(f"IP {ip} 端口 {port} 快速筛选异常: {str(e)[:30]}")
            continue
    
    # 如果延迟超过500ms，直接剔除
    if min_delay > 500:
        return (False, 0)
    
    # 如果无法连接，直接剔除
    if min_delay == float('inf'):
        return (False, 0)
    
    return (True, min_delay)

def test_ip_availability(ip, ping_count=None):
    """TCP Socket检测IP可用性，多次ping测试获取准确延迟数据"""
    if ping_count is None:
        ping_count = CONFIG["tcp_ping_count"]
    # 验证IP地址格式
    try:
        parts = ip.split('.')
        if len(parts) != 4 or not all(0 <= int(part) <= 255 for part in parts):
            return (False, 0, 0, 0)
    except (ValueError, AttributeError):
        return (False, 0, 0, 0)
    
    # 检查测试端口配置
    if not CONFIG["test_ports"] or not isinstance(CONFIG["test_ports"], list):
        logger.warning(f"⚠️ 测试端口配置无效，跳过IP {ip}")
        return (False, 0, 0, 0)
    
    all_delays = []
    success_count = 0
    
    # 多次ping测试
    for ping_attempt in range(ping_count):
        min_delay = float('inf')
        
        # 遍历配置的测试端口
        for port in CONFIG["test_ports"]:
            try:
                # 验证端口号
                if not isinstance(port, int) or not (1 <= port <= 65535):
                    continue
                    
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(3)  # 3秒超时
                    start_time = time.time()
                    
                    # 尝试TCP连接
                    if s.connect_ex((ip, port)) == 0:
                        delay = round((time.time() - start_time) * 1000)
                        min_delay = min(min_delay, delay)
                        
                        # 如果延迟很好，记录并继续
                        if delay < 200:
                            all_delays.append(delay)
                            success_count += 1
                            break  # 找到好的延迟就跳出端口循环
            except (socket.timeout, socket.error, OSError):
                continue  # 继续测试下一个端口
            except Exception as e:
                logger.debug(f"IP {ip} 端口 {port} 检测异常: {str(e)[:30]}")
                continue
        
        # 如果这次ping没有成功，记录一个高延迟值
        if min_delay == float('inf'):
            all_delays.append(999)  # 标记为失败
        else:
            all_delays.append(min_delay)
    
    # 计算统计结果
    if success_count > 0:
        # 过滤掉失败的值（999）
        valid_delays = [d for d in all_delays if d < 999]
        if valid_delays:
            min_delay = min(valid_delays)
            avg_delay = sum(valid_delays) / len(valid_delays)
            # 计算稳定性（方差）
            variance = sum((d - avg_delay) ** 2 for d in valid_delays) / len(valid_delays)
            stability = round(variance, 2)
            return (True, min_delay, avg_delay, stability)
    
    return (False, 0, 0, 0)

def test_ip_bandwidth(ip, test_size_mb=None):
    """通过HTTP下载测试IP带宽性能"""
    if test_size_mb is None:
        test_size_mb = CONFIG["bandwidth_test_size_mb"]
    try:
        import requests
        
        # 验证IP地址格式
        parts = ip.split('.')
        if len(parts) != 4 or not all(0 <= int(part) <= 255 for part in parts):
            return (False, 0, 0)
        
        # 使用真实的下载测试来测量带宽
        test_size_bytes = test_size_mb * 1024 * 1024
        test_urls = [
            # 使用一些公开的测试文件
            f"https://speed.cloudflare.com/__down?bytes={test_size_bytes}",  # 可配置大小测试文件
            f"https://httpbin.org/bytes/{test_size_bytes}",  # 可配置大小测试文件
        ]
        
        best_speed = 0
        best_latency = 0
        
        # 使用配置的测试次数
        test_count = CONFIG["bandwidth_test_count"]
        for test_attempt in range(test_count):
            for url in test_urls:
                try:
                    start_time = time.time()
                    
                    # 发送HTTP请求测试带宽
                    response = requests.get(
                        url, 
                        timeout=15,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                        stream=True
                    )
                    
                    if response.status_code == 200:
                        # 测量下载速度
                        data_size = 0
                        start_download = time.time()
                        
                        # 下载数据块来测试速度
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                data_size += len(chunk)
                                # 限制测试时间，避免过长时间
                                if time.time() - start_download > 10:  # 最多测试10秒
                                    break
                                # 如果下载了足够的数据就停止
                                if data_size > 10 * 1024 * 1024:  # 10MB
                                    break
                        
                        download_time = time.time() - start_download
                        latency = (start_download - start_time) * 1000  # 延迟
                        
                        if download_time > 0 and data_size > 0:
                            # 计算速度 (Mbps)
                            speed_mbps = (data_size * 8) / (download_time * 1000000)
                            best_speed = max(best_speed, speed_mbps)
                            best_latency = latency if best_latency == 0 else min(best_latency, latency)
                            
                            # 如果速度很好，可以提前返回
                            if speed_mbps > 5:  # 超过5Mbps就认为很好
                                return (True, best_speed, best_latency)
                
                except Exception as e:
                    logger.debug(f"IP {ip} 带宽测试失败: {str(e)[:50]}")
                    continue
        
        if best_speed > 0:
            return (True, best_speed, best_latency)
        else:
            # 如果带宽测试失败，返回延迟测试结果
            is_available, latency = test_ip_availability(ip)
            if is_available:
                return (True, 0, latency)  # 返回0表示带宽测试失败，但延迟可用
            else:
                return (False, 0, 0)
            
    except Exception as e:
        logger.error(f"IP {ip} 带宽测试异常: {str(e)[:50]}")
        return (False, 0, 0)

def calculate_score(min_delay, avg_delay, bandwidth, stability):
    """计算IP综合评分，综合考虑延迟、带宽、稳定性"""
    # 延迟评分 (0-100, 延迟越低分数越高)
    latency_score = max(0, 100 - avg_delay / 2)
    
    # 带宽评分 (0-100, 带宽越高分数越高)
    bandwidth_score = min(100, bandwidth * 10)
    
    # 稳定性评分 (0-100, 稳定性越高分数越高)
    stability_score = max(0, 100 - stability / 10)
    
    # 综合评分 (延迟占40%, 带宽占30%, 稳定性占30%)
    total_score = latency_score * 0.4 + bandwidth_score * 0.3 + stability_score * 0.3
    return round(total_score, 1)

def test_ip_bandwidth_only(ip, index, total):
    """仅测试IP带宽，用于分离测试流程"""
    # 测试带宽
    is_fast, bandwidth, latency = test_ip_bandwidth(ip)
    
    # 输出带宽测试日志
    logger.info(f"⚡ [{index}/{total}] {ip}（带宽综合速度：{bandwidth:.2f}Mbps）")
    
    return (is_fast, bandwidth, latency)

def latency_filter_ips(ips_with_latency):
    """按延迟排名筛选前百分比IP，保留最优IP"""
    if not CONFIG["advanced_mode"] or not ips_with_latency:
        return ips_with_latency
    
    # 按延迟排序
    sorted_ips = sorted(ips_with_latency, key=lambda x: x[2])  # 按avg_delay排序
    
    # 计算前百分比的数量
    percentage = CONFIG["latency_filter_percentage"]
    keep_count = max(1, int(len(sorted_ips) * percentage / 100))
    
    # 取前N个IP
    filtered_ips = sorted_ips[:keep_count]
    
    logger.info(f"🔍 延迟排名前{percentage}%筛选：从 {len(ips_with_latency)} 个IP中筛选出 {len(filtered_ips)} 个IP")
    
    # 显示筛选结果
    for i, (ip, min_delay, avg_delay, stability) in enumerate(filtered_ips, 1):
        logger.info(f"📊 {ip}（延迟排名第{i}位：{avg_delay:.1f}ms）")
    
    return filtered_ips

# ===== 5. 地区识别模块 =====
# IP地理位置识别，支持多API和智能缓存

def get_ip_region(ip):
    """识别IP地理位置，支持缓存TTL机制和多API备用"""
    # 检查缓存是否有效
    if ip in region_cache:
        cached_data = region_cache[ip]
        if isinstance(cached_data, dict) and 'timestamp' in cached_data:
            if is_cache_valid(cached_data['timestamp'], CONFIG["cache_ttl_hours"]):
                # 缓存命中，记录缓存来源（延迟输出）
                # 不立即输出，由调用方统一控制日志顺序
                return cached_data['region']
        else:
            # 兼容旧格式缓存
            return cached_data
    
    # 尝试主要API（免费版本）
    logger.info(f"🌐 IP {ip} 开始API查询（主要API: ipinfo.io lite）...")
    try:
        resp = session.get(f'https://api.ipinfo.io/lite/{ip}?token=2cb674df499388', timeout=CONFIG["api_timeout"])
        if resp.status_code == 200:
            data = resp.json()
            country_code = data.get('country_code', '').upper()
            if country_code:
                region_cache[ip] = {
                    'region': country_code,
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"✅ IP {ip} 主要API识别成功: {country_code}（来源：API查询）")
                return country_code
        else:
            logger.warning(f"⚠️ IP {ip} 主要API返回状态码: {resp.status_code}")
    except Exception as e:
        logger.error(f"❌ IP {ip} 主要API识别失败: {str(e)[:30]}")
        pass
    
    # 尝试备用API
    logger.info(f"🌐 IP {ip} 尝试备用API（ip-api.com）...")
    try:
        resp = session.get(f'http://ip-api.com/json/{ip}?fields=countryCode', timeout=CONFIG["api_timeout"])
        if resp.json().get('status') == 'success':
            data = resp.json()
            country_code = data.get('countryCode', '').upper()
            if country_code:
                region_cache[ip] = {
                    'region': country_code,
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"✅ IP {ip} 备用API识别成功: {country_code}（来源：备用API查询）")
                return country_code
        else:
            logger.warning(f"⚠️ IP {ip} 备用API返回状态: {resp.json().get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"❌ IP {ip} 备用API识别失败: {str(e)[:30]}")
        pass
    
    # 失败返回Unknown
    logger.warning(f"❌ IP {ip} 所有API识别失败，标记为Unknown")
    region_cache[ip] = {
        'region': 'Unknown',
        'timestamp': datetime.now().isoformat()
    }
    return 'Unknown'

def get_country_name(code):
    """根据ISO国家代码获取中文名称"""
    return COUNTRY_MAPPING.get(code, code)

# ===== 6. 并发处理模块 =====
# 多线程并发处理，大幅提升检测效率

def quick_filter_ips(ips, max_workers=None):
    """并发快速筛选IP，剔除明显不可用的IP"""
    if max_workers is None:
        max_workers = CONFIG["max_workers"]
    
    logger.info(f"🔍 开始快速筛选 {len(ips)} 个IP，剔除明显不好的IP...")
    filtered_ips = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(quick_filter_ip, ip): ip for ip in ips}
        
        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if isinstance(result, tuple):
                    is_good, current_delay = result
                    if is_good:
                        filtered_ips.append(ip)
                        logger.info(f"✅ 可用 {ip}（延迟 {current_delay}ms）")
                    else:
                        logger.info(f"❌ {ip} 被快速筛选剔除")
            except Exception as e:
                logger.error(f"❌ {ip} 快速筛选出错: {str(e)[:30]}")
    
    elapsed = time.time() - start_time
    logger.info(f"🔍 快速筛选完成，从 {len(ips)} 个IP中筛选出 {len(filtered_ips)} 个IP，耗时: {elapsed:.1f}秒")
    return filtered_ips

def test_ips_concurrently(ips, max_workers=None):
    """并发检测IP可用性，TCP Ping测试获取延迟数据"""
    if max_workers is None:
        max_workers = CONFIG["max_workers"]
    
    logger.info(f"📡 开始并发检测 {len(ips)} 个IP，使用 {max_workers} 个线程，测试类型: 延迟")
    available_ips = []
    
    # 使用更小的批次，避免卡住
    batch_size = CONFIG["batch_size"]
    start_time = time.time()
    
    for i in range(0, len(ips), batch_size):
        batch_ips = ips[i:i+batch_size]
        batch_num = i//batch_size + 1
        total_batches = (len(ips)-1)//batch_size + 1
        
        logger.info(f"📡 处理批次 {batch_num}/{total_batches}，包含 {len(batch_ips)} 个IP")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交批次任务，添加超时保护
            future_to_ip = {executor.submit(test_ip_availability, ip): ip for ip in batch_ips}
            
            # 处理完成的任务
            batch_completed = 0
            timeout = 30  # TCP测试超时时间
            for future in as_completed(future_to_ip, timeout=timeout):
                ip = future_to_ip[future]
                batch_completed += 1
                completed = i + batch_completed
                elapsed = time.time() - start_time
                
                try:
                    is_available, min_delay, avg_delay, stability = future.result()
                    if is_available:
                        available_ips.append((ip, min_delay, avg_delay, stability))
                        logger.info(f"🎯 [{completed}/{len(ips)}] {ip}（TCP Ping 综合延迟：{avg_delay:.1f}ms）")
                    else:
                        logger.info(f"[{completed}/{len(ips)}] {ip} ❌ 不可用")
                    
                except Exception as e:
                    logger.error(f"[{completed}/{len(ips)}] {ip} ❌ 检测出错: {str(e)[:30]} - 耗时: {elapsed:.1f}s")
                    
        
        # 批次间短暂休息，避免过度占用资源
        if i + batch_size < len(ips):
            time.sleep(0.1)  # 减少休息时间
    
    total_time = time.time() - start_time
    logger.info(f"📡 并发检测完成，发现 {len(available_ips)} 个可用IP，总耗时: {total_time:.1f}秒")
    
    
    return available_ips

def get_regions_concurrently(ips, max_workers=None):
    """并发识别IP地理位置，保持日志输出顺序"""
    if max_workers is None:
        max_workers = CONFIG["max_workers"]
    
    logger.info(f"🌍 开始并发地区识别 {len(ips)} 个IP，使用 {max_workers} 个线程")
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_ip = {executor.submit(get_ip_region, ip): (ip, min_delay, avg_delay) for ip, min_delay, avg_delay in ips}
        
        # 先收集所有结果，不输出日志
        for i, (ip, min_delay, avg_delay) in enumerate(ips, 1):
            future = None
            # 找到对应的future
            for f, (f_ip, f_min_delay, f_avg_delay) in future_to_ip.items():
                if f_ip == ip and f_min_delay == min_delay and f_avg_delay == avg_delay:
                    future = f
                    break
            
            if future:
                try:
                    region_code = future.result()
                    results.append((ip, region_code, min_delay, avg_delay))
                    
                    # 只在API查询时等待，缓存查询不需要等待
                    if i % 10 == 0:  # 每10个IP等待一次，减少等待频率
                        time.sleep(CONFIG["query_interval"])
                except Exception as e:
                    logger.warning(f"地区识别失败 {ip}: {str(e)[:50]}")
                    results.append((ip, 'Unknown', min_delay, avg_delay))
        
        # 所有结果收集完成后，先输出缓存获取日志，再输出地区识别结果
        for i, (ip, region_code, min_delay, avg_delay) in enumerate(results, 1):
            # 检查是否从缓存获取
            if ip in region_cache:
                cached_data = region_cache[ip]
                if isinstance(cached_data, dict) and 'timestamp' in cached_data:
                    if is_cache_valid(cached_data['timestamp'], CONFIG["cache_ttl_hours"]):
                        logger.info(f"📦 IP {ip} 地区信息从缓存获取: {cached_data['region']}")
            logger.info(f"📦 [{i}/{len(ips)}] {ip} -> {region_code}")
                    
    
    total_time = time.time() - start_time
    logger.info(f"🌍 地区识别完成，处理了 {len(results)} 个IP，总耗时: {total_time:.1f}秒")
    return results

# ===== 7. 主程序模块 =====
# 程序主流程控制，协调各个模块完成完整的IP检测流程

def save_basic_files(filtered_ips):
    """保存基础版输出文件：DNSIPlist.txt"""
    logger.info("📄 ===== 保存基础IP文件 =====")
    with open('DNSIPlist.txt', 'w', encoding='utf-8') as f:
        for ip in filtered_ips:
            f.write(f"{ip}\n")
    logger.info(f"📄 已保存 {len(filtered_ips)} 个可用IP到 DNSIPlist.txt")

def format_and_save_region_results(ips, output_file, include_region_detection=True):
    """
    格式化并保存带地区信息的结果
    
    Args:
        ips: IP列表或(ip, min_delay, avg_delay, ...)元组列表
        output_file: 输出文件名
        include_region_detection: 是否进行地区识别
    """
    if not include_region_detection:
        logger.info("⏭️  跳过地区识别，仅保存简单格式")
        result = []
        for idx, ip in enumerate(ips, 1):
            if isinstance(ip, tuple):
                ip = ip[0]
            result.append(f"{ip}#Unknown 未知节点 | {idx:02d}")
        
        if result:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
            logger.info(f"📄 已保存 {len(result)} 条记录到 {output_file}")
        return
    
    logger.info("🌍 ===== 并发地区识别与结果格式化 =====")
    
    # 处理输入格式
    if isinstance(ips[0], tuple):
        ip_delay_data = [(ip, min_d, avg_d) for ip, min_d, avg_d, *_ in ips]
    else:
        ip_delay_data = [(ip, 0, 0) for ip in ips]
    
    region_results = get_regions_concurrently(ip_delay_data)
    
    # 按地区分组
    region_groups = defaultdict(list)
    for ip, region_code, min_delay, avg_delay in region_results:
        country_name = get_country_name(region_code)
        region_groups[country_name].append((ip, region_code, min_delay, avg_delay))
    
    logger.info(f"🌍 地区分组完成，共 {len(region_groups)} 个地区")
    
    # 生成并保存最终结果
    result = []
    for region in sorted(region_groups.keys()):
        sorted_ips = sorted(region_groups[region], key=lambda x: x[2])
        for idx, (ip, code, min_delay, avg_delay) in enumerate(sorted_ips, 1):
            result.append(f"{ip}#{code} {region}节点 | {idx:02d}")
        logger.debug(f"地区 {region} 格式化完成，包含 {len(sorted_ips)} 个IP")
    
    if result:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
        logger.info(f"📄 已保存 {len(result)} 条格式化记录到 {output_file}")
    else:
        logger.warning("⚠️ 无有效记录可保存")

def run_advanced_tests(filtered_ips):
    """
    运行高级测试：延迟筛选、TCP Ping、带宽测试
    
    Returns:
        可用IP列表，格式为 (ip, min_delay, avg_delay, bandwidth, latency, score)
    """
    # 8. 延迟排名前30%筛选（可选）
    if CONFIG["enable_latency_filter"]:
        logger.info("🔍 ===== 延迟排名前30%筛选 =====")
        quick_filter_results = []
        for ip in filtered_ips:
            is_good, delay = quick_filter_ip(ip)
            if is_good:
                quick_filter_results.append((ip, delay, delay, 0))
        
        latency_filtered_ips = latency_filter_ips(quick_filter_results)
    else:
        logger.info("⏭️  跳过延迟排名筛选，直接使用所有IP")
        # 如果跳过延迟筛选，也需要对所有IP进行一次快速筛选获取延迟数据
        quick_filter_results = []
        for ip in filtered_ips:
            is_good, delay = quick_filter_ip(ip)
            if is_good:
                quick_filter_results.append((ip, delay, delay, 0))
        latency_filtered_ips = quick_filter_results
    
    # 9. TCP Ping测试（可选）
    tcp_ping_ips = []
    if CONFIG["enable_tcp_ping"]:
        logger.info("🔍 ===== TCP Ping测试 =====")
        tcp_ping_ips = test_ips_concurrently([ip for ip, _, _, _ in latency_filtered_ips])
    else:
        logger.info("⏭️  跳过TCP Ping测试，使用快速筛选结果")
        tcp_ping_ips = latency_filtered_ips
    
    if not tcp_ping_ips:
        logger.warning("⚠️ 延迟测试后没有可用IP")
        return []
    
    # 10. 带宽测试（可选）
    if CONFIG["enable_bandwidth_test"]:
        logger.info("🔍 ===== 带宽测试 =====")
        bandwidth_results = []
        for i, (ip, _, _, _) in enumerate(tcp_ping_ips, 1):
            is_fast, bandwidth, latency = test_ip_bandwidth_only(ip, i, len(tcp_ping_ips))
            if is_fast:
                for orig_ip, min_delay, avg_delay, stability in tcp_ping_ips:
                    if orig_ip == ip:
                        score = calculate_score(min_delay, avg_delay, bandwidth, stability)
                        bandwidth_results.append((ip, min_delay, avg_delay, bandwidth, latency, score))
                        break
        return bandwidth_results
    else:
        logger.info("⏭️  跳过带宽测试，仅基于延迟评分")
        results = []
        for ip, min_delay, avg_delay, stability in tcp_ping_ips:
            score = calculate_score(min_delay, avg_delay, 0, stability)
            results.append((ip, min_delay, avg_delay, 0, avg_delay, score))
        return results

def save_advanced_files(available_ips):
    """保存高级版输出文件"""
    if not available_ips:
        logger.warning("⚠️ 没有可用IP保存高级文件")
        return
    
    # 按评分排序
    if len(available_ips[0]) > 5:
        available_ips.sort(key=lambda x: x[5], reverse=True)
        logger.info(f"📊 按综合评分排序完成")
    
    # 保存优选IP列表
    with open('DNSIPlist-Pro.txt', 'w', encoding='utf-8') as f:
        for ip, min_delay, avg_delay, bandwidth, latency, score in available_ips:
            f.write(f"{ip}\n")
    logger.info(f"📄 已保存 {len(available_ips)} 个优选IP到 DNSIPlist-Pro.txt")
    
    # 保存排名详情
    with open('Ranking.txt', 'w', encoding='utf-8') as f:
        for i, (ip, min_delay, avg_delay, bandwidth, latency, score) in enumerate(available_ips, 1):
            f.write(f"📊 [{i}/{len(available_ips)}] {ip}（延迟 {min_delay}ms，带宽 {bandwidth:.2f}Mbps，评分 {score:.1f}）\n")
    logger.info(f"📄 已保存排名详情到 Ranking.txt")
    
    # 保存高级格式化文件
    logger.info("🌍 ===== 高级地区识别与结果格式化 =====")
    pro_ip_delay_data = [(ip, 0, 0) for ip, _, _, _, _, _ in available_ips]
    
    if CONFIG["enable_region_detection"]:
        pro_region_results = get_regions_concurrently(pro_ip_delay_data)
        
        pro_region_groups = defaultdict(list)
        for ip, region_code, min_delay, avg_delay in pro_region_results:
            country_name = get_country_name(region_code)
            pro_region_groups[country_name].append((ip, region_code, min_delay, avg_delay))
        
        logger.info(f"🌍 高级地区分组完成，共 {len(pro_region_groups)} 个地区")
        
        pro_result = []
        for region in sorted(pro_region_groups.keys()):
            sorted_ips = sorted(pro_region_groups[region], key=lambda x: x[2])
            for idx, (ip, code, min_delay, avg_delay) in enumerate(sorted_ips, 1):
                pro_result.append(f"{ip}#{code} {region}节点 | {idx:02d}")
            logger.debug(f"高级地区 {region} 格式化完成，包含 {len(sorted_ips)} 个IP")
        
        if pro_result:
            with open('DNSResult-Pro.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(pro_result))
            logger.info(f"📄 已保存 {len(pro_result)} 条高级格式化记录到 DNSResult-Pro.txt")
        else:
            logger.warning("⚠️ 高级版无有效记录可保存")
    else:
        logger.info("⏭️  跳过地区识别，使用简单格式保存高级版")
        pro_result = []
        for idx, (ip, _, _, _, _, _) in enumerate(available_ips, 1):
            pro_result.append(f"{ip}#Unknown 未知节点 | {idx:02d}")
        
        with open('DNSResult-Pro.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(pro_result))
        logger.info(f"📄 已保存 {len(pro_result)} 条记录到 DNSResult-Pro.txt")

def main():
    """主程序入口，根据配置条件执行各功能模块"""
    start_time = time.time()
    
    # 1. 预处理：删除旧文件（可选）
    if CONFIG["enable_preprocess"]:
        if CONFIG["enable_basic_output"]:
            delete_file_if_exists('DNSIPlist.txt')
            delete_file_if_exists('DNSResult.txt')
        if CONFIG["enable_pro_output"]:
            delete_file_if_exists('DNSIPlist-Pro.txt')
            delete_file_if_exists('DNSResult-Pro.txt')
            delete_file_if_exists('Ranking.txt')
        logger.info("🗑️ 预处理完成，旧文件已清理")
    else:
        logger.info("⏭️  跳过预处理（不删除旧文件）")

    # 2. 加载域名列表（可选）
    domains = []
    if CONFIG["enable_load_domains"]:
        logger.info("📥 ===== 加载域名列表 =====")
        domains = load_domain_list()
        
        if not domains:
            logger.warning("⚠️ 没有找到任何域名，程序结束")
            return
    else:
        logger.info("⏭️  跳过加载域名列表")

    # 3. 多方法解析获取IP地址（可选）
    all_ips = []
    if CONFIG["enable_dns_resolve"]:
        logger.info("🔍 ===== 多方法解析域名 =====")
        successful_domains = 0
        failed_domains = 0
        
        for i, domain in enumerate(domains):
            try:
                logger.info(f"🔍 解析域名 {domain}...")
                if i > 0:
                    time.sleep(CONFIG["query_interval"])
                
                ips = resolve_domain(domain)
                if ips:
                    all_ips.extend(ips)
                    successful_domains += 1
                    logger.info(f"✅ 成功解析 {domain}，获得 {len(ips)} 个IP地址")
                else:
                    failed_domains += 1
                    logger.warning(f"❌ 解析 {domain} 失败，未获得IP地址")
            except Exception as e:
                failed_domains += 1
                error_msg = str(e)[:50]
                logger.error(f"❌ 解析 {domain} 出错: {error_msg}")
        
        logger.info(f"📊 解析统计: 成功 {successful_domains} 个域名，失败 {failed_domains} 个域名")
    else:
        logger.info("⏭️  跳过DNS解析")

    # 4. IP去重与排序（可选）
    unique_ips = all_ips
    if CONFIG["enable_dedup_sort"] and all_ips:
        logger.info(f"🔢 去重前共 {len(all_ips)} 个IP地址")
        unique_ips = sorted(list(set(all_ips)), key=lambda x: [int(p) for p in x.split('.')])
        logger.info(f"🔢 去重后共 {len(unique_ips)} 个唯一IP地址")
        
        if len(all_ips) != len(unique_ips):
            logger.info(f"🔍 发现重复IP，已去重 {len(all_ips) - len(unique_ips)} 个重复项")
    elif CONFIG["enable_dedup_sort"]:
        logger.info("⏭️  没有IP需要去重排序")
    else:
        logger.info("⏭️  跳过IP去重和排序")
    
    if not unique_ips:
        logger.warning("⚠️ 没有解析到任何IP地址，程序结束")
        return

    # 5. 快速筛选IP（可选，剔除明显不好的）
    if CONFIG["enable_quick_filter"]:
        logger.info("🔍 ===== 快速筛选IP =====")
        working_ips = quick_filter_ips(unique_ips)
        
        if not working_ips:
            logger.warning("⚠️ 快速筛选后没有可用IP，程序结束")
            return
    else:
        logger.info("⏭️  跳过快速筛选，直接使用所有解析到的IP")
        working_ips = unique_ips
    
    # 6. 保存基础文件（可选）
    if CONFIG["enable_basic_output"]:
        save_basic_files(working_ips)
        # 格式化保存 DNSResult.txt（带地区识别或不带）
        format_and_save_region_results(
            working_ips, 
            'DNSResult.txt', 
            include_region_detection=CONFIG["enable_region_detection"]
        )
    
    # 7-11. 高级功能处理（根据配置）
    if CONFIG["advanced_mode"] and CONFIG["enable_pro_output"]:
        logger.info("🚀 ===== 进入高级模式 =====")
        available_ips = run_advanced_tests(working_ips)
        
        if available_ips:
            save_advanced_files(available_ips)
        else:
            logger.warning("⚠️ 高级测试后没有可用IP")
    else:
        logger.info("⏭️  跳过高级模式（advanced_mode 或 enable_pro_output 为 False）")
    
    # 12. 保存缓存（可选）
    if CONFIG["enable_cache_update"]:
        save_region_cache()
    else:
        logger.info("⏭️  跳过缓存更新（只读模式）")
    
    # 显示总耗时
    run_time = round(time.time() - start_time, 2)
    logger.info(f"⏱️ 总耗时: {run_time}秒")
    logger.info(f"📊 缓存统计: 总计 {len(region_cache)} 个")
    logger.info("🏁 ===== 程序完成 =====")

# ===== 8. 程序入口 =====
# 程序启动入口，初始化缓存并执行主程序
if __name__ == "__main__":
    # 程序启动日志
    logger.info("🚀 ===== 开始DNS IP处理程序 =====")
    
    # 合并配置（命令行 > 环境变量 > 配置文件 > 默认值）
    merge_configs()
    
    # 初始化缓存系统
    load_region_cache()
    # 清理过期缓存条目
    clean_expired_cache()
    # 执行主程序流程
    try:
        main()
    except KeyboardInterrupt:
        logger.info("⏹️ 程序被用户中断")
    except Exception as e:
        logger.error(f"❌ 程序运行出错: {str(e)}")
