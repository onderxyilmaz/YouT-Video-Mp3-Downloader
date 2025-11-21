; Inno Setup Script for YouT Video Mp3 Downloader
; www.jrsoftware.org/isinfo.php

#define MyAppName "YouT Video Mp3 Downloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "UnderSpeed"
#define MyAppURL "https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader"
#define MyAppExeName "YouT-Video-Mp3-Downloader.exe"

[Setup]
; Uygulama bilgileri
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Kurulum dizini
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Çıktı ayarları
OutputDir=installer
OutputBaseFilename=YouT-Video-Mp3-Downloader-Setup-v{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Lisans
LicenseFile=LICENSE

; Yönetici izni
PrivilegesRequired=lowest

; Windows versiyon desteği
MinVersion=6.1sp1
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Hızlı Başlatma simgesi oluştur"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Tüm uygulama klasörü (onedir build)
Source: "dist\YouT-Video-Mp3-Downloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; İkon dosyası (kısayollar için)
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; Dokümantasyon (ana klasöre)
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; NOT: FFmpeg installer tarafından yüklenmeyecek, uygulama içinden indirilecek

[Icons]
; Başlat menüsü kısayolu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Masaüstü kısayolu (opsiyonel) - İkon dosyasını kullan
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
; Hızlı başlatma (opsiyonel)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Kurulum bitince uygulamayı çalıştır (opsiyonel)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Kullanıcı ayarlarını sil
Type: files; Name: "{app}\config.json"
Type: files; Name: "{app}\ffmpeg.exe"
Type: dirifempty; Name: "{app}"

[Code]
// Özel kurulum mesajları
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('YouT Video Mp3 Downloader kurulumuna hoş geldiniz!' + #13#10#13#10 + 
         'Bu uygulama YouTube videolarını MP4 ve MP3 formatında indirmenizi sağlar.', 
         mbInformation, MB_OK);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Kurulum sonrası işlemler buraya eklenebilir
  end;
end;

