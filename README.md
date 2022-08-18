# gitscratch-backend-flask

GitScratch 的社区后端。

## 安装依赖 / Installing Requirements
```shell
pip install -r requirements.txt
```
请自行下载 MaxMind `GeoLite2-City.mmdb` 文件，并将其放置在 `geolite2` 目录下。

## 启动 / Start
如果你是Linux：
```shell
sudo sh ./start_prod.sh
```
如果你是Windows：

以管理员身份运行`start_dev.cmd`

## 调试 / Debugging
特别的，如果你想以开发环境运行：

如果你是Linux：
```shell
sudo sh ./start_dev.sh
```
如果你是Windows：

以管理员身份运行`start_dev.cmd`

## TODO
- [x] 头像上传
- [ ] 作品保存
- [ ] 作品发布
- [ ] 作品加密
- [ ] ...
