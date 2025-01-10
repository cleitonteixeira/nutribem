import oracledb

# configuração user

username = "teknisa"
password = "teknisa"
dsn = "host:1521/teknisa"
def consultaOperador():
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT CDOPERADOR, NMOPERADOR FROM OPERADOR       
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def consultaFiliais():
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT CDFILIAL, NMFILIAL FROM FILIAL WHERE NMFILIAL NOT LIKE '%INATIVO%' AND NMFILIAL NOT LIKE '%INAT%'     
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def consultaRc():
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT
            s.CDFILSOLI, s.CDFILLANCA, s.NRSOLICMP, s.DTSOLCMP, o.CDOPERADOR, s.QTITEMSOLIC, m.DSJUSTSOLEXT,i.DTHRAPROVSOL,
            CASE
            WHEN COUNT(i.CDOPERAPROV) = s.QTITEMSOLIC THEN 'APROVADA'
            WHEN COUNT(i.CDOPERAPROV) < s.QTITEMSOLIC AND COUNT(i.CDOPERAPROV) > 0  THEN 'APROVADA PARCIALMENTE'
            ELSE 'REPROVADA'
            END AS "STATUS"
            FROM SOLICITA s
            INNER JOIN FILIAL f ON f.CDFILIAL = s.CDFILSOLI
            INNER JOIN OPERADOR o ON o.CDOPERADOR = s.CDOPERLANC
            INNER JOIN MOVSOLEXT m ON m.CDFILSOLEXT = s.CDFILSOLI AND m.CDFILLANCEXT = s.CDFILLANCA AND m.NRSOLIMOVEXT = s.NRSOLICMP
            INNER JOIN ITEMSOLI i ON i.CDFILSOLI = s.CDFILSOLI AND i.CDFILLAN = s.CDFILLANCA AND i.NRSOLICMP = s.NRSOLICMP
            WHERE s.DTSOLCMP >= '01/01/2025' AND s.IDSOLEXTRA = 'S'
            GROUP BY
                s.CDFILSOLI,
                f.NMFILIAL,
                s.CDFILLANCA,
                s.NRSOLICMP,
                s.DTSOLCMP,
                o.CDOPERADOR,
                s.QTITEMSOLIC,
                m.DSJUSTSOLEXT,
                i.DTHRAPROVSOL
            HAVING 
                COUNT(i.CDOPERAPROV) = s.QTITEMSOLIC
            ORDER BY s.DTSOLCMP, s.CDFILSOLI, s.NRSOLICMP
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def consultaItensRc(rc, solicita, destino):
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT NRSOLICMP,CDPRODUTO, QTSOLIPROD, DTUTILIZA FROM ITEMSOLI WHERE
            CDFILSOLI = '{solicita.code}' AND CDFILLAN = '{destino.code}' AND NRSOLICMP = '{rc}'            
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def CriaClasse():
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT CDPRODUTO, NMPRODUTO FROM PRODUTO
            WHERE NMPRODUTO NOT LIKE '.' HAVING LENGTH(CDPRODUTO) = 3 GROUP BY CDPRODUTO,NMPRODUTO ORDER BY CDPRODUTO
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def CriaProdutos():
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT SUBSTR(CDPRODUTO, 1, 3) AS "CLASSE",CDPRODUTO, NMPRODUTO, SGUNIDADE FROM PRODUTO
            WHERE NMPRODUTO NOT LIKE '.' AND CDPRODUTO IN
            (SELECT DISTINCT(CDPRODUTO) FROM ITEMSOLI WHERE DTUTILIZA >= '01/01/2024' AND CDOPERAPROV IS NOT NULL)
            ORDER BY NMPRODUTO
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



def consultaProdutos(code):
    print("############")
    try:
        connection = oracledb.connect(user=username, password=password,
                                    host="192.168.0.91", port=1521, service_name="orclpdb")
        print("############")
        print(connection.version)

        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT SUBSTR(CDPRODUTO, 1, 3) AS "CLASSE",CDPRODUTO, NMPRODUTO, SGUNIDADE FROM PRODUTO
            WHERE CDPRODUTO = '{code}'
            
        """)
        rows = cursor.fetchall()
        return rows
    except oracledb.DatabaseError as e:
        print (e)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

