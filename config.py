import os
# PARA RENDER (PostgreSQL)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Render usa PostgreSQL
    result = urlparse(DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = f"postgresql://{result.username}:{result.password}@{result.hostname}:{result.port}{result.path}"
    print("Usando PostgreSQL de Render")
else:

    # Configuración para AlwaysData
    DB_HOST = os.environ.get('MYSQL_HOST', 'mysql-gabrielvazquez.alwaysdata.net')
    DB_USER = os.environ.get('MYSQL_USER', '445376')
    DB_PASS = os.environ.get('MYSQL_PASSWORD', 'U7#95drsuCQRvBM')
    DB_NAME = os.environ.get('MYSQL_DATABASE', 'gabrielvazquez_bbdd')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_super_secreta_123')
SQLALCHEMY_TRACK_MODIFICATIONS = False