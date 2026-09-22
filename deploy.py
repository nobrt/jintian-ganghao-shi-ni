#!/usr/bin/env python3
"""一键部署：上传网站文件到腾讯云 COS 并验证线上。

用法：python3 deploy.py [SecretId] [SecretKey]
      不带参数时交互式输入密钥（输入不回显，用完即弃）。
密钥每次部署前在腾讯云控制台新建：https://console.cloud.tencent.com/cam/capi
部署完成后请删除该密钥。
"""

import os
import sys
import time
import urllib.request
from getpass import getpass

BASE_DIR = '/Users/lamegliogioventu/Claude Code/jintian-ganghao-shi-ni'
REGION = 'ap-guangzhou'
BUCKET = 'jintian-ganghao-shi-ni-1492583830'
SITE = f'https://{BUCKET}.cos-website.{REGION}.myqcloud.com'

FILES = ['index.html', 'styles.css', 'script.js', 'README.md']
FILES += [f'assets/{n}.jpg' for n in '12345']
FILES += ['assets/ambient.mp3']


def load_credentials():
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    print('请粘贴腾讯云 API 密钥（https://console.cloud.tencent.com/cam/capi 新建）')
    secret_id = input('SecretId: ').strip()
    secret_key = getpass('SecretKey: ').strip()
    if not secret_id or not secret_key:
        print('[错误] 密钥不能为空')
        sys.exit(1)
    return secret_id, secret_key


def main():
    secret_id, secret_key = load_credentials()
    from qcloud_cos import CosConfig, CosS3Client
    client = CosS3Client(CosConfig(
        Region=REGION, SecretId=secret_id, SecretKey=secret_key))

    print('=== 1/3 上传文件 ===')
    for name in FILES:
        local = os.path.join(BASE_DIR, name)
        if not os.path.exists(local):
            print(f'  [跳过] 本地缺失 {name}')
            continue
        with open(local, 'rb') as fp:
            client.put_object(Bucket=BUCKET, Body=fp, Key=name)
        print(f'  [完成] {name}')

    print('=== 2/3 清理云端多余文件 ===')
    kept = set(FILES)
    resp = client.list_objects(Bucket=BUCKET)
    for obj in resp.get('Contents', []):
        key = obj['Key']
        if key not in kept:
            client.delete_object(Bucket=BUCKET, Key=key)
            print(f'  [删除] {key}')
    if not resp.get('Contents'):
        print('  （云端无多余文件）')

    print('=== 3/3 验证线上 ===')
    time.sleep(2)
    failed = []
    for name in FILES:
        if not os.path.exists(os.path.join(BASE_DIR, name)):
            continue
        url = f'{SITE}/{name}'
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                status = r.status
        except Exception as e:
            status = f'失败({e})'
        mark = '✓' if status == 200 else '✗'
        print(f'  [{mark}] {status}  /{name}')
        if status != 200:
            failed.append(name)

    print()
    if failed:
        print(f'部署完成，但有 {len(failed)} 个文件异常：{failed}')
        sys.exit(1)
    print('全部成功！线上地址：')
    print(SITE)


if __name__ == '__main__':
    main()
