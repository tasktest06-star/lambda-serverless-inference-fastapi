import * as path from 'path';
import { Size, Duration, Stack, StackProps, RemovalPolicy } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb'; // <-- Added import

export class FastapiModelServingStacktsStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // 1. Create the DynamoDB table to store API responses
    const responseTable = new dynamodb.Table(this, 'ApiResponseTable', {
      tableName: 'FastApiResponses',
      partitionKey: { name: 'requestId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY, // Change to RETAIN for production
    });

    // Docker-based Lambda function with 4GB Ephemeral Storage and 2GB RAM[cite: 1]
    const fastapiModelEndpointLambda = new lambda.DockerImageFunction(
      this,
      'fastapi_model_serving_endpoint',
      {
        functionName: 'fastapi_model_serving_endpoint_docker', //[cite: 1]
        architecture: lambda.Architecture.X86_64, //[cite: 1]
        code: lambda.DockerImageCode.fromImageAsset(
          path.join(__dirname, '..', 'model_endpoint', 'docker') //[cite: 1]
        ),
        timeout: Duration.seconds(60), //[cite: 1]
        ephemeralStorageSize: Size.mebibytes(4096), //[cite: 1]
        memorySize: 2048, //[cite: 1]
        // 2. Pass the Table Name as an environment variable to FastAPI
        environment: {
          RESPONSE_TABLE_NAME: responseTable.tableName,
        },
      }
    );

    // 3. Grant Lambda write permissions to the DynamoDB table
    responseTable.grantWriteData(fastapiModelEndpointLambda);

    // REST API Gateway acting as a proxy to route all traffic to FastAPI[cite: 1]
    new apigateway.LambdaRestApi(this, 'docker_model_serving_endpoint', { //[cite: 1]
      handler: fastapiModelEndpointLambda, //[cite: 1]
      proxy: true, //[cite: 1]
    });
  }
}
