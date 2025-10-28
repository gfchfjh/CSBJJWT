; NSIS安装程序自定义脚本
; KOOK消息转发系统 Windows安装程序

; 自定义安装页面
!macro customInit
  ; 检查是否已安装旧版本
  ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString"
  ${If} $0 != ""
    MessageBox MB_YESNO|MB_ICONQUESTION "检测到已安装旧版本，是否卸载后继续？" IDYES uninstall IDNO abort
    uninstall:
      ExecWait '$0 /S _?=$INSTDIR'
      Delete $0
      Goto done
    abort:
      Abort
    done:
  ${EndIf}
!macroend

; 安装完成后
!macro customInstall
  ; 创建快捷方式
  CreateShortCut "$DESKTOP\KOOK消息转发系统.lnk" "$INSTDIR\${PRODUCT_NAME}.exe" "" "$INSTDIR\${PRODUCT_NAME}.exe" 0
  
  ; 添加到开始菜单
  CreateDirectory "$SMPROGRAMS\KOOK消息转发系统"
  CreateShortCut "$SMPROGRAMS\KOOK消息转发系统\KOOK消息转发系统.lnk" "$INSTDIR\${PRODUCT_NAME}.exe"
  CreateShortCut "$SMPROGRAMS\KOOK消息转发系统\卸载.lnk" "$INSTDIR\Uninstall ${PRODUCT_NAME}.exe"
  
  ; 写入注册表
  WriteRegStr HKCU "Software\${PRODUCT_NAME}" "InstallPath" "$INSTDIR"
  WriteRegStr HKCU "Software\${PRODUCT_NAME}" "Version" "${VERSION}"
  
  ; 显示完成提示
  MessageBox MB_OK "安装完成！$\n$\n欢迎使用KOOK消息转发系统。$\n$\n首次启动将自动进入配置向导。"
!macroend

; 卸载时
!macro customUnInstall
  ; 删除快捷方式
  Delete "$DESKTOP\KOOK消息转发系统.lnk"
  Delete "$SMPROGRAMS\KOOK消息转发系统\KOOK消息转发系统.lnk"
  Delete "$SMPROGRAMS\KOOK消息转发系统\卸载.lnk"
  RMDir "$SMPROGRAMS\KOOK消息转发系统"
  
  ; 删除注册表
  DeleteRegKey HKCU "Software\${PRODUCT_NAME}"
  
  ; 询问是否删除用户数据
  MessageBox MB_YESNO|MB_ICONQUESTION "是否删除所有配置和数据？$\n（包括账号、Bot配置、日志等）" IDYES delete_data IDNO skip_data
  delete_data:
    RMDir /r "$DOCUMENTS\KookForwarder"
    MessageBox MB_OK "用户数据已删除"
  skip_data:
!macroend
