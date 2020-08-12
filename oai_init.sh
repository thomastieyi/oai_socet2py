#!/bin/sh
sed -i 's/#   StrictHostKeyChecking ask/StrictHostKeyChecking no/g' /etc/ssh/ssh_config
cd ~
mkdir oai
cd oai
git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git -b develop
chmod a+x openairinterface5g
cd openairinterface5g
source oaienv
cd cmake_targets/


