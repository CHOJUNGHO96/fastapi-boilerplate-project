# coding=utf-8
from dependency_injector import containers, providers

from app.auth.repository.user_repository import Repository as UserRepository


class Container(containers.DeclarativeContainer):
    db = providers.Singleton()

    # Repository
    user_repository = providers.Singleton(UserRepository, session_factory=db.provided.session)
