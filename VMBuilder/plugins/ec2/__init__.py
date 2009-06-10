#
#    Uncomplicated VM Builder
#    Copyright (C) 2007-2008 Canonical Ltd.
#    
#    See AUTHORS for list of contributors
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from VMBuilder import register_plugin, Plugin, VMBuilderUserError
from VMBuilder.util import run_cmd
import logging

class EC2(Plugin):
    name = 'EC2 integration'

    def register_options(self):
        group = self.vm.setting_group('EC2 integation')
        group.add_option('--ec2', action='store_true', help='Build for EC2')
        group.add_option('--ec2-name','--ec2-prefix', metavar='EC2_NAME', help='Name for the EC2 image.')
        group.add_option('--ec2-cert', metavar='CERTFILE', help='PEM encoded public certificate for EC2.')
        group.add_option('--ec2-key', metavar='KEYFILE', help='PEM encoded private key for EC2.')
        group.add_option('--ec2-user', metavar='AWS_ACCOUNT', help='EC2 user ID (a.k.a. AWS account number, not AWS access key ID).')
        group.add_option('--ec2-bucket', metavar='BUCKET', help='S3 bucket to hold the AMI.')
        group.add_option('--ec2-access-key', metavar='ACCESS_ID', help='AWS access key ID.')
        group.add_option('--ec2-secret-key', metavar='SECRET_ID', help='AWS secret access key.')
        group.add_option('--ec2-kernel','--ec2-aki', metavar='AKI', help='EC2 AKI (kernel) to use.')
        group.add_option('--ec2-ramdisk','--ec2-ari', metavar='ARI', help='EC2 ARI (ramdisk) to use.')
	group.add_option('--ec2-version',metavar='EC2_VER',help='Specifity the EC2 image version.')
        self.vm.register_setting_group(group)

    def preflight_check(self):
        if not self.vm.ec2:
            return True

        if not self.vm.hypervisor.name == 'Xen':
            raise VMBuilderUserError('When building for EC2 you must use the xen hypervisor.')

        if not self.vm.ec2_name:
            raise VMBuilderUserError('When building for EC2 you must supply the name for the image.')

        if not self.vm.ec2_cert:
            raise VMBuilderUserError('When building for EC2 you must provide your PEM encoded public key certificate')

        if not self.vm.ec2_key:
            raise VMBuilderUserError('When building for EC2 you must provide your PEM encoded private key file')

        if not self.vm.ec2_user:
            raise VMBuilderUserError('When building for EC2 you must provide your EC2 user ID (your AWS account number, not your AWS access key ID)')

        if not self.vm.ec2_kernel:
            logging.debug('No ec2-aki choosen setting to default. Use --ec2-kernel to change this')
	    if self.vm.suite == 'hardy':
               if self.vm.arch == 'amd64':
	          self.vm.ec2_kernel = 'aki-6f709706'
	       else:
	          self.vm.ec2_kernel = 'aki-6e709707'
	    elif self.vm.suite == 'intrepid':
	        if self.vm.arch == 'amd64':
                   self.vm.ec2_kernel = 'aki-4f4daa26'
	        else: 
	           self.vm.ec2_kernel = 'aki-714daa18' 
	    elif self.vm.suite == 'jaunty':
                if self.vm.arch == 'amd64':
                    self.vm.ec2_kernel = 'aki-6507e00c'
                else:
	            self.vm.ec2_kernel = 'aki-6407e00d'

        logging.info('%s - AKI to be used.' %(self.vm.ec2_kernel))
	logging.info('WARNING! You might be using an outdated AKI. Please check xxx')

        if not self.vm.ec2_ramdisk:
            logging.debug('No ec2-ari choosen setting to default. Use --ec2-ramdisk to change this.')
	    if self.vm.suite == 'hardy':
              if self.vm.arch == 'amd64':
                 self.vm.ec2_ramdisk = 'ari-61709708'
              else:
                 self.vm.ec2_ramdisk = 'ari-6c709705'
	    elif self.vm.suite == 'intrepid':
                if self.vm.arch == 'amd64':
                   self.vm.ec2_ramdisk = 'ari-4c4daa25' 
                else:
                   self.vm.ec2_ramdisk = 'ari-7e4daa17'
	    elif self.vm.suite == 'jaunty':
                if self.vm.arch == 'amd64':
	           self.vm.ec2_ramdisk = 'ari-6307e00a'
                else:
	           self.vm.ec2_ramdisk = 'ari-6207e00b'

	logging .info('%s - ARI to be used.'%(self.vm.ec2_ramdisk))
	logging.info('WARNING! You might be using an outdated AKI. Please check xxx')

        if not self.vm.ec2_bucket:
            raise VMBuilderUserError('When building for EC2 you must provide an S3 bucket to hold the AMI')

        if not self.vm.ec2_access_key:
            raise VMBuilderUserError('When building for EC2 you must provide your AWS access key ID.')

        if not self.vm.ec2_secret_key:
            raise VMBuilderUserError('When building for EC2 you must provide your AWS secret access key.')

	logging.info('Installing common software')
	self.install_common()
	if self.vm.suite == 'hardy':
             self.install_hardy()
	elif self.vm.suite == 'intrepid':
              self.install_intrepid()
	elif self.vm.suite == 'jaunty':
              self.install_jaunty()

    def post_install(self):
        if not self.vm.ec2:
            return

        logging.info("Running ec2 postinstall")
	logging.info("Running common post install")
	if self.vm.suite == 'hardy':
	     self.postinstall_hardy()
	elif self.vm.suite == 'intrepid':
	     self.postinstall_intrepid()
	elif self.vm.suite == 'jaunty':
	     self.postinstall_jaunty()
	self.postinstall_common()

    def deploy(self):
        if not self.vm.ec2:
            return False

        bundle_cmdline = ['ec2-bundle-image', '--image', self.vm.filesystems[0].filename, '--cert', self.vm.ec2_cert, '--privatekey', self.vm.ec2_key, '--user', self.vm.ec2_user, '--prefix', self.vm.ec2_name, '-r', ['i386', 'x86_64'][self.vm.arch == 'amd64'], '-d', self.vm.workdir, '--kernel', self.vm.ec2_kernel, '--ramdisk', self.vm.ec2_ramdisk]

        run_cmd(*bundle_cmdline)

        upload_cmdline = ['ec2-upload-bundle', '--retry', '--manifest', '%s/%s.manifest.xml' % (self.vm.workdir, self.vm.ec2_name), '--bucket', self.vm.ec2_bucket, '--access-key', self.vm.ec2_access_key, '--secret-key', self.vm.ec2_secret_key]
        run_cmd(*upload_cmdline)

        from boto.ec2.connection import EC2Connection
        conn = EC2Connection(self.vm.ec2_access_key, self.vm.ec2_secret_key)
        print conn.register_image('%s/%s.manifest.xml' % (self.vm.ec2_bucket, self.vm.ec2_name))

        return True

    def install_common(self):
        if not self.vm.ec2:
            return False

	if not self.vm.addpkg:
	    self.vm.addpkg = []

	logging.info('Installing common software.')
	self.vm.addpkg += ['openssh-server', 
                           'ec2-init', 
                           'standard^',
		           'ec2-ami-tools',
                           'update-motd',
                           'curl',
                           'screen',
                           'screen-profiles']

	if not self.vm.ppa:
	    self.vm.ppa = []

        self.vm.ppa += ['ubuntu-on-ec2']

    def install_hardy(self):
	if not self.vm.ec2:
	    return False

	logging.info('Installing software for hardy.')
	self.vm.addpkg += ['ruby',
			   'libc6-xen',
			   'ec2-modules',
			   'libopenssl-ruby',
			   'landscape-common',
			   'landscape-client']


    def postinstall_hardy(self):
	if not self.vm.ec2:
	    return False

	logging.info('Running post-install for hardy')
	# work around for libc6/xen bug in hardy.
	self.install_from_template('/etc/ld.so.conf.d/libc6-xen.conf', 'xen-ld-so-conf')
	self.run_in_target('apt-get', 'remove', '-y', 'libc6-i686')

	self.install_from_template('/etc/update-motd.d/51_update-motd', '51_update-motd-hardy')
	self.install_from_template('/etc/event.d/xvc0', 'xvc0')
	self.run_in_target('update-rc.d', '-f', 'hwclockfirst.sh', 'remove')

    def install_intrepid(self):
	if not self.vm.ec2:
	    return False

	logging.info('Installing software for intrepid')
	self.vm.addpkg += ['ec2-modules',
			   'ruby',
			   'libopenssl-ruby',
                           'server^',
                           'policykit',
			   'landscape-common',
			   'landscape-client']

    def postinstall_intrepid(self):
	if not self.vm.ec2:
	    return False

	logging.info('Running post-install for intrepid')
	self.install_from_template('/etc/update-motd.d/51_update-motd', '51_update-motd-intrepid')

    def install_jaunty(self):
	if not self.vm.ec2:
	    return False

	logging.info('Installing software for jaunty')
	self.vm.addpkg += ['ec2-modules',
			   'ruby1.8',
                           'server^',
			   'libopenssl-ruby1.8']

    def postinall_jaunty(self):
	if not self.vm.ec2:
            return False
	
	logging.info('Running post-install for jaunty') 
	self.install_from_template('/etc/update-motd.d/51_update-motd', '51_update-motd-intrepid')

    def postinstall_common(self):
	if not self.vm.ec2:
	    return False

	logging.info('Running common post-install')
	self.install_from_template('/etc/ssh/sshd_config', 'sshd_config')
	self.run_in_target('chpasswd', '-e', stdin='ubuntu:!\n')
	# this makes my skin crawl
	self.install_from_template('/etc/sudoers', 'sudoers')
	# this doesnt
	self.run_in_target('chmod', '755', '/etc/update-motd.d/51_update-motd')
	self.install_from_template('/etc/ec2_version', 'ec2_version', { 'version' : self.vm.ec2_version })

	self.run_in_target('rm', '-f', '/etc/localtime')
	self.run_in_target('ln', '-s', '/usr/share/zoneinfo/UTC', '/etc/localtime')

	self.run_in_target('usermod', '-u', '135', 'ubuntu')
	self.run_in_target('chown', '-R', 'ubuntu', '/home/ubuntu')

	self.run_in_target('update-rc.d', '-f', 'hwclock.sh', 'remove') 
	self.install_from_template('/etc/default/landscape-client', 'landscape_client')

register_plugin(EC2)
