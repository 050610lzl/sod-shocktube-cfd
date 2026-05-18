#!/usr/bin/env python3
"""Sod Shock Tube CFD 项目版本号管理工具。

用法:
    python bump_version.py major     # 升级主版本号 (X+1.0.0)
    python bump_version.py minor     # 升级次版本号 (x.Y+1.0)
    python bump_version.py patch     # 升级修订版本号 (x.y.Z+1)
    python bump_version.py --tag     # 升级后自动创建 git tag
    python bump_version.py --dry-run # 仅预览，不实际修改

版本号规则遵循 Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH):
    MAJOR: 不兼容的 API 变更（修改函数签名、移除数值格式、改变输入/输出格式）
    MINOR: 向后兼容的新功能（新增数值格式、新增分析工具、新增 CLI 选项）
    PATCH: 向后兼容的 Bug 修复（修复数值错误、代码风格修复、性能优化）
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VERSION_FILE = PROJECT_ROOT / "VERSION"
PYPROJECT_FILE = PROJECT_ROOT / "pyproject.toml"
README_FILE = PROJECT_ROOT / "README.md"


def read_version():
    if not VERSION_FILE.exists():
        print(f"错误: 未找到 VERSION 文件 ({VERSION_FILE})")
        sys.exit(1)
    version = VERSION_FILE.read_text().strip()
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        print(f"错误: VERSION 文件格式无效: '{version}'，应为 MAJOR.MINOR.PATCH")
        sys.exit(1)
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    return major, minor, patch, version


def write_version(major, minor, patch, dry_run=False):
    new_version = f"{major}.{minor}.{patch}"
    if dry_run:
        print(f"[DRY-RUN] 将写入 VERSION 文件: {new_version}")
        return new_version
    with open(VERSION_FILE, 'w', newline='\n', encoding='utf-8') as f:
        f.write(new_version + "\n")
    print(f"VERSION 文件已更新: {new_version}")
    _sync_pyproject_toml(new_version, dry_run)
    _sync_readme_badge(new_version, dry_run)
    return new_version


def _sync_pyproject_toml(new_version, dry_run=False):
    if not PYPROJECT_FILE.exists():
        print(f"警告: 未找到 pyproject.toml ({PYPROJECT_FILE})，跳过同步")
        return
    content = PYPROJECT_FILE.read_text(encoding='utf-8')
    import re
    updated, count = re.subn(
        r'^version\s*=\s*"[^"]*"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    if count > 0:
        if dry_run:
            print(f"[DRY-RUN] 将更新 pyproject.toml 版本号: {new_version}")
        else:
            PYPROJECT_FILE.write_text(updated, encoding='utf-8')
            print(f"pyproject.toml 版本号已同步: {new_version}")
    else:
        print("警告: 未能在 pyproject.toml 中找到 version 字段")


def _sync_readme_badge(new_version, dry_run=False):
    if not README_FILE.exists():
        print(f"警告: 未找到 README.md ({README_FILE})，跳过同步")
        return
    content = README_FILE.read_text(encoding='utf-8')
    import re
    updated, count = re.subn(
        r'version-[\d.]+',
        f'version-{new_version}',
        content
    )
    if count > 0:
        if dry_run:
            print(f"[DRY-RUN] 将更新 README.md 版本徽章: {new_version}")
        else:
            README_FILE.write_text(updated, encoding='utf-8')
            print(f"README.md 版本徽章已同步: {new_version}")
    else:
        print("警告: 未能在 README.md 中找到版本徽章")


def create_git_tag(version, dry_run=False):
    tag_name = f"v{version}"
    tag_message = f"Release v{version}"
    if dry_run:
        print(f"[DRY-RUN] 将创建 git tag: {tag_name}")
        print(f"[DRY-RUN] Tag 消息: {tag_message}")
        return
    try:
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", tag_message],
            cwd=PROJECT_ROOT,
            check=True,
        )
        print(f"Git tag 已创建: {tag_name}")
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法创建 git tag: {e}")
        sys.exit(1)


def bump_version(level, tag=False, dry_run=False):
    major, minor, patch, old_version = read_version()

    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "patch":
        patch += 1
    else:
        print(f"错误: 未知的版本升级级别: '{level}'，可选: major, minor, patch")
        sys.exit(1)

    new_version = write_version(major, minor, patch, dry_run)

    if not dry_run:
        print(f"版本号已从 {old_version} 升级到 {new_version}")

    if tag:
        create_git_tag(new_version, dry_run)

    return new_version


def main():
    parser = argparse.ArgumentParser(
        description="Sod Shock Tube CFD 项目版本号管理工具 (SemVer 2.0.0)",
    )
    parser.add_argument(
        "level",
        nargs="?",
        choices=["major", "minor", "patch"],
        help="版本升级级别: major (X+1.0.0), minor (x.Y+1.0), patch (x.y.Z+1)",
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        help="升级后自动创建 git tag (如 v1.2.0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览即将执行的操作，不实际修改文件或创建 tag",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="仅显示当前版本号",
    )

    args = parser.parse_args()

    if args.show:
        _, _, _, version = read_version()
        print(version)
        return

    if not args.level:
        parser.print_help()
        print(f"\n当前版本: {read_version()[3]}")
        return

    bump_version(args.level, tag=args.tag, dry_run=args.dry_run)


if __name__ == "__main__":
    main()