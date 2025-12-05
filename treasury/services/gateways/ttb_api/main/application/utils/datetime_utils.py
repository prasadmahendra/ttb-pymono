from datetime import datetime, timezone, date


class DateTimeUtils:

    @classmethod
    def get_utc_now(cls) -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def get_utc_epoch_millis_now(cls) -> int:
        return int(cls.get_utc_now().timestamp() * 1000)

    @classmethod
    def parse_datetime_str(cls, datetime_str: str) -> datetime:
        return datetime.fromisoformat(datetime_str)

    @classmethod
    def strptime(cls, datetime_str: str, fmt: str) -> datetime:
        return datetime.strptime(datetime_str, fmt)

    @classmethod
    def epoch_to_datetime(cls, epoch_millis: int) -> datetime:
        """
        Convert epoch milliseconds to a UTC datetime object.
        0 epoch millis is 1970-01-01T00:00:00Z
        1672531199000 epoch millis is 2022-12-31T23:59:59Z
        1672531200000 epoch millis is 2023-01-01T00:00:00Z
        1704067199000 epoch millis is 2023-12-31T23:59:59Z
        :param epoch_millis:
        :return: datetime in UTC
        """
        return datetime.fromtimestamp(epoch_millis / 1000.0, tz=timezone.utc)

    @classmethod
    def get_utc_today(cls) -> date:
        utc_now = cls.get_utc_now()
        return utc_now.date()

    @classmethod
    def format_date(cls, d: date, format_str: str) -> str:
        return d.strftime(format_str)
