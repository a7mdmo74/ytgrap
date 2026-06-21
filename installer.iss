[Setup]
AppName=YTGrab
AppVersion=2.0
AppPublisher=Ahmed Amer
AppPublisherURL=https://github.com/ahmedamer
DefaultDirName={autopf}\YTGrab
DefaultGroupName=YTGrab
OutputDir=D:\projects\ytgrap\installer
OutputBaseFilename=YTGrab-Setup
SetupIconFile=D:\projects\ytgrap\ytgrab_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\projects\ytgrap\dist\YTGrab\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\YTGrab"; Filename: "{app}\YTGrab.exe"; IconFilename: "{app}\YTGrab.exe"
Name: "{group}\{cm:UninstallProgram,YTGrab}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\YTGrab"; Filename: "{app}\YTGrab.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\YTGrab.exe"; Description: "{cm:LaunchProgram,YTGrab}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
