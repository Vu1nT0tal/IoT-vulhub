import os

def Read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except:
        return 'None'

results = {}

SCRATCH_DIR = ''

for i in xrange(3):
    if os.path.exists('../' * i + 'firmae.config'):
        SCRATCH_DIR = '../' * i + 'scratch'

for roots, dirs, files in os.walk(SCRATCH_DIR):
    for iid in dirs:
        path = SCRATCH_DIR + '/' + iid + '/'
        name = Read(path + 'name')
        arch = Read(path + 'architecture')
        ip = Read(path + 'ip')
        ping = Read(path + 'ping')
        web = Read(path + 'web')
        results[int(iid)] = iid + '___' + name + '___' + arch + '___' + ip + '___' + ping + '___' + web
    break

outfile = open('result.txt', 'w')

outfile.write('Number___Name___Arch___ip___ping___web\n')
for i in sorted(results):
    outfile.write(results[i] + '\n')

outfile.close()
