#!/bin/sh
if [ ! -d "cJSON"]; then
git clone https://github.com/DaveGamble/cJSON.git
fi

mkdir build
cd build
echo "compling cJSON"
cmake ../cJSON
make
make install
ldconfig
cp libcjson.so /usr/lib
cp libcjson.so /lib
echo "complied cJSON   libcjson -lcjson"


echo "compling s2j"
gcc ../defh/s2j.c -L. -lcjson -fPIC -shared -o libs2j.so
ldconfig
cp libs2j.so /usr/lib
cp libs2j.so /lib
echo "complied s2j   libs2j -ls2j"


echo "compling socket"
gcc ../defh/py_client.c -L. -ls2j -lcjson -fPIC -shared -o libsocket.so
ldconfig
cp libsocket.so /usr/lib
cp libsocket.so /lib
echo "complied s2j   libsocket -lsocket"

echo "libs:"

echo "-lcjson   -ls2j -lsocket"
sed -e '/target_link_libraries (lte-softmodem -lsocket  -ls2j -lcjson)/d' $OPENAIR_HOME/cmake_targets/CMakeLists.txt > $OPENAIR_HOME/cmake_targets/CMakeLists2.txt
rm -rf $OPENAIR_HOME/cmake_targets/CMakeLists.txt
cp  $OPENAIR_HOME/cmake_targets/CMakeLists2.txt $OPENAIR_HOME/cmake_targets/CMakeLists.txt
sed -i '/target_link_libraries (lte-softmodem ${T_LIB})/a\target_link_libraries (lte-softmodem -lsocket  -ls2j -lcjson)' $OPENAIR_HOME/cmake_targets/CMakeLists.txt