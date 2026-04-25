"""Seed dictionaries data

Revision ID: a96fde35b1c7
Revises: 68538b0fb257
Create Date: 2026-04-25 16:49:24.615787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a96fde35b1c7'
down_revision: Union[str, Sequence[str], None] = '68538b0fb257'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
     # 1. Описываем структуры таблиц для Alembic
    firms = sa.table('firms', sa.column('name', sa.String))
    bodies = sa.table('bodies', sa.column('name', sa.String))
    accident_types = sa.table('accident_types', sa.column('name', sa.String))
    accident_reasons = sa.table('accident_reasons', sa.column('name', sa.String))

    # 2. Заполняем Фирмы авто
    op.bulk_insert(firms, [
        {'name': 'Lada (ВАЗ)'}, {'name': 'Toyota'}, {'name': 'Kia'},
        {'name': 'Hyundai'}, {'name': 'Volkswagen'}, {'name': 'BMW'},
        {'name': 'Nissan'}, {'name': 'Subaru'}, {'name': 'Mercedes-Benz'},
        {'name': 'Ford'}, {'name': 'Honda'}, {'name': 'Renault'},
        {'name': 'Skoda'}, {'name': 'Chevrolet'}, {'name': 'Audi'}
    ])

    # 3. Заполняем Типы кузова
    op.bulk_insert(bodies, [
        {'name': 'Седан'}, {'name': 'Хэтчбек'}, {'name': 'Универсал'},
        {'name': 'Кроссовер'}, {'name': 'Внедорожник'}, {'name': 'Пикап'},
        {'name': 'Минивэн'}, {'name': 'Купе'}, {'name': 'Фургон'}
    ])

    # 4. Заполняем Виды ДТП (Строго из твоего PDF + дополнения)
    op.bulk_insert(accident_types, [
        {'name': 'Наезд на пешехода'},
        {'name': 'Наезд на препятствие'},
        {'name': 'Столкновение'},
        {'name': 'Опрокидывание'},
        {'name': 'Наезд на велосипедиста'},
        {'name': 'Падение пассажира'},
        {'name': 'Наезд на стоящее транспортное средство'}
    ])

    # 5. Заполняем Причины ДТП (Строго из твоего PDF + дополнения)
    op.bulk_insert(accident_reasons, [
        {'name': 'Выезд на полосу встречного движения'},
        {'name': 'Состояние водителя (опьянение/усталость)'},
        {'name': 'Неисправность автомобиля'},
        {'name': 'Нарушение ПДД (проезд на красный, непредоставление преимущества)'},
        {'name': 'Превышение установленной скорости'},
        {'name': 'Несоблюдение дистанции'},
        {'name': 'Неудовлетворительные дорожные условия (гололед, ямы)'}
    ])



def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM firms;")
    op.execute("DELETE FROM bodies;")
    op.execute("DELETE FROM accident_types;")
    op.execute("DELETE FROM accident_reasons;")
