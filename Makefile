
.PHONY: clean
clean:
	-rm -rf build dist webim.egg-info htmlcov .eggs

publish:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*

upload: clean publish
