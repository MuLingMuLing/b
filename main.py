#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

import time
import ctypes
import sys
import platform
import getpass
import socket
import os
import wmi
import datetime
import psutil
import locale


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, sys.argv[0], None, 1)


def get_system_info(w, start_time):
    os_info = w.Win32_OperatingSystem()[0]
    info = {
        "操作系统": os_info.Caption,
        "操作系统版本": os_info.Version,
        "操作系统架构": os_info.OSArchitecture,
        "安装日期": os_info.InstallDate.split(".")[0],
        "系统启动时间": os_info.LastBootUpTime.split(".")[0],
        "系统运行时长": str(datetime.timedelta(seconds=int(time.time() - start_time))),
        "主机名": socket.gethostname(),
        "域名": socket.getfqdn(),
        "当前工作目录": os.getcwd(),
        "系统语言": os_info.MUILanguages[0] if hasattr(os_info, "MUILanguages") and os_info.MUILanguages else "✘ 未获取",
        "系统目录": os_info.SystemDirectory,
        "系统驱动器": os_info.SystemDrive,
        "系统制造商": os_info.Manufacturer if hasattr(os_info, "Manufacturer") else "✘ 未获取",
        "系统型号": os_info.BuildType if hasattr(os_info, "BuildType") else "✘ 未获取",
    }
    return info


def get_hardware_info(w):
    cpu_info = platform.processor() or "✘ 未获取"
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    partitions = psutil.disk_partitions()
    gpu_list = []
    try:
        for gpu in w.Win32_VideoController():
            gpu_list.append(gpu.Name)
    except Exception:
        gpu_list = ["✘ 未获取"]

    # 创建基础信息字典
    info = {
        "处理器": cpu_info,
        "处理器架构": platform.machine(),
        "物理核心数": psutil.cpu_count(logical=False),
        "逻辑处理器数": psutil.cpu_count(logical=True),
        "内存总量": f"{round(mem.total / (1024 ** 3), 2)} GB",
        "内存可用量": f"{round(mem.available / (1024 ** 3), 2)} GB",
        "磁盘总量": f"{round(disk.total / (1024 ** 3), 2)} GB",
        "磁盘可用量": f"{round(disk.free / (1024 ** 3), 2)} GB",
        "分区信息": [{"设备": p.device, "类型": p.fstype, "挂载点": p.mountpoint} for p in partitions],
        "GPU": gpu_list,
        "进程数": len(psutil.pids()),
        "电池信息": psutil.sensors_battery().percent if psutil.sensors_battery() else "✘ 未获取",
    }

    # 添加详细硬件信息（如果有）
    try:
        # 内存条信息
        memory_slots = []
        for mem in w.Win32_PhysicalMemory():
            memory_slots.append({
                "容量": f"{int(mem.Capacity)/(1024**3):.2f} GB",
                "速度": f"{mem.Speed} MHz",
                "制造商": mem.Manufacturer,
                "序列号": mem.SerialNumber
            })

        # 磁盘详细信息
        disks = []
        for disk in w.Win32_DiskDrive():
            disks.append({
                "型号": disk.Model,
                "接口类型": disk.InterfaceType,
                "序列号": disk.SerialNumber,
                "大小": f"{int(disk.Size)/(1024**3):.2f} GB" if disk.Size else "✘ 未获取"
            })

        # 添加详细硬件信息到主字典
        info.update({
            "详细硬件信息": {
                "内存条信息": memory_slots,
                "磁盘详细信息": disks,
                "主板信息": {
                    "制造商": w.Win32_BaseBoard()[0].Manufacturer,
                    "产品": w.Win32_BaseBoard()[0].Product
                },
                "电池信息": [b.Name for b in w.Win32_Battery()] if w.Win32_Battery() else "无电池"
            }
        })
    except Exception:
        info["详细硬件信息"] = "✘ 需要管理员权限"

    return info


def get_services_info(w):
    running_services = []
    stopped_services = []
    try:
        for service in w.Win32_Service():
            if service.State == "Running":
                running_services.append(service.Name)
            else:
                stopped_services.append(service.Name)
    except Exception:
        pass

    return {
        "运行中服务数": len(running_services),
        "已停止服务数": len(stopped_services),
    }


def get_performance_info():
    info = {
        "CPU使用率": f"{psutil.cpu_percent()}%",
        "每个CPU核心使用率": psutil.cpu_percent(percpu=True),
        "内存使用率": f"{psutil.virtual_memory().percent}%",
        "交换内存使用情况": f"{psutil.swap_memory().percent}%",
        "网络IO统计": psutil.net_io_counters()._asdict(),
        "启动进程数": psutil.boot_time(),
        "系统平均负载": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else "✘ 未获取"
    }
    return info


def get_network_info(w):
    adapters = []
    for adapter in w.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        adapters.append({
            "名称": adapter.Description,
            "MAC地址": adapter.MACAddress,
            "IP地址": adapter.IPAddress[0] if adapter.IPAddress else "✘ 未获取",
            "子网掩码": adapter.IPSubnet[0] if adapter.IPSubnet else "✘ 未获取",
            "默认网关": adapter.DefaultIPGateway[0] if adapter.DefaultIPGateway else "✘ 未获取"
        })
    info = {
        "网络适配器数量": len(adapters),
        "网络适配器": adapters,
        "主IP地址": socket.gethostbyname(socket.gethostname()),
        "所有IP地址": [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]],
        "主机名": socket.gethostname(),
    }
    return info


def get_security_info(w):
    firewall = "✘ 未获取"
    try:
        firewall_products = w.Win32_FirewallProduct()
        firewall = "启用" if firewall_products and firewall_products[0].Enabled else "禁用"
    except Exception:
        pass

    avs = []
    try:
        for av in w.Win32_AntivirusProduct():
            avs.append({
                "名称": av.displayName,
                "版本": av.productVersion,
                "状态": av.productState
            })
    except Exception:
        avs = []
    
    info = {
        "防火墙状态": firewall,
        "防病毒软件数量": len(avs),
        "防病毒软件": avs,
    }

    try:
        # BitLocker状态
        bitlocker = []
        for vol in w.Win32_EncryptableVolume():
            bitlocker.append({
                "驱动器": vol.DriveLetter,
                "保护状态": vol.ProtectionStatus
            })

        # UAC状态
        uac = w.Win32_OperatingSystem(
        )[0].DataExecutionPrevention_SupportPolicy

        info.update({
            "BitLocker状态": bitlocker,
            "UAC状态": uac,
            "安全启动状态": "✘ 需要WMI查询权限"
        })
    except Exception:
        status = {"安全状态": "✘ 需要管理员权限"}

    return info



def get_environment_info():
    return {
        "Python路径": sys.path,
        "系统区域设置": locale.getdefaultlocale(),
        "系统编码": sys.getdefaultencoding(),
        "当前时区": time.tzname,
        "夏令时状态": time.daylight
    }


def get_user_info():
    info = {
        "用户名": getpass.getuser(),
        "用户目录": os.path.expanduser("~"),
        "登录终端": os.environ.get("SESSIONNAME", "✘ 未获取"),
        # "用户环境变量": dict(os.environ),
    }
    return info


def get_python_info():
    info = {
        "Python解释器": sys.executable,
        "Python版本": platform.python_version(),
        "Python实现": platform.python_implementation(),
        "Python编译器": platform.python_compiler(),
    }
    return info


def get_bios_board_info(isAdmin, w):
    info = {}
    if isAdmin:
        try:
            bios = w.Win32_BIOS()[0]
            disk = w.Win32_DiskDrive()[0]
            info = {
                "BIOS序列号": bios.SerialNumber.strip(),
                "BIOS版本": bios.Version.strip(),
                "BIOS发布日期": bios.ReleaseDate.split(".")[0],
                "BIOS制造商": bios.Manufacturer.strip(),
                "BIOS语言": bios.Language.strip() if hasattr(bios, "Language") else "✘ 未获取",
                "主板型号": bios.SMBIOSBIOSVersion.strip() if hasattr(bios, "SMBIOSBIOSVersion") else "✘ 未获取",
                "主板制造商": bios.Manufacturer.strip(),
                "主板序列号": bios.SerialNumber.strip() if hasattr(bios, "SerialNumber") else "✘ 未获取",
                "硬盘序列号": disk.SerialNumber.strip() if hasattr(disk, "SerialNumber") else "✘ 未获取",
            }
        except Exception:
            info = {
                "BIOS序列号": "获取失败",
                "BIOS版本": "获取失败",
                "BIOS发布日期": "获取失败",
                "BIOS制造商": "获取失败",
                "主板型号": "获取失败",
                "主板制造商": "获取失败",
                "主板序列号": "获取失败",
                "硬盘序列号": "获取失败",
            }
    return info


def main(isAdmin):
    start_time = time.time()
    w = wmi.WMI()

    categories = [
        ("系统信息", get_system_info(w, start_time)),
        ("硬件信息", get_hardware_info(w)),
        ("网络信息", get_network_info(w)),
        ("安全信息", get_security_info(w)),
        ("性能数据", get_performance_info()),
        ("服务信息", get_services_info(w)),
        ("用户信息", get_user_info()),
        ("环境信息", get_environment_info()),
        ("Py环境", get_python_info()),
        ("BIOS主板", get_bios_board_info(isAdmin, w))
    ]

    for cat, info in categories:
        print(f"\n————■ {cat}")
        for k in sorted(info.keys()):
            print(f"{k}: {info[k]}")


if is_admin():
    print("✔ 脚本正以Administrator运行")
    main(True)
else:
    print("当前权限：User，尝试以Administrator重新运行")
    run_as_admin()
    if is_admin():
        print("✔ 已获Administrator权限")
        main(True)
    else:
        print("✘ 用户拒绝")
        main(False)
