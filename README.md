# Email Receiver Manager For AWS SES


## Deploying the API
The first time deploying this SAM, run the deploy script with the `--guided` parameter,
this will help you define the parameters like bucket name and SentrySDK if you want to.

*leave the `SentryDsn=false` to disable the sentry integration*

```bash
sam deploy --guided
```

After the first deploy you should make incremental one's without the flag

```bash
sam deploy
```


## How to create a new Anime
First edit the file in this location `events/anime_create.json`.

Then run this command:

```bash
sam local invoke AnimeCreate -e events/anime_create.json
```

After this, the crawling will start in the new schedule event.

## Config files structure

Global Anime Config located in `{BUCKET_NAME}/animes.json`
```json
{
    "animes": [
        {
            "name": "anime x",
            "slug": "anime-x",
            "do_crawl": true
        }
    ]
}
```


Local Anime Config located in `{BUCKET_NAME}/animes/{slug}.json`
```json
{
    "slug": "anime-x",
    "url": "http://google.com/",
    "path": "animes/downloads/anime-x/",
    "episodes": {
        "12": {
          "url": "http://google.com",
          "download_url": "http://google.com/download"
        }
    }
}
```
