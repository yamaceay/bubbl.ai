### How to Setup

Make sure Python 3.11 (or newer) is installed on your local machine. MacOS is preferred. Then, run `pip3 install -r requirements.txt --upgrade` to install all packages. After that, set the following environment variables:

```bash
OPENAI_API_KEY=your-openai-api-key
WCS_API_KEY=your-weaviate-cluster-api-key
WCS_URL=your-weaviate-cluster-url
```

I prefer to store all environment variables in `.env` and run `source pre.sh` to set them. After setting, you're ready to go. Just run `python3 cli.py` and enjoy!