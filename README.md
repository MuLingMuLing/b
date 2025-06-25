# HeavenlyEye - 天堂之眼 👁️

**Made in Heaven!** ✨

## 项目简介

HeavenlyEye 是一个强大的 Windows 系统信息收集工具，能够全面扫描并展示您的计算机硬件、软件、网络和安全配置等详细信息。它就像上帝之眼一样，洞察您系统的每一个细节。

## 功能特性

- 🔍 **全面系统扫描**：获取操作系统、硬件配置、网络设置等全方位信息
- ⚡ **实时性能监控**：显示 CPU、内存、磁盘等实时使用情况
- 🔒 **安全审计**：检查防火墙状态、杀毒软件、BitLocker 等安全配置
- 🖥️ **硬件详情**：包括 CPU、GPU、内存、磁盘等详细规格
- 🌐 **网络分析**：显示所有网络适配器配置和连接信息
- 👤 **用户环境**：收集用户账户、环境变量和系统设置
- 🐍 **Python 环境**：显示当前 Python 运行环境详细信息

## 使用说明

1. 确保系统已安装 Python 3.x
2. 安装必要依赖：
   ```
   pip install wmi psutil 
   ```
3. 运行脚本：
   ```
   python main.py
   ```

> 注意：部分功能需要管理员权限才能获取完整信息

## 技术栈

- Python 3
- WMI (Windows Management Instrumentation)
- psutil 库
- ctypes (用于权限提升)

## 开源协议

本项目采用 [The Unlicense](https://unlicense.org/) 开源协议：

```
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.
```

## 贡献指南

欢迎任何形式的贡献！您可以通过以下方式参与：

1. 提交 Issue 报告问题或建议
2. Fork 项目并提交 Pull Request
3. 帮助完善文档或翻译

## 未来计划

- [ ] 添加获取公网IP
- [ ] 添加获取微信、QQ等社交媒体帐号

## 免责声明

本工具仅用于合法系统审计和信息收集目的。开发者不对任何滥用行为负责。

---

Made with ❤️ by MuLing | Inspired by Heaven's Door
