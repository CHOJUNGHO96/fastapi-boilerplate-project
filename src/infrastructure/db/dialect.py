# coding=utf-8
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.sql.sqltypes import JSON, DateTime, NullType, String


class StringLiteral(String):
    """Teach SA how to literalize various things."""

    def literal_processor(self, dialect):
        super_processor = super(StringLiteral, self).literal_processor(dialect)

        def process(value):
            if isinstance(value, int):
                return str(value)
            if not isinstance(value, str):
                value = str(value)
            # noinspection PyCallingNonCallable
            result = super_processor(value)
            if isinstance(result, bytes):
                result = result.decode(dialect.encoding)
            return result

        return process


class LiteralDialect(PGDialect):
    colspecs = {
        String: StringLiteral,
        DateTime: StringLiteral,
        NullType: StringLiteral,
        JSON: StringLiteral,
    }
