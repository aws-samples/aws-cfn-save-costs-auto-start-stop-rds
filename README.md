## Automate Start and Stop of Amazon RDS Instances to Save costs

Saving money is a top priority for any AWS user. You can save money by manually shutting down your servers when they’re not in use. However, manually managing and administering multiple servers is quite difficult and time-consuming. This script offers a solution to automate the server stop and start procedure by scheduling with either a fixed time, a flexible time, or both. 

You can stop your instances during non-working hours and start them during working hours by scheduling them automatically with minimal configuration. The solution also requires a one-time configuration of Amazon RDS tags. 

You’re only charged for the hours when the services are running. This solution can help cut your operational costs by stopping resources that are not in use and starting resources when capacity is required.  You can follow either implementing CloudFormation (CFN) template or Serverless (SAM) template as explained below.

### CloudFormation (CFN) template -
The CloudFormation template <code>cfn_auto_start_stop_rds/cfn_auto_start_stop_rds.yaml</code> automatically creates all the AWS resources required for the Amazon RDS solution to function. Complete the following steps to create your AWS resources via the CloudFormation template:

1.	On the AWS CloudFormation console, choose Create stack.
2.	Choose With new resources (standard).
3.	Choose Template is ready and choose Upload a template file.
4.	Upload the provided .yaml file and choose Next.
5.	For Stack name, enter cfn-auto-start-stop-rds.
6.	Modify the parameter values that set the default cron schedule as needed. 
7.	For RegionTZ, choose which Region time zone to use. This is the TimeZone of the Region in which your RDS instances are deployed and you want to set timings convenient to that particular Timezone.
8.	Choose Next and provide tags, if needed.
9.	Choose Next and review the stack details.
10.	Select the acknowledgement check box because this template creates an IAM role and policy.
11.	Choose Create stack. 
12.	Open the stack and navigate to the Resources tab to track the resource creation status. 

To delete all the resources created via this template, choose the stack on the AWS CloudFormation console and choose Delete. Choose Delete stack to confirm the stack deletion.

### AWS Serverless (SAM) template -
The AWS SAM template <code>sam_auto_start_stop_rds/sam_auto_start_stop_rds.yaml</code> automatically creates all the AWS resources required for the Amazon RDS solution to function. Complete the following steps to deploy this template:

1.	Open a command prompt.
2.	Install the AWS SAM CLI, if not installed.
3.	Create a private Amazon S3 bucket in the Region where you want to create resources; e.g., an S3 bucket named <code>aws-sam-save-costs-auto-start-stop-rds</code> in <code>us-west-1</code>.
4.	Use the AWS SAM CLI command sam deploy to deploy the template and create all the resources: 

        sam deploy --template-file <sam_auto_start_stop_rds.yaml file> --s3-bucket <bucket name> --capabilities CAPABILITY_IAM --region <region where bucket is created> --stack-name <cloudformation stack name>
    e.g. : 
    
        sam deploy --template-file sam_auto_start_stop_rds.yaml --s3-bucket aws-sam-save-costs-auto-start-stop-rds --capabilities CAPABILITY_IAM --region us-west-1 --stack-name sam-auto-start-stop-rds
  
5. The command prompt displays the deployment status of <code>CloudFormation stack changeset</code> and <code>CloudFormation events from stack operations</code>. You can also open the stack on the AWS CloudFormation console and navigate to the Resources tab to track the resource creation status.

To delete all the resources created via this template, use the AWS SAM CLI command sam delete: 

    sam delete --stack-name <cloudformation stack name> --region <region where bucket is created>

e.g. :

    sam delete --stack-name sam-auto-start-stop-rds --region us-west-1


### Features
We use the following high-level features to configure and implement this solution:

*	Tags – Configure 6 predefined tags in Amazon RDS:
    *	AutoStart – Set value as <code>True</code> or <code>False</code> (case insensitive) with a schedule set in the auto start rule
    *	AutoStop – Set value as <code>True</code> or <code>False</code> (case insensitive) with a schedule set in the auto stop rule
    * StartWeekDay – Set value in HH:MM to start on a weekday (Monday to Friday)
    * StopWeekDay – Set value in HH:MM to stop on a weekday (Monday to Friday)
    *	StartWeekEnd – Set value in HH:MM to start on a weekend (Saturday to Sunday)
    *	StopWeekEnd – Set value in HH:MM to stop on a weekend (Saturday to Sunday)
*	Lambda – Configure 6 Lambda functions:
    *	Auto start (AutoStartRDSInstance)
    *	Auto stop (AutoStopRDSInstance)
    *	Weekend start (RDSStartWeekEnd)
    *	Weekend stop (RDSStopWeekEnd)
    *	Weekday start (RDSStartWeekDay)
    *	Weekday stop (RDSStopWeekDay)
*	Rule – Create 4 EventBridge rules with cron schedule in UTC:
    *	Auto start (AutoStartRDSRule)
        *	Default schedule is cron (<code>0 13 ? * MON-FRI *</code>)
        *	Auto start instance (Mon–Fri 9:00 AM EST / 1:00 PM UTC)
    *	Auto stop (AutoStopRDSRule)
        *	Default schedule is cron (<code>0 1 ? * MON-FRI *</code>)
        *	Auto stop instance (Mon–Fri 9:00 PM EST / 1:00 AM UTC)
    *	Weekend start and stop (RDSStartStopWeekEndRule)
        *	Default schedule is cron (<code>*/5 * ? * MON-FRI *</code>)
        *	Instance is triggered every weekday, every 5 minutes
    *	Weekday start and stop (RDSStartStopWeekDayRule)
        *	Default schedule is cron (<code>*/5 * ? * SAT-SUN *</code>)
        *	Instance is triggered every weekend, every 5 minutes


### Resources
Following AWS resources are created from this template :
  *	Lambda functions:
      *	AutoStartRDSInstance
      *	AutoStopRDSInstance
      *	RDSStartWeekDay
      *	RDSStopWeekDay
      *	RDSStartWeekEnd
      *	RDSStopWeekEnd
  *	EventBridge rules:
      *	AutoStartRDSRule
      *	AutoStopRDSRule
      *	RDSStartStopWeekDayRule
      *	RDSStartStopWeekEndRule
  *	IAM resources:
      *	LambdaRDSStartStopRole (role)
      *	LambdaRDSStartStopPolicy (inline policy)
  *	CloudWatch log groups:
      *	/aws/lambda/AutoStartRDSInstance
      *	/aws/lambda/AutoStopRDSInstance
      *	/aws/lambda/RDSStartWeekDay
      *	/aws/lambda/RDSStopWeekDay
      *	/aws/lambda/RDSStartWeekEnd
      *	/aws/lambda/RDSStopWeekEnd


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

