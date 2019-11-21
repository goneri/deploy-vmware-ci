#!/usr/bin/env python3

import argparse
import subprocess

class DriverOpenStack:

    @staticmethod
    def cleanup(args):
        subprocess.call(["ansible-playbook", "openstack/playbooks/clean.yaml", "-e", "prefix=%s" % args.prefix])

    @staticmethod
    def purge(args):
        subprocess.call(["ansible-playbook", "openstack/playbooks/purge.yaml", "-e", "prefix=%s" % args.prefix])

    @staticmethod
    def deploy(args):
        subprocess.call(["ansible-playbook", "openstack/playbooks/deploy.yaml", "-i", "openstack/inventory/openstack.yaml", "-e", "prefix=%s" % args.prefix])
        if args.run_test:
            subprocess.call(["ansible-playbook", "-vv", "playbooks/run_test.yaml", "-i", "openstack/inventory/openstack.yaml", "-e", "prefix=%s" % args.prefix])

class DriverLibvirt:

    @staticmethod
    def cleanup(args):
        for i in ["esxi1", "esxi2", "vcenter"]:
            subprocess.call(["vl", "stop", i])

    @staticmethod
    def purge(args):
        subprocess.call(["vl", "down"])

    @staticmethod
    def deploy(args):
        subprocess.call(["vl", "up", "--virt-lightning-yaml", "libvirt/virt-lightning.yaml"])
        subprocess.call("vl ansible_inventory>inventory", shell=True)
        subprocess.call(["ansible-playbook", "libvirt/playbooks/prepare_datastore.yaml", "-i", "inventory"])
        if args.run_test:
            subprocess.call(["ansible-playbook", "-vv", "playbooks/run_test.yaml", "-i", "inventory", "-e", "prefix=%s" % args.prefix])


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


args = parser.parse_args()

if args.driver == 'openstack':
    driver = DriverOpenStack
elif args.driver == 'libvirt':
    driver = DriverLibvirt

getattr(driver, args.action)(args)
