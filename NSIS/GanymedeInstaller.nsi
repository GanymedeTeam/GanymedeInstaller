; Script NSIS pour installer Ganymede

OutFile "GanymedeInstaller.exe"   ; Nom du fichier d'installation généré
InstallDir "$DESKTOP\Ganymede"  ; Répertoire d'installation par défaut
RequestExecutionLevel user   ; Niveau de droits nécessaires
Name "Ganymede"

; Inclure le fichier de langue
!include "MUI2.nsh"
!include "French.nsh" ; Assurez-vous que ce fichier est dans le répertoire ou spécifiez le chemin correct

; Définir la langue de l'installateur
!define MUI_LANGUAGE "French"

; Pages d'installation
Page directory   ; Page pour choisir le répertoire d'installation
Page instfiles    ; Page pour afficher la progression de l'installation

Section "Install"   ; Section principale d'installation
    SetOutPath "$INSTDIR"   ; Définir le répertoire de sortie

    ; Ajouter les fichiers du jeu
    File /r "C:\Users\jules\workspace\GanymedeInstaller\GanymedeInstallPackage\*.*"   ; Inclure tous les fichiers du répertoire de l'application

    ; Créer un raccourci sur le bureau
    CreateShortCut "$DESKTOP\Ganymede.lnk" "$INSTDIR\Ganymede.exe"

    ; Créer un raccourci dans le menu démarrer
    CreateShortCut "$SMPROGRAMS\Ganymede\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

; Section de désinstallation
Section "Uninstall"
    ; Supprimer les fichiers et les répertoires
    Delete "$INSTDIR\Ganymede.exe"
    RMDir /r "$INSTDIR"

    ; Supprimer les raccourcis
    Delete "$DESKTOP\Ganymede.lnk"
    Delete "$SMPROGRAMS\Ganymede\Uninstall.lnk"
   

    ; Supprimer le répertoire du menu démarrer
    RMDir "$SMPROGRAMS\Ganymede"
SectionEnd

