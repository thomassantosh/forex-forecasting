install:
	pip install --upgrade pip
	pip install jedi
	pip install pynvim
	pip install pandas-datareader
	pip install yfinance

setup_run:
	./setup/create-resources.sh
	#./setup/create_cluster.sh
