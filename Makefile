clean:
	rm -rf .aws-sam

deploy:
	sam build
	sam deploy --guided
