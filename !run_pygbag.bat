

set DEST=visual-lambda-2.0
@rem  It will be also the name of .apk file


rd /Q /S %DEST%
mkdir %DEST%


xcopy *.py %DEST%\
xcopy config.cfg %DEST%\
xcopy toolbar_icons.png %DEST%\
xcopy workspaces\default_workspace.xml %DEST%\workspaces\


python -m pygbag --app_name VisualLambda --package bntr.visuallambda --title "Visual Lambda" %DEST%
