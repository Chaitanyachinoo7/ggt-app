import glob, shutil

for file_path in glob.glob('/tmp/ggt-tasks/downloads/*.pdf'):
  arr = file_path.split('/')
  filename = arr[len(arr)-1]

  shutil.move(file_path, '/tmp/ggt-tasks/downloads/PDF-REPORTS/ ' + filename)
