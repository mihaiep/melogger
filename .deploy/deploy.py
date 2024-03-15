import argparse
import os


def increment_version(_version, is_major, is_minor, is_patch):
	major, minor, patch = _version.split('.')
	if is_major:
		major = int(major) + 1
		minor, patch = 0, 0
	if is_minor:
		minor = int(minor) + 1
		patch = 0
	if is_patch:
		patch = int(patch) + 1
	return f'{major}.{minor}.{patch}'


if __name__ == '__main__':
	ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
	SETUP_PATH = os.path.join(ROOT_PATH, "setup.py")
	VERSION_PATH = os.path.join(ROOT_PATH, ".deploy/version.txt")
	SETUP_SOURCE_PATH = os.path.join(ROOT_PATH, ".deploy/setup.txt")
	PACKAGE_NAME = os.path.basename(ROOT_PATH)

	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('-M', '--major', action="store_true", default=False)
	arg_parser.add_argument('-m', '--minor', action="store_true", default=False)
	arg_parser.add_argument('-p', '--patch', action="store_true", default=False)
	arg_parser.add_argument('-i', '--install', action="store_true", default=False)
	args = arg_parser.parse_args()

	if not (args.major or args.minor or args.patch):
		print("No flags enabled. Deployment canceled.")
		exit(1)

	# Calculate new version and update setup.py
	crt_version = open(VERSION_PATH, 'r').read()
	version = increment_version(
		crt_version,
		is_major=args.major,
		is_minor=args.minor,
		is_patch=args.patch
	)
	try:
		open(SETUP_PATH, 'w').write(open(SETUP_SOURCE_PATH, 'r').read().format(version=version))

		# Cleanup old files
		old_dirs_path = ['build', 'dist', f'{PACKAGE_NAME}.egg-info']
		old_dirs_path = list(filter(lambda x: os.path.isdir(os.path.join(ROOT_PATH,x)), old_dirs_path))
		if len(old_dirs_path) > 0:
			print("Cleaning old directories:")
			[os.system('cd "{0}" && test -d {1} && rm -rf {1}'.format(ROOT_PATH, crt_dir)) for crt_dir in old_dirs_path]

		# Uninstalling package locally
		if args.install:
			print("Uninstalling old version...")
			os.system(f'pip3 uninstall -y {PACKAGE_NAME}')

		# Deploy package
		ret_code = os.system(f'cd "{ROOT_PATH}" && python3 setup.py sdist bdist_wheel')
		if ret_code != 0:
			raise Exception("Error occurred while deploying")
		else:
			open(VERSION_PATH, 'w').write(version)
			print(f"\033[32m[BUILD SUCCESS]\033[0m Version {version} successfully deployed.")

		# Install package locally
		if args.install:
			print("\nInstalling new version...")
			ret_code = os.system(f'cd "{ROOT_PATH}" && pip3 install .')
			if ret_code != 0:
				print(f"\033[33m[WARNING]\033[0m Installation of {PACKAGE_NAME} {version} failed")
			else:
				print(f"\033[32m[BUILD SUCCESS]\033[0m Version {version} successfully installed.")

	except FileNotFoundError:
		print("\033[31m[BUILD FAILED]\033[0m Setup template was not found: .deploy/setup.txt")
		exit(10)
	except Exception as e:
		print(f"\033[31m[BUILD FAILED]\033[0m {e}")
		open(SETUP_PATH, 'w').write(open(SETUP_SOURCE_PATH, 'r').read().format(version=crt_version))
