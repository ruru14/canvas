from util import info
import pymysql

connect = info.getDbInfo()

class DbConnector:

    def __init__(self, connectInfo):
        self.conn = pymysql.connect(host=connectInfo['host'], user=connectInfo['user'],
                                    password=connectInfo['password'],
                                    db=connectInfo['database'], charset='utf8')
        self.dictCurs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.curs = self.conn.cursor()

    def isAlreadyInserted(self, table):
        sql = """SELECT count(Date) FROM %s WHERE Date=curdate()"""
        sql = sql.replace('%s', table)

        self.curs.execute(sql)
        rows = self.curs.fetchall()
        if (int(rows[0][0]) == 0):
            return False
        else:
            return True

    def insertUser(self, users):
        sql = """INSERT INTO Member values(curdate(), %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        self.curs.executemany(sql, users)
        print(str(len(users)) + "Users Inserted : Member")
        self.conn.commit()

    def insertGuildInfo(self, info):
        sql = """INSERT INTO GuildInfo values(curdate(), %s, %s, %s)"""

        self.curs.execute(sql, info)
        self.conn.commit()

    def insertSubUser(self, users):
        sql = """INSERT INTO SubMember values(curdate(), %s, %s)"""

        self.curs.executemany(sql, users)
        print(str(len(users)) + "Users Inserted : SubMember")
        self.conn.commit()

    def selectOldMember(self):
        sql = """SELECT """

    def selectLeaveMember(self, table, isSub):
        sql = """select Date, Name from (select max(Date) as date, Name from %s group by Name) as leaved where date<>CURRENT_DATE-1 and date<>CURRENT_DATE"""
        sql = sql.replace('%s', table)

        self.curs.execute(sql)
        self.dictCurs.execute(sql)
        rowsDict = self.dictCurs.fetchall()
        rows = self.curs.fetchall()

        self.deleteLeaveMember(rowsDict)
        if not isSub:
            self.moveLeaveMember(rows)

        print(table + " Deleted List")
        for n in rows:
            print(n)

    def deleteLeaveMember(self, users):
        sql = """DELETE FROM Member where Name=%s"""

        for n in users:
            self.dictCurs.execute(sql, n['Name'])
        self.conn.commit()

    def moveLeaveMember(self, users):
        sql = """insert into LeaveMember values (%s, %s)"""

        self.curs.executemany(sql, users)
        self.conn.commit()

    def __del__(self):
        self.conn.close()


