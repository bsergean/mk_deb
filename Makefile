all: indent

indent:
	black mk_deb.py test_mk_deb.py
