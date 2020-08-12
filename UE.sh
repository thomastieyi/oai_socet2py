#! /bin/bash
read -p "输入局域网代理地址及端口：proxy_addr:port(http 端口)" proxy_addr
git config --global https.proxy http://$proxy_addr
git config --global https.proxy https://$proxy_addr
export http_proxy="http://$proxy_addr"
export https_proxy="https://$proxy_addr"
cd ~
mkdir oai
cd oai
git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git -b develop
chmod a+x openairinterface5g
cd openairinterface5g
source oaienv
git clone https://github.com/thomastieyi/oai_socet2py.git
chmod a+x oai_socet2py
cd oai_socet2py
./install.sh
cd ../cmake_targets
./build_oai -I --UE

check_results=`uname -r | cut -d- -f3`
echo "现在操作内核为: `uname -r`"
if [[ $check_results = "lowlatency" ]] 
then 
    echo "无需切换内核"
    ket=`cat  /boot/grub/grub.cfg | grep "Ubuntu, with"|grep -n "lowlatency'" |cut -d: -f1`
    grub=`cat  /etc/default/grub | grep -n "GRUB_DEFAULT=" |cut -d: -f1`
    b=1
    c="1> "
    val=`expr $ket - $b`
    index=$val
    #echo "${grub}s:.*:GRUB_DEFAULT=1000:g"
    sed -i "${grub}s:.*:GRUB_DEFAULT=\"1> ${index}\":g"  /etc/default/grub
    sudo update-grub
else 
    echo "正在安装安装低延时内核，安装完成后请重启虚拟机"
    sudo apt-get install linux-lowlatency -y
    sudo apt-get -y install linux-image-`uname -r | cut -d- -f1-2`-lowlatency 
    sudo apt-get -y install linux-headers-`uname -r | cut -d- -f1-2`-lowlatency
    ket=`cat  /boot/grub/grub.cfg | grep "Ubuntu, with"|grep -n "lowlatency'" |cut -d: -f1`
    grub=`cat  /etc/default/grub | grep -n "GRUB_DEFAULT=" |cut -d: -f1`
    b=1
    c="1> "
    val=`expr $ket - $b`
    index=$val
    #echo "${grub}s:.*:GRUB_DEFAULT=1000:g"
    sed -i "${grub}s:.*:GRUB_DEFAULT=\"1> ${index}\":g"  /etc/default/grub
    sudo update-grub
    echo "安装完成，请重新启动虚拟机"

 fi