import argparse
import os
import re


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
    INIT_FILE = os.path.join(ROOT_PATH, "melogger/__init__.py")
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
    init_content = open(INIT_FILE, 'r').read()
    version_line = re.findall('(^VERSION *= *)([\'"])(.+)(\\2)', init_content, flags=re.MULTILINE)[0]
    new_version = increment_version(
        version_line[2],
        is_major=args.major,
        is_minor=args.minor,
        is_patch=args.patch
    )
    try:
        # Cleanup old files
        old_dirs_path = ['build', 'dist', f'{PACKAGE_NAME}.egg-info']
        old_dirs_path = list(filter(lambda x: os.path.isdir(os.path.join(ROOT_PATH, x)), old_dirs_path))
        if len(old_dirs_path) > 0:
            print("Cleaning old directories:")
            [os.system('cd "{0}" && test -d {1} && rm -rf {1}'.format(ROOT_PATH, crt_dir)) for crt_dir in old_dirs_path]

        # Uninstalling package locally
        if args.install:
            print("Uninstalling old version...")
            os.system(f'pip3 uninstall -y {PACKAGE_NAME}')

        # Persist new version
        open(INIT_FILE, 'w').writelines(re.sub(''.join(version_line), ''.join(list(version_line[:2]) + [new_version] + [version_line[-1]]), init_content))

        # Install package locally
        if args.install:
            print("\nInstalling new version...")
            ret_code = os.system(f'cd "{ROOT_PATH}" && pip3 install .')
            if ret_code != 0:
                print(f"\033[33m[WARNING]\033[0m Installation of {PACKAGE_NAME} {new_version} failed")
            else:
                print(f"\033[32m[BUILD SUCCESS]\033[0m Version {new_version} successfully installed.")

    except Exception as e:
        print(f"\033[31m[BUILD FAILED]\033[0m {e}")
        open(INIT_FILE, 'w').writelines(init_content)
