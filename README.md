# Deploy ESXi+vsphere lab on libvirt

## Description

This playbook will deploy:

- a local vsphere
- two ESXi
- a datastore VM (with a NFS)

It can easier target a local Libvirt hypervisor, or an OpenStack tenant.

## Requirements

- a Python virtualenv
- memory 20GB
- vcpus: 2 for vcenter, 1 for ESXi, more will probably seriously increase the performance
- Ansible 2.8+
- Qcow2 Images:
    - ESXi: https://github.com/virt-lightning/esxi-cloud-images
    - vcenter: https://github.com/goneri/vcsa_to_qcow2
- A copy of the following repository in the ../ansible-zuul directory.

    mkdir ../ansible-zuul
    git clone https://github.com/ansible/ansible-zuul-jobs ../ansible-zuul/ansible-zuul-jobs
    git clone https://opendev.org/zuul/zuul-jobs.git ../ansible-zuul/zuul-jobs

### Libvirt

- A working libvirt installation
- Virt-Lightning
- Ensure nested KVM is enabled
    ```shell
    cat /etc/modprobe.d/kvm.conf
    options kvm_intel nested=1 enable_apicv=n
    options kvm ignore_msrs=1
    ```

## Installation

    virtualenv -p python3.7 .virtualenv/py37
    source .virtualenv/py37/bin/activate
    pip install -r requirements.txt
    ./run.py --driver openstack deploy

## Usage

Just use the `--help` argument:

    ./run.py --help

For instance, to start a deployment:

    ./run.py --driver openstack deploy


## How to run the community.vmware test-suite

### prepare a venv

Prepare and load a virtualenv, install ansible and position yourself in ~/.ansible/collections/ansible_collections/community/vmware/

You should also install some extra dependencies with:

    pip install -r requirements.txt -r test-requirements.txt

### write the configuration for ansible-test

You need to write a configuration file in your collection directory with the lab credentials. e.g:

    [DEFAULT]
    vcenter_username: administrator@vsphere.local
    vcenter_password: QW/B|aEwN*NUQ,~7$Llf
    vcenter_hostname: vcenter.test
    vmware_validate_certs: false
    esxi1_username: zuul
    esxi1_hostname: esxi1.test
    esxi1_password: 1oaGnT1OxWOPw3456

To know the correct passwords, take a look at the following files:

- `/tmp/vcenter/tmp/vcenter_password.txt`
- `/tmp/vcenter/tmp/esxi_password_zuul.txt`

### call ansible-test

For here you can call `ansible-test` with:

    VMWARE_TEST_PLATFORM=static ansible-test integration --python 3.9 vmware_dvswitch

Just replace `3.9`` with your actual verison of Python, and `vmware_dvswitch`` with the target to run.
