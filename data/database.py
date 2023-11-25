import copy
import mysql.connector
import configparser
import os


class ConfigReader:
    def __init__(self, file_name):
        self.config = configparser.ConfigParser()
        config_path = os.path.split(os.path.realpath(__file__))[0] + os.sep + file_name
        self.config.read(config_path, "utf-8")

    def get_config(self, config_item):
        sections = self.config.sections()
        for section in sections:
            if self.config.has_option(section, config_item):
                return self.config.get(section, config_item)


class MysqlConnectionClass():

    def __init__(self, database_name):
        cf = ConfigReader("database_dev.cfg")
        self.host = cf.get_config(database_name + "_host")
        self.port = cf.get_config(database_name + "_port")
        self.user = cf.get_config(database_name + "_user")
        self.password = cf.get_config(database_name + "_password")
        self.database_name = database_name

    def __call__(self):
        try:
            self.cnx = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database_name.lower())
            self.cursor = self.cnx.cursor()
        except Exception as e:
            print("创建数据库链接失败")
            print(e)

    def close_connection(self):
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.cnx is not None:
                self.cnx.close()
        except Exception as e:
            print("关闭数据库链接失败")
            print(e)

    def query_data_by_criteria(self, table_name, search_condition={},
                               search_column_name=''):  # e.g:{'column_name':['operator','value']}
        """
        :param self: 表示该方法是一个类的成员方法
        :param table_name: 表示要查询的表名
        :param search_condition:表示查询条件，以字典的形式提供。每个键是列名，值是一个包含操作符和值的列表，用于构建查询条件
        :param search_column_name:表示要查询的列名，如果为空，则查询所有列。
        :return:返回处理后的 table_data 列表，其中包含了查询结果的所有行数据。
        """
        try:
            if search_column_name == '':
                query = 'select * from ' + table_name
            # 首先，根据参数组合构建查询语句   如果 search_column_name 为空，则构建一个"select * from table_name"的查询语句，
            else:
                # 否则构建"select search_column_name from table_name"的查询语句。
                query = 'select ' + search_column_name + ' from ' + table_name
            # 接着，根据 search_condition 构建 WHERE 子句
            if len(search_condition) > 0:
                # 如果 search_condition 的长度大于0，则开始构建 WHERE 子句，并添加一个占位条件 (1=1) ，保证后续的条件可以通过 "and" 连接。
                query += ' where (1=1) '
                # 使用 for 循环遍历 search_condition 中的每个键值对
                for key, val in search_condition.items():
                    # 检查键是否为 "limit"、"order by" 或 "group by"，如果是，则跳过当前循环。
                    if str(key).lower().strip() == "limit" or str(key).lower().strip() == "order by" \
                            or str(key).lower().strip() == "group by":
                        continue
                    query += 'and '  # 在查询语句中添加 "and" 来连接条件。
                    query += key  # 将列名添加到查询语句中。
                    query += val[0]  # 添加操作符。
                    if type(val[1]) == str and not val[1].startswith('date'):
                        # 检查值的类型，如果是字符串且不以 "date" 开头
                        # 则将值用单引号括起来
                        query += ('\'' + val[1] + '\'')
                    else:
                        # 否则直接转换为字符串并添加到查询语句中。
                        query += str(val[1])
                if "order by" in search_condition.keys():
                    # search_condition  包含 "order by"，则在查询语句末尾添加 "order by" 子句。
                    query += " order by " + str(search_condition["order by"][0]) + str(search_condition["order by"][1])
                if "group by" in search_condition.keys():
                    # 如果 search_condition 包含 "group by"，则在查询语句末尾添加 "group by" 子句
                    query += " group by " + str(search_condition["group by"][0]) + str(search_condition["group by"][1])
                if "limit " in search_condition.keys():
                    # 如果 search_condition 包含 "limit"，则在查询语句末尾添加 "limit" 子句。
                    query += " limit " + str(search_condition["limit "][1])
            query += ';'
            print(query)  # 将构建好的查询语句打印出来
            self.cursor.execute(query)  # 使用 self.cursor.execute(query) 执行查询操作
            result = self.cursor.fetchall()  # 使用 self.cursor.fetchall() 获取查询结果
            colume_names = self.cursor.column_names  # 使用 self.cursor.column_names 获取查询结果的列名。
            table_data = []  # 创建一个空列表 table_data，用于存储处理后的表数据
            rows = {}  # 遍历查询结果中的每一行数据。
            for row in result:  # 对于每一行数据。
                for index, column in enumerate(colume_names):  # 使用 enumerate(colume_names) 枚举列名和对应的索引
                    rows[column] = row[index]  # 将列名作为键，将对应索引处的值赋给字典 rows。
                table_data.append(copy.deepcopy(rows))  # 使用 copy.deepcopy() 来创建副本，避免多次迭代时覆盖原始数据。
                # 将每个字典副本追加到 table_data 列表中
            # print(table_data)
            return table_data  # 返回处理后的 table_data 列表，其中包含了查询结果的所有行数据。
        except Exception as e:  # 如果在执行过程中出现异常
            print(e)  # ，将异常消息打印出来
            self.close_connection()  # 调用 self.close_connection() 关闭数据库连接

    def update_data_by_criteria(self, table_name, update_column_name,
                                update_column_value, search_condition={}):
        if type(update_column_value) == str:
            query = 'update ' + table_name + ' set ' + update_column_name + ' = \'' + update_column_value + '\''
        else:
            query = 'update ' + table_name + ' set ' + update_column_name + ' = ' + update_column_value

        if len(search_condition) > 0:
            query += ' where '
            for key, val in search_condition.items():
                query += key
                query += ' = '
                if type(val) == str:
                    query += ('\'' + val + '\'')
                else:
                    query += str(val)
                query += ' and '
            query = query[0:query.rfind(' and ')]
        query += ';'
        print(query)
        try:
            self.cursor.execute((query))
            self.cnx.commit()
        except Exception as e:
            print('更新数据库数据失败')
            print(e)
            raise ('更新数据库数据失败')

    def execute_sql_statement(self, sql):
        print(sql)
        try:
            self.cursor.execute((sql))
            if sql.startswith("select"):
                result = self.cursor.fetchall()
                self.cnx.commit()
                return result
            else:
                self.cursor.execute(sql)
                self.cnx.commit()
                return 0
        except Exception as e:
            print('执行sql失败')
            raise e

    def execute_delete_statement(self, sql):
        print(sql)
        try:
            self.cursor.execute((sql))
            self.cnx.commit()
        except Exception as e:
            print('执行sql失败')
            raise e

    def query_table_data_counts_by_criteria(self, table_name, page_number,
                                            search_condition={}):  # e.g:{'column_name':['operator','value']}
        try:
            query = 'select id from ' + table_name
            if len(search_condition) > 0:
                query += ' where '
                for key, val in search_condition.items():
                    query += key
                    query += (' ' + val[0] + ' ')
                    if type(val[1]) == str and (not val[1].startswith('date')) and (not val[1].startswith('null')):
                        query += ('\'' + val[1] + '\'')
                    else:
                        query += str(val[1])
                    query += ' and '
                query = query[0:query.rfind(' and ')]
            query += ' limit 0,' + str(page_number) + ';'
            print(query)
            self.cursor.execute((query))
            result = self.cursor.fetchall()
            return len(result)
        except Exception as e:
            print(e)
            self.close_connection()

    def insert_data(self, table_name, insert_data={}):
        try:
            if len(insert_data) > 0:
                columns = []
                values = []
                for key, val in insert_data.items():
                    columns.append(key)
                    if isinstance(val, str) and not val.startswith('date'):
                        values.append(f"'{val}'")
                    else:
                        values.append(str(val))
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
                print(query)
                self.cursor.execute(query)
                self.cnx.commit()
                print("Data inserted successfully.")
        except Exception as e:
            print(e)
            self.close_connection()


if __name__ == '__main__':
    from faker import Faker
    import random

    faker1 = Faker(locale='zh_cn')
    m1 = MysqlConnectionClass("lctest")

    for i in range(0, 100):
        m1()
        insert_data = {
            'name': faker1.name(),
            'phone_number': faker1.phone_number(),
            'age': random.randint(19, 28),
            'address': faker1.address()
        }
        m1()
        m1.insert_data("student", insert_data)
    #
    # 构建查询条件
    search_condition = {
         'age': ['=', '24'],
         'order by': ['age',' desc'],
         'limit':[10]
     }
    m1()
    print(m1.query_data_by_criteria("student", search_condition, "name"))

