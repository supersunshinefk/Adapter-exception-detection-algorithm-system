# 1. Aplec_v0.2.2更新说明

## 1.1. Aplec_web [V0.2.0] 2018.12.19

### 1.1.1. Functionality Added or Changed

- 前端报文信息栏只展示I/N/R报文数据,简称Q3
- 替换页面所有中文字为英文字
- aplec界面左边栏增加根据时间查询以及实现动态查询适配器功能

### 1.1.2. Bugs Fixed

- 修改页面英文字母大小写问题  

## 1.2. Aplec_admin [V0.2.0] 2018.12.19

### 1.2.1. Functionality Added or Changed

- 增加了根据时间期限查询数据功能

### 1.2.2. Bugs Fixed

- 修复下发至前端最近6小时数据和24小时数据展示不准确bug
- 修改获取aplec计算数据接口时，无法根据概率值查询相应数据bug

## 1.3. Aplec_compute [V0.2.0] 2018.12.19

### 1.3.1. Functionality Added or Changed

- 数据格式的code中,error msg中文字替换成英文字
- 增加aplec计算数据在mysql中保留时间功能

### 1.3.2. Bugs Fixed

- 再次修改计算周期中,4小时未能计算p2周期指数的bug
- 修改计算周期的指数值的判断范围


