import os
import subprocess

fileList = ['image', 'image.raw', 'mipsel', 'mipseb', 'armel', 'armeb', 'qemu.final.serial.log', 'run.sh', 'serial.log', '.qemu.final.serial.log.swp']

folderwhitelist = ['/dev', '/share']

def log(data):
 f = open('compare_log.txt', 'w')
 f.write(data)
 f.close()

def getimage(tarfile):
 tarfilename = tarfile[:tarfile.find('.tar.gz')]
 for dirname, dirnames, filenames in os.walk('./scratch'):
  for filename in filenames:
    if dirname.endswith(tarfilename) and filename == 'image.raw':
        return os.path.join(dirname, filename)

def checkExist(brand, tarfile, imagefile):
 firmware = tarfile[tarfile.rfind('/') : tarfile.find('.tar.gz')]
 resultDir = 'work/' + brand + firmware

 os.system('mkdir -p compare_work/tar')

 os.system('cp ' + tarfile + ' compare_work/tar/archive.tar.gz')
 os.system('cd compare_work/tar && tar xzf archive.tar.gz')
 os.system('rm compare_work/tar/archive.tar.gz')

 for dirname, dirnames, filenames in os.walk('./compare_work/tar/'):
  for filename in filenames:
    if filename.find('preinit') != -1:
        print '[*] find init file : ' + os.path.join(dirname, filename)
        os.system('mkdir -p ' + resultDir)
        filepath = os.path.join(dirname, filename)
        dstfilepath = resultDir + filepath.replace('./compare_work/tar', '')
        os.system('mkdir -p ' + dstfilepath[:dstfilepath.rfind('/')])
        os.system('cp ' + filepath + ' ' + dstfilepath)

 os.system('rm -rf compare_work')

def compareconf(brand, tarfile, imagefile):
 firmware = tarfile[tarfile.rfind('/') : tarfile.find('.tar.gz')]
 resultDir = 'work/' + brand + firmware
 for dirname, dirnames, filenames in os.walk(imagefile[:imagefile.rfind('/')]):
  for filename in filenames:
    if filename not in fileList:
        print '[*] find config file : ' + os.path.join(dirname, filename)
        os.system('mkdir -p ' + resultDir)
        os.system('cp ' + os.path.join(dirname, filename) + ' ' + resultDir)

def compare(brand, tarfile, imagefile):
 firmware = tarfile[tarfile.rfind('/'):tarfile.find('.tar.gz')]
 resultDir = 'work/' + brand + firmware + '/image'

 os.system('mkdir -p ' + resultDir)
 os.system('mkdir -p compare_work/tar')
 os.system('mkdir -p compare_work/image')

 os.system('cp ' + tarfile + ' compare_work/tar/archive.tar.gz')
 os.system('cd compare_work/tar && tar xzf archive.tar.gz')
 os.system('rm compare_work/tar/archive.tar.gz')

 os.system('cp ' + imagefile + ' compare_work/')
 os.system('kpartx -asv compare_work/image.raw')
 os.system('mount /dev/mapper/loop0p1 compare_work/image')
 for dirname, dirnames, filenames in os.walk('./compare_work/image'):
  if dirname[20:].startswith('/dev') or dirname[20:].startswith('/share') or dirname[20:].startswith('/tmp/dev') or dirname[20:].startswith('/usr/dev'):
    continue
  for filename in filenames:
    if filename.endswith('ttyS1'):
     continue
    rootdir = dirname[20:]
    rootfilepath = os.path.join(rootdir, filename)
    tarfilepath = './compare_work/tar/' + rootfilepath
    imagefilepath = './compare_work/image/' + rootfilepath
    resultfilefolder = resultDir + '/' + rootdir

    if not os.path.exists(tarfilepath):
      os.system('mkdir -p ' + resultfilefolder)
      if os.path.exists(imagefilepath):
       os.system('cp ' + imagefilepath + ' ' + resultfilefolder + '/' + filename + '.new')
    else: # compare hash?
      cmd = 'cmp ' + tarfilepath + ' ' + imagefilepath
      try:
          subprocess.check_output(cmd.split())
      except:
          os.system('mkdir -p ' + resultfilefolder + ' && cp ' + imagefilepath + ' ' + resultfilefolder + '&& diff ' + tarfilepath + ' ' + imagefilepath + ' > ' + resultfilefolder + '/' + filename + '.diff')

 os.system('umount compare_work/image')
 os.system('kpartx -d /dev/loop0')
 os.system('losetup -d /dev/loop0')

 os.system('rm -rf compare_work')

for dirname, dirnames, filenames in os.walk('./images'):
 for filename in filenames:
    if filename.endswith('.tar.gz'):
     imagefile = getimage(filename)
     tarfile = os.path.join(dirname, filename)

     if imagefile == None:
        log("[*] can't found - " + tarfile)
        continue

     idx = tarfile.find('/', 5) + 1
     idx2 = tarfile.find('/', idx)
     brand = tarfile[idx:idx2]
     print '[*] compare now - ' + tarfile
	 #checkExist(brand, tarfile, imagefile)
	 compare(brand, tarfile, imagefile)
	 compareconf(brand, tarfile, imagefile)
