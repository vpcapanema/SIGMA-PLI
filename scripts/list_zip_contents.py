import sys
import zipfile
zf = zipfile.ZipFile(sys.argv[1])
print('\n'.join(zf.namelist()))
