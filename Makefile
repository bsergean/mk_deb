all: indent

indent:
	black -S mk_deb.py test_mk_deb.py

test:
	python3 test_mk_deb.py
