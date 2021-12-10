#!/bin/bash
# aws logs describe-log-streams --output text --log-group-name /aws/lambda/fundacion | awk '{print $4 " " $3 " " $2}' | sort
aws logs describe-log-streams --log-group-name /aws/lambda/fundacion | grep logStreamName | \
    tail -10 | awk -F\" '{print $4 }' | while read ln ; do
    echo $ln
    # aws logs get-log-events --log-group-name /aws/lambda/fundacion --log-stream-name $ln 
done
#aws logs get-log-events --output text --log-group-name /aws/lambda/fundacion --log-stream-name '2021/12/10/[$LATEST]8b8754041414437ca5b22b9106549a2f'