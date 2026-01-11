!include "MUI2.nsh"

Name "Hei-DataHub"
OutFile "hei-datahub-setup.exe"
InstallDir "$PROGRAMFILES64\Hei-DataHub"
InstallDirRegKey HKCU "Software\Hei-DataHub" ""
RequestExecutionLevel admin

!define VERSION "0.61-beta"

!define MUI_ABORTWARNING
!define MUI_ICON "hei-datahub.ico"
!define MUI_UNICON "hei-datahub.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Hei-DataHub Core" SecCore
  SetOutPath "$INSTDIR"
  File "hei-datahub.exe"
  File "hei-datahub.ico"

  ; Write the uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Registry keys for Add/Remove programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hei-DataHub" "DisplayName" "Hei-DataHub"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hei-DataHub" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hei-DataHub" "DisplayIcon" '"$INSTDIR\hei-datahub.ico"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hei-DataHub" "Publisher" "Hei-DataHub Team"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hei-DataHub" "DisplayVersion" "${VERSION}"
SectionEnd

Section "Start Menu Shortcuts" SecShortcuts
  CreateDirectory "$SMPROGRAMS\Hei-DataHub"
  ; Use hei-datahub.ico for better quality icons
  CreateShortcut "$SMPROGRAMS\Hei-DataHub\Hei-DataHub.lnk" "$INSTDIR\hei-datahub.exe" "" "$INSTDIR\hei-datahub.ico" 0
  CreateShortcut "$SMPROGRAMS\Hei-DataHub\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  ; Desktop shortcut
  CreateShortcut "$DESKTOP\Hei-DataHub.lnk" "$INSTDIR\hei-datahub.exe" "" "$INSTDIR\hei-datahub.ico" 0
SectionEnd

Section "Uninstall"
  ; Remove program files
  Delete "$INSTDIR\hei-datahub.exe"
  Delete "$INSTDIR\hei-datahub.ico"
  Delete "$INSTDIR\uninstall.exe"
  Delete "$SMPROGRAMS\Hei-DataHub\Hei-DataHub.lnk"
  Delete "$SMPROGRAMS\Hei-DataHub\Uninstall.lnk"
  Delete "$DESKTOP\Hei-DataHub.lnk"
  RMDir "$SMPROGRAMS\Hei-DataHub"
  RMDir "$INSTDIR"

  ; ===== COMPLETE DATA CLEANUP =====
  ; Remove config directory (~/.config/hei-datahub)
  RMDir /r "$PROFILE\.config\hei-datahub"

  ; Remove cache directory (~/.cache/hei-datahub)
  RMDir /r "$PROFILE\.cache\hei-datahub"

  ; Remove state directory (~/.local/state/hei-datahub)
  RMDir /r "$PROFILE\.local\state\hei-datahub"

  ; Remove data directory (%LOCALAPPDATA%\Hei-DataHub)
  RMDir /r "$LOCALAPPDATA\Hei-DataHub"

  ; Remove credentials from Windows Credential Manager
  nsExec::ExecToLog 'cmdkey /delete:hei-datahub'
  nsExec::ExecToLog 'cmdkey /delete:hei-datahub:token'
  nsExec::ExecToLog 'cmdkey /delete:hei-datahub:password'

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Hei-DataHub"
  DeleteRegKey HKCU "Software\Hei-DataHub"
SectionEnd
