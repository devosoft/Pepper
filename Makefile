test:
	py.test --cov-report=html --cov-report=xml --cov=pepper

diff-cover: test
	diff-cover coverage.xml --compare-branch=origin/master --fail-under=100	
