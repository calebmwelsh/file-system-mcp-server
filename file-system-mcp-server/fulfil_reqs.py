import subprocess

# ---- installs pipreqs, creates reqs file, and installs reqs ---- #
try:
	# install pipreqs
	subprocess.run("pip install pipreqs", shell=True, check=True)
	# create requirement file
	subprocess.run("pipreqs --encoding=utf8 --force", shell=True, check=True)
	# install reqs
	subprocess.run("pip install -r requirements.txt", shell=True, check=True)
except subprocess.CalledProcessError as e:
	print(e)
	if str(e) == "Command 'pip install pipreqs' returned non-zero exit status 127.":
		# install pipreqs
		subprocess.run("pip3 install pipreqs", shell=True, check=True)
		# create requirement file
		subprocess.run("pipreqs --encoding=utf8 --force", shell=True, check=True)
		# install reqs
		subprocess.run("pip3 install -r requirements.txt", shell=True, check=True)

