Developed with Python 3.5 (Tested with Python 3.4)

Required Python Packages
 * pyModbusTCP
 * mysql-connector (this may be installed by default; may be called mysql-connector-python)

Use on Mac or Linux
  python -m pip install [package]
on windows 
  python.exe -m pip install [package]
  
You may need to navigate to the location of python or add the path to environment variables

MariaDB Create
DROP DATABASE IF EXISTS solar;
CREATE DATABASE solar;


MariaDB Permissions
GRANT all
ON solarDB.*
TO sUser@localhost identified by 'sPasswd';