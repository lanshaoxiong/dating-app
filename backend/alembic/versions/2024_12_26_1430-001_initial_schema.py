"""Initial schema with PostGIS support

Revision ID: 001
Revises: 
Create Date: 2024-12-26 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create enum types
    op.execute("CREATE TYPE activity_level_enum AS ENUM ('low', 'medium', 'high')")
    op.execute("CREATE TYPE distance_unit_enum AS ENUM ('miles', 'kilometers')")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=False),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_profiles_user_id'), 'profiles', ['user_id'], unique=False)
    # Create spatial index on location
    op.execute('CREATE INDEX idx_profiles_location ON profiles USING GIST (location)')
    
    # Create photos table
    op.create_table(
        'photos',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_photos_profile_id'), 'photos', ['profile_id'], unique=False)
    
    # Create prompts table
    op.create_table(
        'prompts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompts_profile_id'), 'prompts', ['profile_id'], unique=False)
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('profile_id', sa.String(length=36), nullable=False),
        sa.Column('min_age', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_age', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('max_distance', sa.Float(), nullable=False, server_default='25.0'),
        sa.Column('activity_level', postgresql.ENUM('low', 'medium', 'high', name='activity_level_enum'), nullable=False, server_default='medium'),
        sa.Column('distance_unit', postgresql.ENUM('miles', 'kilometers', name='distance_unit_enum'), nullable=False, server_default='miles'),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('profile_id')
    )
    op.create_index(op.f('ix_user_preferences_profile_id'), 'user_preferences', ['profile_id'], unique=False)
    
    # Create likes table
    op.create_table(
        'likes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'target_id', name='uq_like_user_target')
    )
    op.create_index(op.f('ix_likes_user_id'), 'likes', ['user_id'], unique=False)
    op.create_index(op.f('ix_likes_target_id'), 'likes', ['target_id'], unique=False)
    op.create_index('ix_likes_target_user', 'likes', ['target_id', 'user_id'], unique=False)
    
    # Create passes table
    op.create_table(
        'passes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'target_id', name='uq_pass_user_target')
    )
    op.create_index(op.f('ix_passes_user_id'), 'passes', ['user_id'], unique=False)
    op.create_index(op.f('ix_passes_target_id'), 'passes', ['target_id'], unique=False)
    
    # Create matches table
    op.create_table(
        'matches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user1_id', sa.String(length=36), nullable=False),
        sa.Column('user2_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user1_id', 'user2_id', name='uq_match_users')
    )
    op.create_index(op.f('ix_matches_user1_id'), 'matches', ['user1_id'], unique=False)
    op.create_index(op.f('ix_matches_user2_id'), 'matches', ['user2_id'], unique=False)
    op.create_index(op.f('ix_matches_created_at'), 'matches', ['created_at'], unique=False)
    op.create_index('ix_matches_user1_created', 'matches', ['user1_id', 'created_at'], unique=False)
    op.create_index('ix_matches_user2_created', 'matches', ['user2_id', 'created_at'], unique=False)
    
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('match_id', sa.String(length=36), nullable=False),
        sa.Column('user1_id', sa.String(length=36), nullable=False),
        sa.Column('user2_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id')
    )
    op.create_index(op.f('ix_conversations_match_id'), 'conversations', ['match_id'], unique=False)
    op.create_index(op.f('ix_conversations_user1_id'), 'conversations', ['user1_id'], unique=False)
    op.create_index(op.f('ix_conversations_user2_id'), 'conversations', ['user2_id'], unique=False)
    op.create_index(op.f('ix_conversations_updated_at'), 'conversations', ['updated_at'], unique=False)
    op.create_index('ix_conversations_user1_updated', 'conversations', ['user1_id', 'updated_at'], unique=False)
    op.create_index('ix_conversations_user2_updated', 'conversations', ['user2_id', 'updated_at'], unique=False)
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), nullable=False),
        sa.Column('sender_id', sa.String(length=36), nullable=False),
        sa.Column('recipient_id', sa.String(length=36), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_messages_recipient_id'), 'messages', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_messages_created_at'), 'messages', ['created_at'], unique=False)
    op.create_index('ix_messages_conversation_created', 'messages', ['conversation_id', 'created_at'], unique=False)
    op.create_index('ix_messages_recipient_read', 'messages', ['recipient_id', 'read'], unique=False)
    
    # Create playgrounds table
    op.create_table(
        'playgrounds',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playgrounds_user_id'), 'playgrounds', ['user_id'], unique=False)
    # Create spatial index on location
    op.execute('CREATE INDEX idx_playgrounds_location ON playgrounds USING GIST (location)')


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_playgrounds_location', table_name='playgrounds')
    op.drop_index(op.f('ix_playgrounds_user_id'), table_name='playgrounds')
    op.drop_table('playgrounds')
    
    op.drop_index('ix_messages_recipient_read', table_name='messages')
    op.drop_index('ix_messages_conversation_created', table_name='messages')
    op.drop_index(op.f('ix_messages_created_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_recipient_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_sender_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')
    
    op.drop_index('ix_conversations_user2_updated', table_name='conversations')
    op.drop_index('ix_conversations_user1_updated', table_name='conversations')
    op.drop_index(op.f('ix_conversations_updated_at'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_user2_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_user1_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_match_id'), table_name='conversations')
    op.drop_table('conversations')
    
    op.drop_index('ix_matches_user2_created', table_name='matches')
    op.drop_index('ix_matches_user1_created', table_name='matches')
    op.drop_index(op.f('ix_matches_created_at'), table_name='matches')
    op.drop_index(op.f('ix_matches_user2_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_user1_id'), table_name='matches')
    op.drop_table('matches')
    
    op.drop_index(op.f('ix_passes_target_id'), table_name='passes')
    op.drop_index(op.f('ix_passes_user_id'), table_name='passes')
    op.drop_table('passes')
    
    op.drop_index('ix_likes_target_user', table_name='likes')
    op.drop_index(op.f('ix_likes_target_id'), table_name='likes')
    op.drop_index(op.f('ix_likes_user_id'), table_name='likes')
    op.drop_table('likes')
    
    op.drop_index(op.f('ix_user_preferences_profile_id'), table_name='user_preferences')
    op.drop_table('user_preferences')
    
    op.drop_index(op.f('ix_prompts_profile_id'), table_name='prompts')
    op.drop_table('prompts')
    
    op.drop_index(op.f('ix_photos_profile_id'), table_name='photos')
    op.drop_table('photos')
    
    op.drop_index('idx_profiles_location', table_name='profiles')
    op.drop_index(op.f('ix_profiles_user_id'), table_name='profiles')
    op.drop_table('profiles')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS distance_unit_enum')
    op.execute('DROP TYPE IF EXISTS activity_level_enum')
    
    # Note: We don't drop PostGIS extension as it might be used by other databases
    # op.execute('DROP EXTENSION IF EXISTS postgis')
