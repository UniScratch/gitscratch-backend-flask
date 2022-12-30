# gitscratch-backend-flask

GitScratch 的社区后端。

## 安装依赖 / Installing Requirements
```shell
pip install -r requirements.txt
```
请自行下载 [MaxMind `GeoLite2-City.mmdb`](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en) 文件，并将其放置在 `geolite2` 目录下。
需要在工作区根目录下创建 `commits` 和 `assets` 文件夹

## 启动 / Start
```shell
sh ./start_prod.sh
```

## 调试 / Debugging
特别地，如果你想以开发环境运行：

```shell
sh ./start_dev.sh
```

## TODO
- [x] 头像上传
- [ ] 作品保存
- [ ] 作品发布
- [ ] 作品加密
- [ ] .......
