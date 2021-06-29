# mk_deb

Create a debian package with python, faster than dpkg-deb because we can make the gzip compression faster thanks to https://github.com/nix7drummer88/pigz-python

```
git clone https://github.com/bsergean/mk_deb.git
cd mk_deb
python3 -mvenv venv
source venv/bin/activate
pip install pigz_python
python3 test_mk_deb.py
```
