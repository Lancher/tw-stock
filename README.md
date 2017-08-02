## Usage

Parse the stock reports to mysql:

```
./parse_stock_data_to_mysql.py -s 2017_07_12 -e 2017_07_14 -d ~/stock-data/
```

Run Docker-Compose:

```
docker-compose up
```

Load *.sql to MySQL db:

```
mycli -u root -h db
> source *.sql
```

Build & Run:

```
docker build -t desktop .
docker run -it -d --rm -e TZ=Asia/Taipei -e VNC_PASSWORD=444555666d -v /home/Steve/stock-data:/data -v /home/Steve/docker-ubuntu-vnc-desktop/image/testing_scripts:/testing_scripts -p 6080:80 desktop
```

