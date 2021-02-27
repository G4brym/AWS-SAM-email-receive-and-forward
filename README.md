# AWS SAM Receive And Forward Emails with SES and Lambda

## Deploying the API
The first time deploying this SAM, run the deploy script with the `--guided` parameter,
this will help you define the parameters like bucket name and SentrySDK if you want to.

*leave the `SentryDsn=disabled` to disable the sentry integration*

```bash
sam deploy --guided
```

After the first deploy you should make incremental one's without the flag

```bash
sam deploy
```
