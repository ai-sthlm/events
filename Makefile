.PHONY: build check serve

build:
	python3 build.py

check:
	python3 build.py --check

serve: build
	# http://localhost:8000/
	python3 -m http.server 8000 --directory dist


t:
	python3 scripts/test_telegram.py
