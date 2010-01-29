#!/usr/bin/python

from distutils.core import setup
import VMBuilder.plugins
import os
import subprocess

if os.path.exists('.bzr'):
    try:
        o = subprocess.Popen(('bzr','version-info', '--python'), stdout=subprocess.PIPE).stdout
        f = open('VMBuilder/vcsversion.py', 'w')
        f.write(o.read())
        f.close()
        o.close()
    except Exception, e:
        print repr(e)

vmbuilder_data = []

for p in VMBuilder.plugins.find_plugins():
    for pkg in [p.split('.')[-1]]:
        vmbuilder_data.extend(['/etc/vmbuilder/%s' % (pkg,)])
        
        for root, dirs, files in os.walk('VMBuilder/plugins/%s/templates' % (pkg,)):
            for filename in files:
                vmbuilder_data.append(os.path.join(root, filename))

setup(name='VMBuilder',
      version='0.11',
      description='Uncomplicated VM Builder',
      author='Soren Hansen',
      author_email='soren@canonical.com',
      url='http://launchpad.net/vmbuilder/',
      packages=['VMBuilder', 'VMBuilder.plugins'] + VMBuilder.plugins.find_plugins(),
      data_files=vmbuilder_data,
      scripts=['vmbuilder'], 
      )
