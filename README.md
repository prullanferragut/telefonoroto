

## Minimum configuration

In the ".env" file (or secrets pushed as enviroment variables) put:

```python
ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", cast=str)
ACCOUNT_TOKEN = config("TWILIO_AUTH_TOKEN", cast=str)
APP_PHONE_ORIGIN = config("APP_PHONE_ORIGIN", cast=str)
```