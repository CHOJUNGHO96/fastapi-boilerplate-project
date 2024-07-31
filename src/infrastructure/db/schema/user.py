from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    inspect,
    text,
)
from sqlalchemy.orm import mapped_column

from .base import Base


class UserInfo(Base):
    __tablename__ = "user_info"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="user_info_pkey"),
        Index("user_info_login_id_idx", "user_id"),
    )

    user_id = mapped_column(Integer)
    user_type = mapped_column(SmallInteger, nullable=False, server_default=text("3"))
    login_id = mapped_column(Text)
    user_name = mapped_column(Text)
    password = mapped_column(Text)
    email = mapped_column(Text)
    refresh_token = mapped_column(Text)
    is_enable = mapped_column(SmallInteger, server_default=text("1"))
    reg_date = mapped_column(DateTime(True), server_default=text("now()"))

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
