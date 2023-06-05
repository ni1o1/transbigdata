```cmd
# 移除build中原有文件
rm -r build
# 正式build
sphinx-build -b html ./source build
```

```cmd
sphinx-build -b gettext ./source build/gettext
sphinx-intl update -p ./build/gettext -l zh_CN
```