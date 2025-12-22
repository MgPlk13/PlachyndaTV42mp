from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    inspect,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from config_db import ANALYTICS_DATABASE_URI

from decorators import login_required, role_required

Base = declarative_base()

AnalyticsEngine = create_engine(
    ANALYTICS_DATABASE_URI,
    echo=True,
    client_encoding="utf8",
)

AnalyticsSession = sessionmaker(bind=AnalyticsEngine)


class AttackType(Base):
    __tablename__ = "attack_types"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text)

    def __repr__(self):
        return (
            f"<AttackType(code='{self.code}', "
            f"description='{self.description}')>"
        )


class AttackLog(Base):
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    query = Column(Text, nullable=False)
    score = Column(Float)
    source_ip = Column(String, default="127.0.0.1")
    status = Column(String, default="blocked")
    attack_type_id = Column(Integer, ForeignKey("attack_types.id"))
    attack_type = relationship("AttackType")

    def __repr__(self):
        return (
            f"<AttackLog(time='{self.timestamp}', "
            f"reason='{self.reason}', "
            f"status='{self.status}')>"
        )


@login_required
def create_analytics_tables():
    inspector = inspect(AnalyticsEngine)
    existing_tables = inspector.get_table_names()

    required_tables = {"attack_logs", "attack_types"}
    missing_tables = required_tables - set(existing_tables)

    if missing_tables:
        Base.metadata.create_all(AnalyticsEngine)
        print(f"Таблиці analytics створено: {', '.join(missing_tables)}")
    else:
        print("Таблиці analytics вже існують — створення пропущено.")


if __name__ == "__main__":
    create_analytics_tables()
