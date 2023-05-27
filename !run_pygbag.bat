

set DEST=visual-lambda-2.0
@rem  It will be also the name of .apk file


rd /Q /S %DEST%
mkdir %DEST%


xcopy *.py %DEST%\
xcopy config.cfg %DEST%\
xcopy library.txt %DEST%\
xcopy toolbar_icons.png %DEST%\
xcopy workspaces\library_demo.xml %DEST%\workspaces\
xcopy workspaces\clear.xml %DEST%\workspaces\


python -m pygbag --app_name VisualLambda --package bntr.visuallambda --title "Visual Lambda" --template pygbag_index_html.tmpl --icon favicon.png --archive %DEST%
