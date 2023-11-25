"""
内置库：configparser
用于读取和写入配置文件。它提供了一种简单的方法来解析和操作INI格式的配置文件。

使用configparser库，你可以轻松地读取和修改配置文件中的各种设置和选项。
它支持创建、读取、更新和删除配置文件中的节(section)和键值(key-value)对。通常，配置文件用于存储应用程序的参数、选项和其他配置信息。
"""
import configparser
import os

config = configparser.ConfigParser()  # 实例化configparser对象
"""
读取ini文件
"""
# step1 ： 指定config.ini文件，必须存在
config.read('config.ini')
# step2：  section_name:set     key_name:BASE_URL
value = config.get('URL', 'DEV_BASE_URL')
print(value)

"""
修改ini文件
"""
config.set('URL', 'DEV_BASE_URL', 'www.devs.com')
# 将改动点写入ini文件中
with open('config.ini', 'w') as f:
    config.write(f)

# 查看是否修改成功
value = config.get('URL', 'DEV_BASE_URL')
print(value)

# 删除某一个option_name
config.remove_option('URL', 'SIT_BASE_URL')

# 将改动点写入文件
with open('config.ini', 'w') as f:
    config.write(f)

print(config.sections())


# 获取所有的section
# print(config.sections()) # 返回格式是列表

# 循环，遍历判断传入的section 是否存在于sections列表中
# for i in config.sections():
#     print(config.has_option(i, "dev_database")) # 判断section是否存在于 sctions中
print(config.has_option("URL", "dev_base_url"))














