test:
	py.test --cov-report=html --cov-report=xml --cov=pepper

diff-cover: test
	diff-cover coverage.xml --compare-branch=origin/master --html-report DiffCovReport.html --fail-under=100	
