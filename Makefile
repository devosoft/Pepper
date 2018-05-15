test:
	py.test -vv --cov-report=html --cov-report=xml --cov=pepper

typecheck:
	echo "Reminder: mypy config in setup.cfg" && mypy --strict --ignore-missing-import src/pepper/*.py

diff-cover: test
	diff-cover coverage.xml --compare-branch=origin/master --html-report DiffCovReport.html --fail-under=100

diff-quality:
	diff-quality --compare-branch=origin/master --violations=flake8 --fail-under=100

push-check: diff-cover typecheck diff-quality
	echo "Yay!"

doc-html:
	cd docs/sphinx && make html
