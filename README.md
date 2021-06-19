# Arris WIFI Connection Manager

> This script, was tested only with hardware version 10 and firmware version 9.1.103DV8W

## Requirements

- Google Chrome o Chromium
- Chrome WebDriver
- Python 3.7 or greather
- Linux
- envsubst command (Optional)

> This script was developed using Chromium 88 in Raspian OS.

## Use

To run this script you must install virtualenv in the cloned directory as follow:

```shell
virtualenv .venv
```

Now you must create a `env.ini` file with the following values:

```shell
export ARRIS_CONSOLE_HOST="http://10.10.0.1"
export ARRIS_CONSOLE_USER="user"
export ARRIS_CONSOLE_PASSWORD="secret"
export CLIENT_MAC_ADDRESS="XX:XX:XX:XX:XX:XX"
# Set this with value 1 if you want run this script without disable/enable your WIFI
export DRY_RUN="0"
export EXECUTABLE_PATH="/usr/bin"
```

Now you can execute the `disable.sh` and `enable.sh` scripts.

> To run this with headless option off pass 0 as argument to both scripts

## Crontab

If you want run this script using cronjob, you can use the `crontab.template.txt` file with `envsubst`.