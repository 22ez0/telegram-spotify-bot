"""
Modelos de banco de dados usando SQLAlchemy 2.0+
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Integer, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base para todos os modelos"""
    pass


class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    group_users: Mapped[list["GroupUser"]] = relationship("GroupUser", back_populates="user")


class Group(Base):
    """Modelo de grupo"""
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    
    # Configurações de boas-vindas
    welcome_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    welcome_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Configurações de AutoMod
    automod_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_links: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_spam: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Log Channel
    log_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Fuso horário
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    group_users: Mapped[list["GroupUser"]] = relationship("GroupUser", back_populates="group")


class GroupUser(Base):
    """Modelo de relação entre usuário e grupo (para rank)"""
    __tablename__ = "group_users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.id"))
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user: Mapped["User"] = relationship("User", back_populates="group_users")
    group: Mapped["Group"] = relationship("Group", back_populates="group_users")


class ModerationLog(Base):
    """Modelo para logs de moderação"""
    __tablename__ = "moderation_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger)
    moderator_id: Mapped[int] = mapped_column(BigInteger)
    target_user_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(50))  # ban, mute, kick, etc
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SpotifyAccount(Base):
    """Modelo para armazenar credenciais OAuth do Spotify por usuário"""
    __tablename__ = "spotify_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[str] = mapped_column(Text)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime)
    
    spotify_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    spotify_display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SpotifyTrack(Base):
    """Modelo para armazenar histórico de músicas do Spotify"""
    __tablename__ = "spotify_tracks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.id"))
    
    track_id: Mapped[str] = mapped_column(String(255))
    track_name: Mapped[str] = mapped_column(String(500))
    artist_name: Mapped[str] = mapped_column(String(500))
    album_name: Mapped[str] = mapped_column(String(500))
    album_image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    spotify_url: Mapped[str] = mapped_column(String(1000))
    
    played_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserFriend(Base):
    """Modelo para lista de amigos entre usuários"""
    __tablename__ = "user_friends"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    friend_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'friend_id', name='uq_user_friend'),
        CheckConstraint('user_id != friend_id', name='ck_no_self_friend'),
    )


class UserSettings(Base):
    """Modelo para configurações do usuário (como .fmset)"""
    __tablename__ = "user_settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    
    fm_mode: Mapped[str] = mapped_column(String(50), default="embed")
    show_reactions: Mapped[bool] = mapped_column(Boolean, default=True)
    default_time_period: Mapped[str] = mapped_column(String(20), default="alltime")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ArtistCrown(Base):
    """Modelo para crowns (quem tem mais plays de cada artista no servidor)"""
    __tablename__ = "artist_crowns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    artist_name: Mapped[str] = mapped_column(String(500))
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('group_id', 'artist_name', name='uq_group_artist_crown'),
    )
