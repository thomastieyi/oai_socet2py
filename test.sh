
#! /bin/bash

read -p "输入eNB机器的ip地址:" eNB_ip
read -p "输入eNB机器的用户名(建议使用root):" eNB_user
read -p "输入eNB机器的密码:" eNB_passwd
read -p "输入UE机器的ip地址:" UE_ip
read -p "输入UE机器的用户名(建议使用root):" UE_user
read -p "输入UE机器的密码:" UE_passwd
read -p "输入局域网代理地址及端口：proxy_addr:port(http 端口)" proxy_addr
echo $proxy_addr > temp.proxy_addr
sshpass -p $eNB_passwd scp temp.proxy_addr $eNB_user@$eNB_ip
sshpass -p $UE_passwd scp temp.proxy_addr $UE_user@$UE_ip

sudo apt-get install sshpass -y 
sed -i 's/#   StrictHostKeyChecking ask/StrictHostKeyChecking no/g' /etc/ssh/ssh_config

echo "开始安装编译eNB，请稍后"
sshpass -p $eNB_passwd ssh $eNB_user@$eNB_ip > /dev/null 2>&1 << eeooff
export proxy_addr=`cat temp.proxy_addr`
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
cd cmake_targets/
./build_oai -I --eNB

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

exit
eeooff
echo "开始安装编译UEs，请稍后"
sshpass -p $UE_passwd ssh $UE_user@$UE_ip > /dev/null 2>&1 << eeooff
export proxy_addr=`cat temp.proxy_addr`
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
cd cmake_targets/
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

exit
eeooff