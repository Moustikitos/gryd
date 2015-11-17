# -*- coding:utf-8 -*-
"""
Create a binary wheel (.whl) distribution (no source file).
"""
from distutils import log as logger
from shutil import rmtree
__version__ = "1.0.0"

try:
    import sysconfig
except ImportError:  # pragma nocover
    # Python < 2.7
    import distutils.sysconfig as sysconfig

from wheel import bdist_wheel
import os, sys, compileall

class wheel(bdist_wheel.bdist_wheel):
	"""
	"""

	boolean_options = bdist_wheel.bdist_wheel.boolean_options + ['no-src']
	user_options = bdist_wheel.bdist_wheel.user_options + [
		('src-ext=', None, "coma-separated list of extension source file to delete from the distribution", " (default: 'py,pyw')")
	]

	def write_wheelfile(self, wheelfile_base, generator='bindist_wheel (' + __version__ + ')'):
		return bdist_wheel.bdist_wheel.write_wheelfile(self, wheelfile_base, generator=generator)

	def initialize_options(self):
		bdist_wheel.bdist_wheel.initialize_options(self)
		self.src_ext = 'py,pyw'

	def finalize_options(self):
		bdist_wheel.bdist_wheel.finalize_options(self)
		self.src_ext = self.src_ext.split(",")

	# def get_tag(self):
	# 	supported_tags = bdist_wheel.pep425tags.get_supported()

	# 	if self.plat_name is None and self.distribution.is_pure():
	# 		if self.universal:
	# 			impl = 'py2.py3'
	# 		else:
	# 			impl = self.python_tag
	# 		tag = (impl, 'none', 'any')
	# 	else:
	# 		plat_name = self.plat_name
	# 		if plat_name is None:
	# 			plat_name = bdist_wheel.get_platform()
	# 		plat_name = plat_name.replace('-', '_').replace('.', '_')
	# 		impl_name = bdist_wheel.get_abbr_impl()
	# 		impl_ver = bdist_wheel.get_impl_ver()
	# 		# PEP 3149 -- no SOABI in Py 2
	# 		# For PyPy?
	# 		# "pp%s%s" % (sys.pypy_version_info.major,
	# 		# sys.pypy_version_info.minor)
	# 		abi_tag = sysconfig.get_config_vars().get('SOABI', 'none')
	# 		if abi_tag.startswith('cpython-'):
	# 			abi_tag = 'cp' + abi_tag.rsplit('-', 1)[-1]

	# 		tag = (impl_name + impl_ver, abi_tag, plat_name)
	# 		# XXX switch to this alternate implementation for non-pure:
	# 		assert tag == supported_tags[0]
	# 	return tag

	def remove_sources(self):
		logger.info('Compyling python files')
		if sys.version[0] >= "3":
			import functools
			reduce = functools.reduce
			compileall.compile_dir(self.bdist_dir, legacy=True, optimize=2)
		else:
			compileall.compile_dir(self.bdist_dir)

		logger.info('Removing %s source file from %s' % (",".join(["*."+e+" " for e in self.src_ext]), self.bdist_dir))
		for ext in self.src_ext:
			if sys.platform.startswith("win"):
				os.system(r'del "%s\*.%s" /S' % (self.bdist_dir, ext))
			elif sys.platform.startswith("linux"):
				os.system('find "./%s" -name "*.%s" -delete' % (self.bdist_dir, ext))
			else:
				logger.info('--> source file can not be deleted')

	def run(self):
		build_scripts = self.reinitialize_command('build_scripts')
		build_scripts.executable = 'python'

		if not self.skip_build:
			self.run_command('build')

		install = self.reinitialize_command('install', reinit_subcommands=True)
		install.root = self.bdist_dir
		install.compile = False
		install.skip_build = self.skip_build
		install.warn_dir = False

		# A wheel without setuptools scripts is more cross-platform.
		# Use the (undocumented) `no_ep` option to setuptools'
		# install_scripts command to avoid creating entry point scripts.
		install_scripts = self.reinitialize_command('install_scripts')
		install_scripts.no_ep = True

		# Use a custom scheme for the archive, because we have to decide
		# at installation time which scheme to use.
		for key in ('headers', 'scripts', 'data', 'purelib', 'platlib'):
			setattr(install, 'install_' + key, os.path.join(self.data_dir, key))

		basedir_observed = ''

		if os.name == 'nt':
			# win32 barfs if any of these are ''; could be '.'?
			# (distutils.command.install:change_roots bug)
			basedir_observed = os.path.join(self.data_dir, '..')
			self.install_libbase = self.install_lib = basedir_observed

		try:
			setattr(install,
				'install_purelib' if self.root_is_purelib else 'install_platlib',
				basedir_observed)
		except:
			setattr(install, 'install_platlib', basedir_observed)

		logger.info("installing to %s", self.bdist_dir)

		self.run_command('install')

		archive_basename = self.get_archive_basename()

		pseudoinstall_root = os.path.join(self.dist_dir, archive_basename)
		if not self.relative:
			archive_root = self.bdist_dir
		else:
			archive_root = os.path.join(
				self.bdist_dir,
				self._ensure_relative(install.install_base)
			)

		self.remove_sources()
		
		self.set_undefined_options('install_egg_info', ('target', 'egginfo_dir'))
		self.distinfo_dir = os.path.join(self.bdist_dir, '%s.dist-info' % self.wheel_dist_name)
		self.egg2dist(self.egginfo_dir, self.distinfo_dir)
		self.write_wheelfile(self.distinfo_dir)
		self.write_record(self.bdist_dir, self.distinfo_dir)

		# Make the archive
		if not os.path.exists(self.dist_dir):
			os.makedirs(self.dist_dir)
		wheel_name = bdist_wheel.archive_wheelfile(pseudoinstall_root, archive_root)

		# Sign the archive
		if 'WHEEL_TOOL' in os.environ:
			subprocess.call([os.environ['WHEEL_TOOL'], 'sign', wheel_name])

		# Add to 'Distribution.dist_files' so that the "upload" command works
		getattr(self.distribution, 'dist_files', []).append(
			('bdist_wheel', bdist_wheel.get_python_version(), wheel_name)
		)

		if not self.keep_temp:
			if self.dry_run:
				logger.info('removing %s', self.bdist_dir)
			else:
				rmtree(self.bdist_dir)
