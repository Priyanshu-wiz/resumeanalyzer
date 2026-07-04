from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL ="mysql://3saVw6Sp2UMaZKb.root:<PASSWORD>@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/sys" 

engine=create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl":{
          "ssl":True
        }
    }
)

Sessionlocal = sessionmaker(bind=engine)
Base= declarative_base()
