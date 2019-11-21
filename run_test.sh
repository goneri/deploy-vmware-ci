#tmux new-session -d -s "myTempSession" /opt/my_script.sh

export VMWARE_TEST_PLATFORM=static
sudo yum install -y epel-release
sudo yum install -y python36-virtualenv.noarch git
test -d ansible || git clone https://github.com/ansible/ansible
if ! test -d ~/.virtualenv/py36; then
    test -d ~/.virtualenv/py36 || virtualenv-3 -p python3.6 ~/.virtualenv/py36
    source ~/.virtualenv/py36/bin/activate
    pip install --upgrade pip setuptools
    pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git
    pip install pyvmomi -ransible/requirements.txt jmespath
else
    source ~/.virtualenv/py36/bin/activate
fi

mkdir ~/done
mkdir ~/fail

cd ~/ansible
source hacking/env-setup

echo '
[DEFAULT]
vcenter_username: administrator@vsphere.local
vcenter_password: !234AaAa56
vcenter_hostname: vcenter.test
vmware_validate_certs: false
esxi1_username: root
esxi1_hostname: esxi1.test
esxi1_password: !234AaAa56
esxi2_username: root
esxi2_hostname: test2.test
esxi2_password: !234AaAa56
' > test/integration/cloud-config-vcenter.ini

for i in $(find test/integration/targets -maxdepth 1 -type d -regex '.*/\(vcenter\|vmware\).*' -exec basename '{}' \;|sort); do
    if [ -f "$HOME/done/$i.log" ]; then
        continue
    fi
    echo $i
    start=$(date +%s)
    if ansible-test integration --python 3.6 $i -vvvv > run.log 2>&1 ; then
        duration=$(expr $(date +%s) - ${start})
        rm -f "$HOME/fail/$i.log"
        mv run.log "$HOME/done/$i.log"
        echo "success $duration"
        echo "${i},${duration}" >> "$HOME/$i.csv"
    else
        mv run.log "$HOME/fail/$i.log"
        echo "fail"
    fi
    sleep 1
done
touch "$HOME/done.stamp"
