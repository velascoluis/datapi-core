pip uninstall datapi -y 
 pip install -e . --no-cache-dir
rm -Rf test
datapi init test
cd test
