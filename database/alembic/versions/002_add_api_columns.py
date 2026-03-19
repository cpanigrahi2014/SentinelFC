"""Add columns needed by API endpoints

Revision ID: 002_api_columns
Revises: 001_initial
Create Date: 2026-03-18 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '002_api_columns'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alerts: add priority, customer_name, rule_id, escalation_reason, close_reason
    op.add_column('alerts', sa.Column('priority', sa.String(16), server_default='medium'))
    op.add_column('alerts', sa.Column('customer_name', sa.String(256)))
    op.add_column('alerts', sa.Column('rule_id', sa.String(64)))
    op.add_column('alerts', sa.Column('escalation_reason', sa.Text))
    op.add_column('alerts', sa.Column('close_reason', sa.String(64)))

    # Cases: add case_type, customer_id, customer_name, assigned_to_name, escalation_reason
    op.add_column('cases', sa.Column('case_type', sa.String(32), server_default='aml'))
    op.add_column('cases', sa.Column('customer_id', sa.String(64)))
    op.add_column('cases', sa.Column('customer_name', sa.String(256)))
    op.add_column('cases', sa.Column('assigned_to_name', sa.String(256)))
    op.add_column('cases', sa.Column('escalation_reason', sa.Text))
    op.create_index('idx_case_customer', 'cases', ['customer_id'])

    # SAR Reports: add customer_id, customer_name, filing_type, suspicious_activity_type,
    #              narrative, filing_reference, filing_date
    op.add_column('sar_reports', sa.Column('customer_id', sa.String(64)))
    op.add_column('sar_reports', sa.Column('customer_name', sa.String(256)))
    op.add_column('sar_reports', sa.Column('filing_type', sa.String(32)))
    op.add_column('sar_reports', sa.Column('suspicious_activity_type', sa.String(64)))
    op.add_column('sar_reports', sa.Column('narrative', sa.Text))
    op.add_column('sar_reports', sa.Column('filing_reference', sa.String(64)))
    op.add_column('sar_reports', sa.Column('filing_date', sa.DateTime(timezone=True)))
    op.create_index('idx_sar_customer', 'sar_reports', ['customer_id'])

    # CTR Reports: add transaction_id, filing_date
    op.add_column('ctr_reports', sa.Column('transaction_id', sa.String(64)))
    op.add_column('ctr_reports', sa.Column('filing_date', sa.DateTime(timezone=True)))

    # Audit Logs: add username, status
    op.add_column('audit_logs', sa.Column('username', sa.String(64)))
    op.add_column('audit_logs', sa.Column('status', sa.String(16), server_default='success'))


def downgrade() -> None:
    op.drop_column('audit_logs', 'status')
    op.drop_column('audit_logs', 'username')
    op.drop_column('ctr_reports', 'filing_date')
    op.drop_column('ctr_reports', 'transaction_id')
    op.drop_index('idx_sar_customer', 'sar_reports')
    op.drop_column('sar_reports', 'filing_date')
    op.drop_column('sar_reports', 'filing_reference')
    op.drop_column('sar_reports', 'narrative')
    op.drop_column('sar_reports', 'suspicious_activity_type')
    op.drop_column('sar_reports', 'filing_type')
    op.drop_column('sar_reports', 'customer_name')
    op.drop_column('sar_reports', 'customer_id')
    op.drop_index('idx_case_customer', 'cases')
    op.drop_column('cases', 'escalation_reason')
    op.drop_column('cases', 'assigned_to_name')
    op.drop_column('cases', 'customer_name')
    op.drop_column('cases', 'customer_id')
    op.drop_column('cases', 'case_type')
    op.drop_column('alerts', 'close_reason')
    op.drop_column('alerts', 'escalation_reason')
    op.drop_column('alerts', 'rule_id')
    op.drop_column('alerts', 'customer_name')
    op.drop_column('alerts', 'priority')
