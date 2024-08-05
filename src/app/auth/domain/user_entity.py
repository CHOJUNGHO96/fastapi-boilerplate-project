from dataclasses import asdict, dataclass, field


@dataclass
class UserEntity:
    user_id: int = field(default=None)
    login_id: str = field(default=None)
    password: str = field(default=None)
    user_name: str = field(default=None)
    email: str = field(default=None)
    user_type: int = field(default=None)
    token_type: str = field(default=None)
    access_token: str = field(default=None)
    refresh_token: str = field(default=None)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return asdict(self)

    def delete_to_dict_none_data(self):
        return {k: v for k, v in self.to_dict().items() if v is not None}
