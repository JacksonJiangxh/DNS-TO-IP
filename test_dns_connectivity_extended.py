#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展的DNS连通性测试脚本 - 包含更多DNS服务器
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

DNS_SERVERS = {
    '223.5.5.5': '阿里云-DNS',
    '223.6.6.6': '阿里云-DNS',
    '223.5.5.6': '阿里云-DNS',
    '180.76.76.76': '百度-DNS',
    '119.29.29.29': '腾讯-DNS',
    '182.254.116.116': '腾讯-DNS',
    '183.60.83.19': '腾讯-DNS',
    '183.60.82.98': '腾讯-DNS',
    '114.114.114.114': '114-DNS',
    '114.114.115.115': '114-DNS',
    '1.2.4.8': 'CNNIC-DNS',
    '210.2.4.8': 'CNNIC-DNS',
    '101.6.6.6': 'CNNIC-DNS',
    '117.50.11.11': 'OneDNS',
    '52.80.66.66': 'OneDNS',
    '101.226.4.6': '360-DNS(电信/移动)',
    '218.30.118.6': '360-DNS(电信/移动)',
    '123.125.81.6': '360-DNS(联通)',
    '140.207.198.6': '360-DNS(联通)',
    '4.2.2.1': '微软-DNS',
    '4.2.2.2': '微软-DNS',
    '122.112.208.1': '华为云-DNS',
    '139.9.23.90': '华为云-DNS',
    '202.38.93.153': '中科大-DNS',
    '202.141.162.123': '清华-DNS',
    '202.112.20.131': '北邮-DNS',
    '218.2.2.2': '中国电信-全国',
    '218.4.4.4': '中国电信-全国',
    '101.226.4.6': '中国电信-全国',
    '218.30.118.6': '中国电信-全国',
    '219.141.136.10': '中国电信-北京',
    '219.141.140.10': '中国电信-北京',
    '202.96.209.133': '中国电信-上海',
    '202.96.209.5': '中国电信-上海',
    '116.228.111.118': '中国电信-上海',
    '180.168.255.118': '中国电信-上海',
    '202.96.128.86': '中国电信-广东',
    '202.96.128.166': '中国电信-广东',
    '202.96.134.133': '中国电信-广东',
    '202.96.128.68': '中国电信-广东',
    '61.139.2.69': '中国电信-四川',
    '218.6.200.139': '中国电信-四川',
    '202.103.24.68': '中国电信-湖北',
    '202.103.0.68': '中国电信-湖北',
    '202.103.0.117': '中国电信-湖北',
    '202.103.0.118': '中国电信-湖北',
    '219.146.1.66': '中国电信-山东',
    '219.147.1.66': '中国电信-山东',
    '218.85.152.99': '中国电信-福建',
    '218.85.157.99': '中国电信-福建',
    '202.101.172.35': '中国电信-浙江',
    '60.191.244.5': '中国电信-浙江',
    '61.153.81.75': '中国电信-浙江',
    '222.88.88.88': '中国电信-河南',
    '222.85.85.85': '中国电信-河南',
    '218.30.19.40': '中国电信-陕西',
    '61.134.1.4': '中国电信-陕西',
    '202.101.224.69': '中国电信-江西',
    '202.101.226.68': '中国电信-江西',
    '61.132.163.68': '中国电信-安徽',
    '202.102.213.68': '中国电信-安徽',
    '202.100.64.68': '中国电信-甘肃',
    '61.178.0.93': '中国电信-甘肃',
    '202.103.225.68': '中国电信-广西',
    '202.103.224.68': '中国电信-广西',
    '202.98.192.67': '中国电信-贵州',
    '202.98.198.167': '中国电信-贵州',
    '59.51.78.211': '中国电信-湖南',
    '59.51.78.210': '中国电信-湖南',
    '222.246.129.80': '中国电信-湖南',
    '219.147.198.230': '中国电信-黑龙江',
    '219.147.198.242': '中国电信-黑龙江',
    '61.128.192.68': '中国电信-重庆',
    '61.128.128.68': '中国电信-重庆',
    '222.172.200.68': '中国电信-云南',
    '61.166.150.123': '中国电信-云南',
    '219.150.32.132': '中国电信-天津',
    '219.146.0.132': '中国电信-天津',
    '123.123.123.123': '中国联通-全国',
    '123.123.123.124': '中国联通-全国',
    '123.125.81.6': '中国联通-全国',
    '140.207.198.6': '中国联通-全国',
    '202.106.196.115': '中国联通-北京',
    '202.106.46.151': '中国联通-北京',
    '202.106.0.20': '中国联通-北京',
    '202.106.195.68': '中国联通-北京',
    '210.22.70.3': '中国联通-上海',
    '210.22.84.3': '中国联通-上海',
    '210.22.70.225': '中国联通-上海',
    '210.21.196.6': '中国联通-广东',
    '210.21.4.130': '中国联通-广东',
    '221.5.88.88': '中国联通-广东',
    '119.6.6.6': '中国联通-四川',
    '124.161.87.155': '中国联通-四川',
    '221.6.4.66': '中国联通-江苏',
    '221.6.4.67': '中国联通-江苏',
    '221.12.1.227': '中国联通-浙江',
    '221.12.33.227': '中国联通-浙江',
    '218.104.128.106': '中国联通-福建',
    '218.104.128.107': '中国联通-福建',
    '219.146.1.66': '中国联通-山东',
    '219.147.1.66': '中国联通-山东',
    '202.102.224.68': '中国联通-河南',
    '202.102.227.68': '中国联通-河南',
    '202.103.24.68': '中国联通-湖北',
    '202.103.44.150': '中国联通-湖北',
    '58.20.127.238': '中国联通-湖南',
    '58.20.57.31': '中国联通-湖南',
    '202.96.69.38': '中国联通-辽宁',
    '202.96.64.68': '中国联通-辽宁',
    '221.11.1.67': '中国联通-陕西',
    '221.11.1.68': '中国联通-陕西',
    '202.99.160.68': '中国联通-河北',
    '202.99.166.4': '中国联通-河北',
    '202.97.224.69': '中国联通-黑龙江',
    '202.97.224.68': '中国联通-黑龙江',
    '221.5.203.98': '中国联通-重庆',
    '221.7.92.98': '中国联通-重庆',
    '211.138.180.2': '中国移动-全国',
    '211.138.180.3': '中国移动-全国',
    '211.136.28.228': '中国移动-北京',
    '211.136.28.234': '中国移动-北京',
    '211.136.112.50': '中国移动-上海',
    '211.136.150.66': '中国移动-上海',
    '211.136.192.6': '中国移动-广东',
    '211.136.192.7': '中国移动-广东',
    '221.131.143.69': '中国移动-江苏',
    '221.131.141.135': '中国移动-江苏',
    '112.4.0.55': '中国移动-江苏',
    '211.140.13.188': '中国移动-浙江',
    '211.140.188.188': '中国移动-浙江',
    '211.137.82.4': '中国移动-四川',
    '221.176.88.95': '中国移动-四川',
    '211.138.151.161': '中国移动-福建',
    '211.138.156.66': '中国移动-福建',
    '211.138.91.1': '中国移动-山东',
    '218.201.96.130': '中国移动-山东',
    '211.137.191.26': '中国移动-山东',
    '211.138.24.71': '中国移动-河南',
    '211.138.31.145': '中国移动-河南',
    '211.137.58.20': '中国移动-湖北',
    '211.137.64.163': '中国移动-湖北',
    '211.142.210.100': '中国移动-湖南',
    '211.142.210.101': '中国移动-湖南',
    '211.137.32.178': '中国移动-辽宁',
    '218.25.90.52': '中国移动-辽宁',
    '211.137.130.19': '中国移动-陕西',
    '211.137.130.3': '中国移动-陕西',
    '211.138.13.66': '中国移动-河北',
    '221.192.136.330': '中国移动-河北',
    '211.138.106.3': '中国移动-山西',
    '211.138.106.7': '中国移动-山西',
    '211.141.90.68': '中国移动-江西',
    '211.141.85.68': '中国移动-江西',
    '218.201.4.3': '中国移动-重庆',
    '211.137.241.35': '中国移动-黑龙江',
    '218.203.160.194': '中国移动-甘肃',
    '218.203.160.195': '中国移动-甘肃',
    '211.139.5.30': '中国移动-云南',
    '8.8.8.8': 'Google-DNS',
    '8.8.4.4': 'Google-DNS',
    '1.1.1.1': 'Cloudflare-DNS',
    '1.0.0.1': 'Cloudflare-DNS',
    '1.1.1.2': 'Cloudflare-DNS(安全)',
    '1.1.1.3': 'Cloudflare-DNS(家庭)',
    '9.9.9.9': 'Quad9-DNS',
    '149.112.112.112': 'Quad9-DNS',
    '9.9.9.10': 'Quad9-DNS(无过滤)',
    '208.67.222.222': 'OpenDNS',
    '208.67.220.220': 'OpenDNS',
    '208.67.222.123': 'OpenDNS(家庭安全)',
    '208.67.220.123': 'OpenDNS(家庭安全)',
    '64.6.64.6': 'Verisign-DNS',
    '64.6.65.6': 'Verisign-DNS',
    '209.244.0.3': 'Level3-DNS',
    '209.244.0.4': 'Level3-DNS',
    '156.154.70.1': 'Neustar-DNS',
    '156.154.71.1': 'Neustar-DNS',
    '8.26.56.26': 'Comodo-DNS',
    '8.20.247.20': 'Comodo-DNS',
    '77.88.8.8': 'Yandex-DNS',
    '77.88.8.1': 'Yandex-DNS',
    '77.88.8.88': 'Yandex-DNS(安全)',
    '76.76.19.19': 'Alternate-DNS',
    '76.223.122.150': 'Alternate-DNS',
    '185.222.222.222': 'DNS.SB',
    '185.184.222.222': 'DNS.SB',
    '94.140.14.14': 'AdGuard-DNS',
    '94.140.15.15': 'AdGuard-DNS',
    '185.228.168.9': 'CleanBrowsing-DNS',
    '185.228.169.9': 'CleanBrowsing-DNS',
    '168.95.1.1': '中华电信-DNS',
    '168.95.192.1': '中华电信-DNS',
    '203.80.96.10': '香港宽频-DNS',
    '203.80.96.9': '香港宽频-DNS',
    '168.126.63.1': '韩国KT-DNS',
    '168.126.63.2': '韩国KT-DNS',
    '203.112.2.4': '新加坡SingTel',
    '203.112.2.5': '新加坡SingTel',
    '202.44.8.34': '泰国CAT',
    '202.44.8.35': '泰国CAT',
}

TEST_DOMAIN = 'cloudflare.com'
TIMEOUT = 3
MAX_WORKERS = 20


def test_dns(dns_server, dns_name):
    """测试单个DNS服务器"""
    result = {
        'server': dns_server,
        'name': dns_name,
        'available': False,
        'latency': None,
        'error': None
    }
    
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = TIMEOUT
        resolver.lifetime = TIMEOUT
        
        query_start = time.time()
        answers = resolver.resolve(TEST_DOMAIN, 'A')
        latency = (time.time() - query_start) * 1000
        
        if answers:
            result['available'] = True
            result['latency'] = round(latency, 1)
        else:
            result['error'] = '无响应数据'
            
    except Exception as e:
        result['error'] = str(e)[:50]
    
    return result


def main():
    total = len(DNS_SERVERS)
    print("=" * 80)
    print(f"DNS连通性测试 - 共 {total} 个DNS服务器")
    print(f"测试域名: {TEST_DOMAIN} | 超时: {TIMEOUT}s | 并发: {MAX_WORKERS}")
    print("=" * 80)
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_dns = {
            executor.submit(test_dns, server, name): (server, name)
            for server, name in DNS_SERVERS.items()
        }
        
        for future in as_completed(future_to_dns):
            result = future.result()
            results.append(result)
            
            status = "✅" if result['available'] else "❌"
            latency = f"{result['latency']}ms" if result['latency'] else "N/A"
            error = f" | 错误: {result['error']}" if not result['available'] else ""
            print(f"{status} {result['server']:18s} | {result['name']:20s} | 延迟: {latency}{error}")
    
    available = [r for r in results if r['available']]
    unavailable = [r for r in results if not r['available']]
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print(f"测试完成！总耗时: {total_time:.1f}秒")
    print(f"✅ 可用: {len(available)}/{total} ({len(available)/total*100:.1f}%)")
    print(f"❌ 不可用: {len(unavailable)}/{total} ({len(unavailable)/total*100:.1f}%)")
    print("=" * 80)
    
    if available:
        print("\n📊 可用DNS服务器 (按延迟排序, Top 50):")
        available_sorted = sorted(available, key=lambda x: x['latency'] if x['latency'] else 9999)
        for i, r in enumerate(available_sorted[:50], 1):
            latency = f"{r['latency']}ms" if r['latency'] else "N/A"
            print(f"  [{i:3d}] {r['server']:18s} | {r['name']:20s} | {latency}")
        
        if len(available_sorted) > 50:
            print(f"  ... 还有 {len(available_sorted) - 50} 个可用DNS")
    
    if unavailable:
        print(f"\n❌ 不可用的DNS服务器 ({len(unavailable)}个):")
        for r in unavailable:
            print(f"   {r['server']:18s} | {r['name']:20s} | {r['error']}")
    
    if available:
        print("\n" + "=" * 80)
        print("💡 建议的DNS配置（按延迟排序，只保留可用的）:")
        print("=" * 80)
        print('"dns_servers": {')
        for r in available_sorted:
            print(f"    '{r['server']}': '{r['name']}',")
        print('},')
        
        print("\n📋 精简版建议（每类保留2-3个最快的）:")
        print("=" * 80)
        
        categories = {}
        for r in available_sorted:
            name = r['name']
            if '阿里云' in name:
                cat = '国内公共DNS'
            elif '腾讯' in name:
                cat = '国内公共DNS'
            elif '114' in name:
                cat = '国内公共DNS'
            elif '百度' in name:
                cat = '国内公共DNS'
            elif '360' in name:
                cat = '国内公共DNS'
            elif 'OneDNS' in name:
                cat = '国内公共DNS'
            elif 'CNNIC' in name:
                cat = '国内公共DNS'
            elif '中国电信' in name:
                cat = '电信DNS'
            elif '中国联通' in name:
                cat = '联通DNS'
            elif '中国移动' in name:
                cat = '移动DNS'
            elif 'Google' in name:
                cat = '国际DNS'
            elif 'Cloudflare' in name:
                cat = '国际DNS'
            elif 'Quad9' in name:
                cat = '国际DNS'
            elif 'OpenDNS' in name:
                cat = '国际DNS'
            elif '中华电信' in name:
                cat = '亚太DNS'
            elif '香港' in name:
                cat = '亚太DNS'
            elif '韩国' in name:
                cat = '亚太DNS'
            else:
                cat = '其他DNS'
            
            if cat not in categories:
                categories[cat] = []
            if len(categories[cat]) < 3:
                categories[cat].append(r)
        
        print('"dns_servers": {')
        for cat, servers in categories.items():
            print(f"    # {cat}")
            for r in servers:
                print(f"    '{r['server']}': '{r['name']}',")
        print('},')


if __name__ == '__main__':
    main()
