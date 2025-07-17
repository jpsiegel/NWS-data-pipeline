"""add fields to weather obs

Revision ID: 92804713d0c9
Revises: 0a8b5a9d4af9
Create Date: 2025-07-17 02:20:16.055016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92804713d0c9'
down_revision: Union[str, None] = '0a8b5a9d4af9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('weather_observations', sa.Column('wind_direction', sa.Float(), nullable=True))
    op.add_column('weather_observations', sa.Column('pressure', sa.Float(), nullable=True))
    op.add_column('weather_observations', sa.Column('dewpoint', sa.Float(), nullable=True))
    op.add_column('weather_observations', sa.Column('visibility', sa.Float(), nullable=True))

    # Add constraints
    op.create_check_constraint(
        "temperature_above_absolute_zero",
        "weather_observations",
        condition="temperature IS NULL OR temperature >= -273.15"
    )
    op.create_check_constraint(
        "valid_wind_direction",
        "weather_observations",
        condition="wind_direction IS NULL OR wind_direction BETWEEN 0 AND 360"
    )
    op.create_check_constraint(
        "valid_humidity",
        "weather_observations",
        condition="humidity IS NULL OR humidity BETWEEN 0 AND 100"
    )
    op.create_check_constraint(
        "positive_visibility",
        "weather_observations",
        condition="visibility IS NULL OR visibility >= 0"
    )



def downgrade() -> None:
    # Drop constraints
    op.drop_constraint("temperature_above_absolute_zero", "weather_observations", type_="check")
    op.drop_constraint("valid_wind_direction", "weather_observations", type_="check")
    op.drop_constraint("valid_humidity", "weather_observations", type_="check")
    op.drop_constraint("positive_visibility", "weather_observations", type_="check")

    # Drop columns
    op.drop_column('weather_observations', 'visibility')
    op.drop_column('weather_observations', 'dewpoint')
    op.drop_column('weather_observations', 'pressure')
    op.drop_column('weather_observations', 'wind_direction')
