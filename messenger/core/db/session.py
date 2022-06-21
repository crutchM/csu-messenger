from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url = "mysql+pymysql://root:22334455@192.168.0.106:3306/messenger"
engine = create_engine(db_url)
session = sessionmaker(engine)
