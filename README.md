新三板公告抓取
==============

描述
-----
主要解决从巨潮接入新三板公告余老三板公告数据慢的问题， 实行抓取；抓取的文件形成数据存入122.144.134.95 mongo， 公告文件上传S3
    
抓取来源
----
http://www.neeq.com.cn/disclosure/announcement.html（挂牌公司、两网及退市公司）
    
程序运行
----
1:执行脚本：announcement_otc/jobs/aps.py

2:根据计划准备放在122.144.134.3:/opt/scrapyer/announcement_otc下运行

3:使用screen命令， 是程序在后台工作， 运行：python run_otc.py
    
备注
------
目前程序已部署和运行， 具体问题以代码为准
