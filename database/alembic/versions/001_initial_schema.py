"""Initial schema - all tables

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Monitored Transactions
    op.create_table(
        'monitored_transactions',
        sa.Column('transaction_id', sa.String(64), primary_key=True),
        sa.Column('customer_id', sa.String(64), nullable=False),
        sa.Column('account_id', sa.String(64)),
        sa.Column('transaction_type', sa.String(32)),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('channel', sa.String(32)),
        sa.Column('originator_country', sa.String(3)),
        sa.Column('beneficiary_country', sa.String(3)),
        sa.Column('beneficiary_id', sa.String(64)),
        sa.Column('risk_score', sa.Float, server_default='0'),
        sa.Column('is_suspicious', sa.Boolean, server_default='false'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', sa.JSON, server_default='{}'),
    )
    op.create_index('idx_txn_customer_time', 'monitored_transactions', ['customer_id', 'timestamp'])
    op.create_index('idx_txn_suspicious', 'monitored_transactions', ['is_suspicious'])
    op.create_index('idx_txn_customer', 'monitored_transactions', ['customer_id'])
    op.create_index('idx_txn_account', 'monitored_transactions', ['account_id'])

    # AML Rules
    op.create_table(
        'aml_rules',
        sa.Column('rule_id', sa.String(64), primary_key=True),
        sa.Column('name', sa.String(256), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(64)),
        sa.Column('threshold', sa.JSON),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('severity', sa.String(16), server_default='medium'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    # Rule Execution Logs
    op.create_table(
        'rule_execution_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('rule_id', sa.String(64), sa.ForeignKey('aml_rules.rule_id')),
        sa.Column('transaction_id', sa.String(64), sa.ForeignKey('monitored_transactions.transaction_id')),
        sa.Column('triggered', sa.Boolean, server_default='false'),
        sa.Column('score', sa.Float),
        sa.Column('details', sa.JSON),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_rule_exec_rule', 'rule_execution_logs', ['rule_id'])
    op.create_index('idx_rule_exec_txn', 'rule_execution_logs', ['transaction_id'])

    # Cases (must be before Alerts due to FK)
    op.create_table(
        'cases',
        sa.Column('case_id', sa.String(64), primary_key=True),
        sa.Column('title', sa.String(512), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(16), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(16), server_default='medium'),
        sa.Column('assigned_to', sa.String(64)),
        sa.Column('alert_ids', sa.JSON, server_default='[]'),
        sa.Column('customer_ids', sa.JSON, server_default='[]'),
        sa.Column('total_exposure', sa.Float, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('closed_at', sa.DateTime(timezone=True)),
        sa.Column('resolution', sa.Text),
    )
    op.create_index('idx_case_status', 'cases', ['status'])
    op.create_index('idx_case_priority', 'cases', ['priority'])
    op.create_index('idx_case_assigned', 'cases', ['assigned_to'])

    # Alerts
    op.create_table(
        'alerts',
        sa.Column('alert_id', sa.String(64), primary_key=True),
        sa.Column('alert_type', sa.String(32), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='new'),
        sa.Column('risk_score', sa.Float, server_default='0'),
        sa.Column('customer_id', sa.String(64)),
        sa.Column('transaction_id', sa.String(64)),
        sa.Column('description', sa.Text),
        sa.Column('triggered_rules', sa.JSON, server_default='[]'),
        sa.Column('assigned_to', sa.String(64)),
        sa.Column('case_id', sa.String(64), sa.ForeignKey('cases.case_id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('closed_at', sa.DateTime(timezone=True)),
        sa.Column('resolution', sa.Text),
        sa.Column('metadata', sa.JSON, server_default='{}'),
    )
    op.create_index('idx_alert_type', 'alerts', ['alert_type'])
    op.create_index('idx_alert_severity', 'alerts', ['severity'])
    op.create_index('idx_alert_status', 'alerts', ['status'])
    op.create_index('idx_alert_customer', 'alerts', ['customer_id'])
    op.create_index('idx_alert_assigned', 'alerts', ['assigned_to'])

    # Alert History
    op.create_table(
        'alert_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('alert_id', sa.String(64), sa.ForeignKey('alerts.alert_id')),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('performed_by', sa.String(64)),
        sa.Column('details', sa.JSON),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_alert_hist_alert', 'alert_history', ['alert_id'])

    # Investigation Notes
    op.create_table(
        'investigation_notes',
        sa.Column('note_id', sa.String(64), primary_key=True),
        sa.Column('case_id', sa.String(64), sa.ForeignKey('cases.case_id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('note_type', sa.String(32), server_default='investigation'),
        sa.Column('created_by', sa.String(64)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_note_case', 'investigation_notes', ['case_id'])

    # Evidence
    op.create_table(
        'evidence',
        sa.Column('evidence_id', sa.String(64), primary_key=True),
        sa.Column('case_id', sa.String(64), sa.ForeignKey('cases.case_id'), nullable=False),
        sa.Column('evidence_type', sa.String(32)),
        sa.Column('description', sa.Text),
        sa.Column('file_path', sa.String(512)),
        sa.Column('uploaded_by', sa.String(64)),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_evidence_case', 'evidence', ['case_id'])

    # Case History
    op.create_table(
        'case_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('case_id', sa.String(64), sa.ForeignKey('cases.case_id')),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('performed_by', sa.String(64)),
        sa.Column('details', sa.JSON),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_case_hist_case', 'case_history', ['case_id'])

    # SAR Reports
    op.create_table(
        'sar_reports',
        sa.Column('report_id', sa.String(64), primary_key=True),
        sa.Column('case_id', sa.String(64), sa.ForeignKey('cases.case_id')),
        sa.Column('status', sa.String(16), nullable=False, server_default='draft'),
        sa.Column('subject_name', sa.String(256)),
        sa.Column('subject_id', sa.String(64)),
        sa.Column('filing_institution', sa.String(256)),
        sa.Column('activity_description', sa.Text),
        sa.Column('amount_involved', sa.Float),
        sa.Column('activity_start_date', sa.DateTime(timezone=True)),
        sa.Column('activity_end_date', sa.DateTime(timezone=True)),
        sa.Column('bsa_reference', sa.String(64)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('filed_at', sa.DateTime(timezone=True)),
        sa.Column('filed_by', sa.String(64)),
    )
    op.create_index('idx_sar_case', 'sar_reports', ['case_id'])
    op.create_index('idx_sar_status', 'sar_reports', ['status'])

    # CTR Reports
    op.create_table(
        'ctr_reports',
        sa.Column('report_id', sa.String(64), primary_key=True),
        sa.Column('customer_name', sa.String(256)),
        sa.Column('customer_id', sa.String(64)),
        sa.Column('transaction_date', sa.DateTime(timezone=True)),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD'),
        sa.Column('transaction_type', sa.String(32)),
        sa.Column('institution_name', sa.String(256)),
        sa.Column('status', sa.String(16), server_default='filed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('filed_at', sa.DateTime(timezone=True)),
    )
    op.create_index('idx_ctr_customer', 'ctr_reports', ['customer_id'])

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('event_id', sa.String(64), primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('user_id', sa.String(64)),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('resource_type', sa.String(32)),
        sa.Column('resource_id', sa.String(64)),
        sa.Column('service', sa.String(64)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('details', sa.JSON),
    )
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('idx_audit_service', 'audit_logs', ['service'])
    op.create_index('idx_audit_user_time', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])

    # Customer Risk Profiles
    op.create_table(
        'customer_risk_profiles',
        sa.Column('customer_id', sa.String(64), primary_key=True),
        sa.Column('overall_risk_score', sa.Float, server_default='0'),
        sa.Column('risk_level', sa.String(16), server_default='low'),
        sa.Column('geographic_risk', sa.Float, server_default='0'),
        sa.Column('product_risk', sa.Float, server_default='0'),
        sa.Column('behavior_risk', sa.Float, server_default='0'),
        sa.Column('pep_status', sa.Boolean, server_default='false'),
        sa.Column('sanctions_match', sa.Boolean, server_default='false'),
        sa.Column('cdd_level', sa.String(16), server_default='standard'),
        sa.Column('review_frequency', sa.String(16), server_default='annual'),
        sa.Column('last_review_date', sa.DateTime(timezone=True)),
        sa.Column('next_review_date', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('factor_details', sa.JSON, server_default='{}'),
    )


def downgrade() -> None:
    op.drop_table('customer_risk_profiles')
    op.drop_table('audit_logs')
    op.drop_table('ctr_reports')
    op.drop_table('sar_reports')
    op.drop_table('case_history')
    op.drop_table('evidence')
    op.drop_table('investigation_notes')
    op.drop_table('alert_history')
    op.drop_table('alerts')
    op.drop_table('cases')
    op.drop_table('rule_execution_logs')
    op.drop_table('aml_rules')
    op.drop_table('monitored_transactions')
