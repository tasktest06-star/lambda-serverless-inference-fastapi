import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as path from 'path';

export class FastapiModelServingStacktsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 1. S3 Bucket for Training Data
    const trainingDataBucket = new s3.Bucket(this, 'TrainingDataBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY, 
    });

    // 2. DynamoDB Table for API Responses
    const responseTable = new dynamodb.Table(this, 'ApiResponseTable', {
      partitionKey: { name: 'requestId', type: dynamodb.AttributeType.STRING },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // 3. Lambda Docker Image Function
    const modelServingLambda = new lambda.DockerImageFunction(this, 'ModelServingFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../app')),
      memorySize: 1024, 
      timeout: cdk.Duration.seconds(30), 
      environment: {
        TRAINING_DATA_BUCKET: trainingDataBucket.bucketName,
        TRAINING_DATA_KEY: 'model.pkl', // Updated to point to the weights file
        RESPONSE_TABLE_NAME: responseTable.tableName,
      },
    });

    // Grant IAM Permissions
    trainingDataBucket.grantRead(modelServingLambda);
    responseTable.grantWriteData(modelServingLambda);

    // 4. API Gateway
    new apigateway.LambdaRestApi(this, 'ModelServingApi', {
      handler: modelServingLambda,
      proxy: true, 
    });
  }
}
