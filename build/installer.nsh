; NSIS安装脚本扩展
; 用于自定义Windows安装程序

; 安装前检查
!macro customInit
  ; 检查是否已安装
  ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "UninstallString"
  ${If} $0 != ""
    MessageBox MB_YESNO|MB_ICONQUESTION "检测到已安装旧版本，是否卸载后继续？" IDYES uninstall
    Quit
    uninstall:
      ExecWait '$0 /S _?=$INSTDIR'
      Delete $0
      RMDir $INSTDIR
  ${EndIf}
  
  ; 检查Python环境（可选）
  ; nsExec::ExecToStack 'python --version'
  ; Pop $0
  ; ${If} $0 != "0"
  ;   MessageBox MB_OK|MB_ICONEXCLAMATION "未检测到Python环境，部分功能可能无法使用。"
  ; ${EndIf}
!macroend

; 安装完成后
!macro customInstall
  ; 创建快捷方式
  CreateShortcut "$DESKTOP\KOOK消息转发系统.lnk" "$INSTDIR\${PRODUCT_FILENAME}.exe"
  
  ; 写入注册表
  WriteRegStr HKLM "Software\KOOK消息转发系统" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\KOOK消息转发系统" "Version" "${VERSION}"
  
  ; 创建卸载信息
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "DisplayName" "KOOK消息转发系统"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "Publisher" "KOOK Forwarder Team"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_FILENAME}.exe"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINSTALL_APP_KEY}" "NoRepair" 1
!macroend

; 卸载时
!macro customUnInstall
  ; 删除桌面快捷方式
  Delete "$DESKTOP\KOOK消息转发系统.lnk"
  
  ; 删除注册表
  DeleteRegKey HKLM "Software\KOOK消息转发系统"
  
  ; 询问是否保留配置文件
  MessageBox MB_YESNO|MB_ICONQUESTION "是否保留配置文件和数据？" IDYES keep_data
  RMDir /r "$APPDATA\KookForwarder"
  RMDir /r "$DOCUMENTS\KookForwarder"
  keep_data:
!macroend

; 界面文字本地化
!macro customHeader
  !define MUI_TEXT_WELCOME_INFO_TITLE "欢迎使用KOOK消息转发系统安装向导"
  !define MUI_TEXT_WELCOME_INFO_TEXT "这将在您的计算机上安装KOOK消息转发系统。$\r$\n$\r$\n建议在继续之前关闭所有其他应用程序。$\r$\n$\r$\n点击「下一步」继续。"
  !define MUI_TEXT_DIRECTORY_TITLE "选择安装位置"
  !define MUI_TEXT_DIRECTORY_SUBTITLE "请选择KOOK消息转发系统的安装文件夹。"
  !define MUI_TEXT_INSTALLING_TITLE "正在安装"
  !define MUI_TEXT_INSTALLING_SUBTITLE "KOOK消息转发系统正在安装，请稍候..."
  !define MUI_TEXT_FINISH_TITLE "安装完成"
  !define MUI_TEXT_FINISH_SUBTITLE "KOOK消息转发系统已成功安装到您的计算机。"
  !define MUI_TEXT_ABORT_TITLE "安装已中止"
  !define MUI_TEXT_ABORT_SUBTITLE "安装未完成。"
  
  !define MUI_BUTTONTEXT_FINISH "完成"
  !define MUI_TEXT_FINISH_INFO_TITLE "完成KOOK消息转发系统安装向导"
  !define MUI_TEXT_FINISH_INFO_TEXT "KOOK消息转发系统已安装在您的计算机上。$\r$\n$\r$\n点击「完成」关闭此向导。"
  !define MUI_TEXT_FINISH_INFO_REBOOT "您的计算机需要重新启动才能完成KOOK消息转发系统的安装。您想现在重新启动吗？"
  !define MUI_TEXT_FINISH_REBOOTNOW "现在重新启动"
  !define MUI_TEXT_FINISH_REBOOTLATER "我想稍后手动重新启动"
  !define MUI_TEXT_FINISH_RUN "运行KOOK消息转发系统"
  !define MUI_TEXT_FINISH_SHOWREADME "显示自述文件"
!macroend
