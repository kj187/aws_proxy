```

    WORK IN PROGRESS

```

# AWS Proxy

The AWS proxy enables you from localhost to reach AWS services which are based in a private subnet (VPC).

## Problem

In a modern infrastructure architecture, services like RDS, ElastiCache, OpenSearch, MQ etc. should be live in a protected private network which is not accessable from the public. Some of these services are providing web interfaces which are quite helpful to debug problems. But how is it possible to reach them in the browser? And how is it possible to have a look in a database or any other AWS service which is protected and not accessable via the AWS Console? 

One way to solve this kind of problem is to open a **proxy** to these services. 
And on this way the **AWS Proxy** as a small CLI utility comes into play to support you with that.

```
                                              AWS ACCOUNT
--------------------------------------------------------------------------
                            |    PUBLIC SUBNET              PRIVATE SUBNET
-------------+              |    +----------+               +-------------
    LOCAL    |              |    |  BASTION |               |     AWS
    CLIENT   | <== SSH 22 =====> |  SERVER  | <== local ==> |   SERVICE
-------------+              |    +----------+               +-------------
                            |
--------------------------------------------------------------------------
```


## Supported AWS services

Currently we support the following AWS services

- RDS (default local port `6950`)
- OpenSearch (Elasticsearch, with Kibana) (default local port `6951`)
- RabbitMQ (default local port `6952`)
- ElastiCache (default local port `6953`)

## Requirements

### Bastion Host and SSH access to this

To open a proxy to your private network services, we need something like a bridge between your public and your private network. 
This kind of bridge is called a **jump host** or a **bastion server**. 
This is a server which lives in your public network and has access to your private network. 
For security reasons you should only allow SSH as ingress. 
Also, you need to have access from you local machine to the bastion server. 
The AWS Proxy assumes that you have access to the bastion with a valid user and a valid SSH key. 

You need also configure the security group of your protected AWS services to allow access from the bastion host.

## Examples

``` 
aws_proxy --aws-profile AWSPROFILENAME --bastion-host 1.2.3.4 --bastion-username firstname.lastname opensearch
aws_proxy --aws-profile AWSPROFILENAME --bastion-host 1.2.3.4 --bastion-username firstname.lastname opensearch --local-bind-port 8888
aws_proxy --aws-profile AWSPROFILENAME --bastion-host 1.2.3.4 --bastion-username firstname.lastname opensearch --local-bind-port 8888 --cluster-name CLUSTERNAME
```

You can also ignore the `--bastion-host` flag, in this case the `--bastion-label-selector` flag with its default value of `tag:Name=bastion` comes into play. 
It will search an EC2 instance with a tag "Name" and with the Value "bastion". So, just tag your bastion host with this Key=Value. 

## Based on 

- Python 3+ 
- SSHTunnel Module
- Click CLI Module
- AWS Boto SDK