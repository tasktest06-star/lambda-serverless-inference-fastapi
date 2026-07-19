import * as path from 'path';
import { Size, Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class FastapiModelServingStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Docker-based Lambda function with 4GB Ephemeral Storage and 2GB RAM
    const fastapiModelEndpointLambda = new lambda.DockerImageFunction(
      this,
      'fastapi_model_serving_endpoint',
      {
        functionName: 'fastapi_model_serving_endpoint_docker',
        architecture: lambda.Architecture.X86_64,
        code: lambda.DockerImageCode.fromImageAsset(
          path.join(__dirname, '..', 'model_endpoint', 'docker')
        ),
        timeout: Duration.seconds(60),
        ephemeralStorageSize: Size.mebibytes(4096),
        memorySize: 2048,
      }
    );

    // REST API Gateway acting as a proxy to route all traffic to FastAPI
    new apigateway.LambdaRestApi(this, 'docker_model_serving_endpoint', {
      handler: fastapiModelEndpointLambda,
      proxy: true,
    });
  }
}