# gitscratch-backend-flask

GitScratch 的社区后端。

[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)
[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg)](https://github.com/996icu/996.ICU/blob/master/LICENSE)



## 安装依赖 / Installing Requirement
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
