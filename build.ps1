venv_build/Scripts/python.exe -m PyInstaller `
--onefile  `
--windowed `
--clean `
--noupx `
--collect-all pygame_manager `
--collect-all pong `
--add-data "pong./_assets;pong/_assets" `
--add-data "pong./_languages;pong/_languages" `
--add-data "data; pong/data"
--icon "pong/_assets/icons/icon.ico" `
--name "PONG - Chaos Evolution" `
launcher.py