#!/usr/bin/env python3

import argparse
import subprocess
import os

class DriverOpenStack:

    @staticmethod
    def cleanup(args):
        subprocess.check_call(["ansible-playbook", "openstack/playbooks/clean.yaml", "-e", "prefix=%s" % args.prefix])

    @staticmethod
    def purge(args):
        subprocess.check_call(["ansible-playbook", "openstack/playbooks/purge.yaml", "-e", "prefix=%s" % args.prefix])

    @staticmethod
    def deploy(args):
        subprocess.check_call(["ansible-playbook", "openstack/playbooks/deploy.yaml", "-i", "openstack/inventory/openstack.yaml", "-e", "prefix=%s" % args.prefix])
        if args.run_test:
            subprocess.check_call(["ansible-playbook", "-vv", "playbooks/run_test.yaml", "-i", "openstack/inventory/openstack.yaml", "-e", "prefix=%s" % args.prefix])

class DriverLibvirt:

    @staticmethod
    def cleanup(args):
        for i in ["esxi1", "esxi2", "vcenter", "datastore"]:
            subprocess.check_call(["vl", "stop", i])

    @staticmethod
    def purge(args):
        subprocess.check_call(["vl", "down"])

    @staticmethod
    def deploy(args):
        # prepare virt lightning configuration
        cmd = []
        cmd.append("ansible-playbook")
        cmd.append("libvirt/playbooks/prepare_virt_lightning.yaml")
        cmd.extend([ '-e "{}_distro={}"'.format(k,vars(args)[k]) for k in ( "datastore", "esxi", "vcenter" ) if vars(args)[k] is not None ])
        cmd.append("-vv")
        subprocess.check_call(cmd)
        # create virt lightning vm
        subprocess.check_call(["vl", "up", "--virt-lightning-yaml", "libvirt/virt-lightning.yaml"])
        # download zuul useful roles
        cmd = []
        cmd.append("ansible-playbook")
        cmd.append("libvirt/playbooks/download_zuul_ci_roles.yaml")
        cmd.append("-vv")
        subprocess.check_call(cmd)
        # create ansible inventory
        subprocess.check_call("vl ansible_inventory>inventory", shell=True)
        # unset any ANSIBLE_ROLES_PATH variable to read the ansible.cfg file
        if "ANSIBLE_ROLES_PATH" in os.environ :
            del os.environ['ANSIBLE_ROLES_PATH']
        # prepare datastore
        subprocess.check_call(["ansible-playbook", "libvirt/playbooks/prepare_datastore.yaml", "-i", "inventory", "-vv"])
        subprocess.check_call(["ansible-playbook", "playbooks/write_inventory.yaml", "-i", "inventory", "-vv"])
        if args.run_test:
            subprocess.check_call(["ansible-playbook", "-vv", "playbooks/run_test.yaml", "-i", "inventory", "-e", "prefix=%s" % args.prefix])


parser = argparse.ArgumentParser(description='Process some integers.')

actions = {
    'deploy': "Deploy the environment.",
    'cleanup': "Remove the ESXi VMs and the VCenter, preserver the datastore.",
    'purge': "Remove all the resources.",
}

help_actions = ", ".join(["🔥{k}: {v}".format(k=k, v=v) for k, v in actions.items()])
parser.add_argument('action', type=str, choices=actions.keys(), metavar=None,
                    help=help_actions)
parser.add_argument('--driver', dest='driver', type=str, choices=['libvirt', 'openstack'],
                    help='Driver to use')
parser.add_argument('--prefix', type=str, default="")
parser.add_argument('--run-test', type=bool, default=False)
parser.add_argument('--datastore-distro', type=str, dest="datastore")
parser.add_argument('--esxi-distro', type=str, dest="esxi")
parser.add_argument('--vcenter-distro', type=str, dest="vcenter")


args = parser.parse_args()

if args.driver == 'openstack':
    driver = DriverOpenStack
elif args.driver == 'libvirt':
    driver = DriverLibvirt

getattr(driver, args.action)(args)
