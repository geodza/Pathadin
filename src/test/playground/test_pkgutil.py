import pkgutil

if __name__ == '__main__':
	pkgs = list(pkgutil.walk_packages('.'))
	print(pkgs)

	pkgs = list(pkgutil.iter_modules('.'))
	print(pkgs)
