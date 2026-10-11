"""add invoice address and drop stored total

Revision ID: 9a4c00560ef5
Revises: 07d7375b07fc
Create Date: 2026-10-11 12:47:00.997597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9a4c00560ef5"
down_revision: Union[str, Sequence[str], None] = "07d7375b07fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_INVOICE_ADDRESS = "fk_invoice_address_id_address"


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("address", schema=None) as batch_op:
        batch_op.create_index(
            "uq_address_one_default_per_client",
            ["client_id"],
            unique=True,
            sqlite_where=sa.text("is_default = 1"),
            postgresql_where=sa.text("is_default = true"),
        )

    with op.batch_alter_table("invoice", schema=None) as batch_op:
        # Total is now computed from line items
        batch_op.drop_constraint("total_nonnegative_check", type_="check")
        batch_op.drop_column("total")

        # Rename "sent" status to "issued"
        batch_op.drop_constraint("status_valid_values_check", type_="check")
        batch_op.create_check_constraint(
            "status_valid_values_check",
            "status IN ('draft', 'issued', 'paid', 'void')",
        )

        # Table is empty, so NOT NULL needs no backfill
        batch_op.add_column(sa.Column("address_id", sa.Integer(), nullable=False))
        batch_op.create_index(
            batch_op.f("ix_invoice_address_id"), ["address_id"], unique=False
        )
        batch_op.create_foreign_key(
            FK_INVOICE_ADDRESS, "address", ["address_id"], ["id"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("invoice", schema=None) as batch_op:
        batch_op.drop_constraint(FK_INVOICE_ADDRESS, type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_invoice_address_id"))
        batch_op.drop_column("address_id")

        batch_op.drop_constraint("status_valid_values_check", type_="check")
        batch_op.create_check_constraint(
            "status_valid_values_check",
            "status IN ('draft', 'sent', 'paid', 'void')",
        )

        batch_op.add_column(
            sa.Column(
                "total",
                sa.Numeric(precision=12, scale=2),
                server_default=sa.text("0.00"),
                nullable=False,
            )
        )
        batch_op.create_check_constraint("total_nonnegative_check", "total >= 0")

    with op.batch_alter_table("address", schema=None) as batch_op:
        batch_op.drop_index(
            "uq_address_one_default_per_client",
            sqlite_where=sa.text("is_default = 1"),
            postgresql_where=sa.text("is_default = true"),
        )
