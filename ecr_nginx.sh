IMAGE_NAME=ecr_nginx

docker build -f nginx_dockerfile -t ${IMAGE_NAME} .

REGION=us-east-1
ACCOUNT=$(aws --profile personal sts get-caller-identity --query Account --output text)

aws --profile personal ecr create-repository --repository-name ${IMAGE_NAME} --region=us-east-1 > /dev/null 2>&1

REPOSITORY_NAME=${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE_NAME}:latest

docker tag ${IMAGE_NAME} ${REPOSITORY_NAME}

$(aws --profile personal ecr get-login --no-include-email --region=us-east-1)

docker push ${REPOSITORY_NAME}
