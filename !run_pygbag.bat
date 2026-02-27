@rem  See: https://pygame-web.github.io/wiki/pygbag/
@rem       https://pygame-web.github.io/wiki/publishing/itch.io/


set DEST=visual-lambda-2.3
@rem  It will be also the name of .apk file


rd /Q /S %DEST%
mkdir %DEST%


xcopy *.py                              %DEST%\
xcopy config.cfg                        %DEST%\
xcopy library.txt                       %DEST%\

xcopy res\toolbar_icons.png             %DEST%\res\
xcopy res\OpenSans-Regular.ttf          %DEST%\res\
xcopy res\OFL.txt                       %DEST%\res\

xcopy workspaces\default_workspace.xml  %DEST%\workspaces\
xcopy workspaces\clear.xml              %DEST%\workspaces\
xcopy workspaces\library_demo.xml       %DEST%\workspaces\
xcopy workspaces\predecessors.xml       %DEST%\workspaces\
xcopy workspaces\puzzles.xml            %DEST%\workspaces\


python -m pygbag --app_name VisualLambda --package bntr.visuallambda --title "Visual Lambda" --template pygbag_0.9.3_index_html.tmpl --icon docs/favicon.png --archive %DEST%


@rem  Prepare for https://bntre.github.io/visual-lambda/
xcopy %DEST%\build\web\index.html       docs\ /Y
xcopy %DEST%\build\web\%DEST%.tar.gz    docs\ /Y
