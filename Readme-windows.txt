Instructions for installing jcchess on windows.
I tried this on windows 7 64 bit.


 1. Install python 3.4

    Don't use Python 3.5 or greater since pygobject for windows doesn't support it. 
 
    Download https://www.python.org/ftp/python/3.4.4/python-3.4.4.amd64.msi

    Install it:
        select 'install for all users'

        # accept the default for the install directory
        C:\Python34\

        when it says 'customize python 3.4.4 (64 bit)'
        click next to accept the defaults
        

 2. Install pygobject for windows

    uninstall any previous version of PyGI from add/remove panel

    Download from latest version 
    I used 3.24.1_rev1 from this link:
        https://sourceforge.net/projects/pygobjectwin32/files/pygi-aio-3.24.1_rev1-setup_049a323fe25432b10f7e9f543b74598d4be74a39.exe/download

    Install it:

        When it says 'Do you have portable python installation?' answer 'No'

        For 'choose python destination to install'        
        check the box for 3.4 64 C:\Python34\Lib\site_packages

        For 'Choose available GNOME/Freedesktop libraries to install' select:
            Base packages
            GDK-Pixbuf 2.36.6
            GTK+ 3.18.9
            Pango 1.40.6

        For 'Choose non GNOME packages to install'
            none

        For 'choose development packages to install'
            none


 3. Install jcchess

    Download https://github.com/johncheetham/jcchess/archive/master.zip
    Right click on jcchess-master in downloads folder and do 'extract all'

    Accept the default and it will install in C:\Users\Home\Downloads\jcchess-master


 4. Check it works

    open command prompt (in windows 7 it's in All Programs, Accessories folder).

    # cd into jcchess folder
    cd C:\Users\Home\Downloads\jcchess-master\jcchess-master

    # run it
    c:\Python34\python.exe run.py


 5. Create a launcher

    You can create a bat file to make it easier to launch

    # start notepad from the command prompt to create jcchess.bat file
    notepad jcchess.bat

    # add these lines to the file and save it
    cd C:\Users\Home\Downloads\jcchess-master\jcchess-master
    c:\Python34\python.exe run.py

    Type 'jcchess.bat' or double click it to start jcchess.

    Lastly use explorer to drag jcchess.bat onto the dektop.
    You can now start it from the desktop by double clicking the jcchess icon.
















