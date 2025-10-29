#!/usr/bin/env python3
"""
安装包制作工具
生成Windows NSIS安装向导 / Linux AppImage / macOS DMG
"""

import platform
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
VERSION_FILE = ROOT_DIR / "VERSION"
VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "14.0.0"


def create_windows_installer():
    """创建Windows NSIS安装脚本"""
    nsis_script = BUILD_DIR / "installer.nsi"
    
    nsis_content = f"""
; KOOK消息转发系统 - Windows安装向导脚本
; 版本: {VERSION}

!include "MUI2.nsh"

; 基本配置
Name "KOOK消息转发系统"
OutFile "..\\dist\\KOOK-Forwarder-Setup-v{VERSION}.exe"
InstallDir "$PROGRAMFILES64\\KookForwarder"
InstallDirRegKey HKLM "Software\\KookForwarder" "InstallDir"
RequestExecutionLevel admin

; 界面配置
!define MUI_ICON "..\\build\\icon.ico"
!define MUI_UNICON "..\\build\\icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "..\\build\\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\\build\\welcome.bmp"

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装节
Section "主程序" SecMain
    SetOutPath "$INSTDIR"
    
    ; 复制文件
    File /r "..\\dist\\installer\\*.*"
    
    ; 创建快捷方式
    CreateDirectory "$SMPROGRAMS\\KOOK消息转发系统"
    CreateShortcut "$SMPROGRAMS\\KOOK消息转发系统\\KOOK消息转发系统.lnk" "$INSTDIR\\启动.bat" "" "$INSTDIR\\icon.ico"
    CreateShortcut "$DESKTOP\\KOOK消息转发系统.lnk" "$INSTDIR\\启动.bat" "" "$INSTDIR\\icon.ico"
    
    ; 写入注册表
    WriteRegStr HKLM "Software\\KookForwarder" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\\KookForwarder" "Version" "{VERSION}"
    
    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KookForwarder" \\
                     "DisplayName" "KOOK消息转发系统"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KookForwarder" \\
                     "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KookForwarder" \\
                     "DisplayIcon" "$INSTDIR\\icon.ico"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KookForwarder" \\
                     "DisplayVersion" "{VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KookForwarder" \\
                     "Publisher" "KOOK Forwarder Team"
SectionEnd

; 卸载节
Section "Uninstall"
    ; 删除文件
    RMDir /r "$INSTDIR"
    
    ; 删除快捷方式
    Delete "$DESKTOP\\KOOK消息转发系统.lnk"
    RMDir /r "$SMPROGRAMS\\KOOK消息转发系统"
    
    ; 删除注册表
    DeleteRegKey HKLM "Software\\KookForwarder"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KookForwarder"
SectionEnd
"""
    
    nsis_script.write_text(nsis_content, encoding="utf-8")
    print(f"✅ Windows安装脚本已创建: {nsis_script}")
    print("提示：运行 makensis installer.nsi 生成安装程序")


def create_linux_appimage():
    """创建Linux AppImage配置"""
    print("Linux AppImage配置...")
    
    # AppImage需要使用appimagetool
    # 这里创建AppDir结构
    appdir = BUILD_DIR / "AppDir"
    appdir.mkdir(parents=True, exist_ok=True)
    
    # 创建desktop文件
    desktop_file = appdir / "kook-forwarder.desktop"
    desktop_file.write_text(f"""[Desktop Entry]
Type=Application
Name=KOOK消息转发系统
Comment=KOOK消息转发到Discord/Telegram/飞书
Exec=kook-forwarder
Icon=kook-forwarder
Categories=Network;Chat;
Version={VERSION}
""")
    
    print(f"✅ AppImage配置已创建: {appdir}")
    print("提示：使用 appimagetool 打包为AppImage")


def create_macos_dmg():
    """创建macOS DMG配置"""
    print("macOS DMG配置...")
    
    # macOS使用create-dmg工具
    # 这里创建DMG配置脚本
    dmg_script = BUILD_DIR / "create-dmg.sh"
    dmg_script.write_text(f"""#!/bin/bash
# macOS DMG创建脚本

create-dmg \\
  --volname "KOOK消息转发系统 v{VERSION}" \\
  --window-pos 200 120 \\
  --window-size 800 400 \\
  --icon-size 100 \\
  --icon "KOOK消息转发系统.app" 200 190 \\
  --hide-extension "KOOK消息转发系统.app" \\
  --app-drop-link 600 185 \\
  "../dist/KOOK-Forwarder-v{VERSION}-macOS.dmg" \\
  "../frontend/dist-electron/mac"
""", encoding="utf-8")
    
    dmg_script.chmod(0o755)
    print(f"✅ DMG创建脚本已创建: {dmg_script}")
    print("提示：运行 ./create-dmg.sh 生成DMG文件")


def main():
    """主函数"""
    os_name = platform.system().lower()
    
    if os_name == "windows":
        create_windows_installer()
    elif os_name == "linux":
        create_linux_appimage()
    elif os_name == "darwin":
        create_macos_dmg()
    else:
        print(f"不支持的操作系统: {os_name}")


if __name__ == "__main__":
    main()
