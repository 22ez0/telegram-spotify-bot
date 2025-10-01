"""
Gerenciamento de conexão com banco de dados
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from src.database.models import (
    Base, User, Group, GroupUser, ModerationLog, 
    SpotifyAccount, SpotifyTrack, UserFriend, UserSettings, ArtistCrown
)
from src.config import DATABASE_URL


class Database:
    """Classe para gerenciar o banco de dados"""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self) -> None:
        """Inicializa o banco de dados"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Retorna uma sessão do banco de dados"""
        async with self.session_maker() as session:
            yield session
    
    async def get_or_create_user(self, session: AsyncSession, user_id: int, username: str | None, 
                                  first_name: str, last_name: str | None) -> User:
        """Obtém ou cria um usuário"""
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        else:
            # Atualiza informações se mudaram
            if user.username != username or user.first_name != first_name or user.last_name != last_name:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                await session.commit()
        
        return user
    
    async def get_or_create_group(self, session: AsyncSession, group_id: int, title: str) -> Group:
        """Obtém ou cria um grupo"""
        result = await session.execute(select(Group).where(Group.id == group_id))
        group = result.scalar_one_or_none()
        
        if not group:
            group = Group(id=group_id, title=title)
            session.add(group)
            await session.commit()
            await session.refresh(group)
        else:
            if group.title != title:
                group.title = title
                await session.commit()
        
        return group
    
    async def get_or_create_group_user(self, session: AsyncSession, user_id: int, 
                                       group_id: int) -> GroupUser:
        """Obtém ou cria relação grupo-usuário"""
        result = await session.execute(
            select(GroupUser).where(
                GroupUser.user_id == user_id,
                GroupUser.group_id == group_id
            )
        )
        group_user = result.scalar_one_or_none()
        
        if not group_user:
            group_user = GroupUser(user_id=user_id, group_id=group_id)
            session.add(group_user)
            await session.commit()
            await session.refresh(group_user)
        
        return group_user
    
    async def increment_message_count(self, session: AsyncSession, user_id: int, group_id: int) -> None:
        """Incrementa contador de mensagens"""
        group_user = await self.get_or_create_group_user(session, user_id, group_id)
        group_user.message_count += 1
        await session.commit()
    
    async def get_user_rank(self, session: AsyncSession, user_id: int, group_id: int) -> tuple[int, int]:
        """Retorna posição e total de mensagens do usuário"""
        result = await session.execute(
            select(GroupUser).where(GroupUser.group_id == group_id)
            .order_by(GroupUser.message_count.desc())
        )
        group_users = result.scalars().all()
        
        user_messages = 0
        user_position = 0
        
        for idx, gu in enumerate(group_users, 1):
            if gu.user_id == user_id:
                user_position = idx
                user_messages = gu.message_count
                break
        
        return user_position, user_messages
    
    async def log_moderation(self, session: AsyncSession, group_id: int, moderator_id: int,
                            target_user_id: int, action: str, reason: str | None = None,
                            duration: str | None = None) -> None:
        """Registra ação de moderação"""
        log = ModerationLog(
            group_id=group_id,
            moderator_id=moderator_id,
            target_user_id=target_user_id,
            action=action,
            reason=reason,
            duration=duration
        )
        session.add(log)
        await session.commit()


# Instância global do banco de dados
db = Database(DATABASE_URL)
