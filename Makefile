S3BucketName ?= my-bucket


clean:
	rm -rf .aws-sam

first-deploy:
	sam build
	sam deploy --guided

deploy:
	sam build
	sam deploy

config-sync: clean
	sam local invoke ConfigSync -e events/forward_mapping.json --parameter-overrides S3BucketName=$(S3BucketName)
