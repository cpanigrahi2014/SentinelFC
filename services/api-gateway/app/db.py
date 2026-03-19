"""Database connection, session management, and seed utilities for API Gateway."""

import logging
import os
from typing import AsyncGenerator, Optional

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger(__name__)

# --- Connection Configuration ---

DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('POSTGRES_USER', 'actimize')}:{os.getenv('POSTGRES_PASSWORD', 'actimize_secret')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}"
    f"/{os.getenv('POSTGRES_DB', 'actimize')}"
)

engine = None
SessionLocal: Optional[async_sessionmaker] = None
db_available = False


async def init_db():
    """Initialize database engine, create tables, and seed if empty."""
    global engine, SessionLocal, db_available

    try:
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
        )
        SessionLocal = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        # Create all tables from models
        from database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        db_available = True
        logger.info("Database connected — tables ready")

        # Seed if tables are empty
        await seed_if_empty()

    except Exception as e:
        logger.warning("Database not available, using in-memory data: %s", e)
        db_available = False


async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """FastAPI dependency — yields an async session or None if DB is unavailable."""
    if not db_available or SessionLocal is None:
        yield None
        return
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Seed Functions ──────────────────────────────────────────────────

async def seed_if_empty():
    """Populate tables with initial demo data when they are empty."""
    if not db_available or SessionLocal is None:
        return

    from database.models import (
        Alert, Case, InvestigationNote,
        SuspiciousActivityReport, CurrencyTransactionReport, AuditLog,
    )

    async with SessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(Alert))
        if result.scalar() > 0:
            logger.info("Database already seeded — skipping")
            return

        logger.info("Seeding database with initial demo data …")

        # Import seed data from routes (the existing hardcoded lists)
        from .routes import ALERTS, CASES, CASE_NOTES, SAR_REPORTS, CTR_REPORTS, AUDIT_LOGS

        # ── Alerts ───────────────────────────────────
        for a in ALERTS:
            alert = Alert(
                alert_id=a["alert_id"],
                alert_type=a["alert_type"],
                severity=a["severity"],
                status=a["status"],
                risk_score=a.get("risk_score", 0),
                priority=a.get("priority", "medium"),
                customer_id=a.get("customer_id"),
                customer_name=a.get("customer_name"),
                description=a.get("description"),
                assigned_to=a.get("assigned_to"),
                rule_id=a.get("rule_id"),
                escalation_reason=a.get("escalation_reason"),
                close_reason=a.get("close_reason"),
            )
            session.add(alert)

        # ── Cases ────────────────────────────────────
        for c in CASES:
            case = Case(
                case_id=c["case_id"],
                title=c["title"],
                description=c.get("description", ""),
                status=c["status"],
                priority=c.get("priority", "medium"),
                case_type=c.get("case_type", "aml"),
                customer_id=c.get("customer_id"),
                customer_name=c.get("customer_name"),
                assigned_to=c.get("assigned_to"),
                assigned_to_name=c.get("assigned_to_name"),
                alert_ids=c.get("alert_ids", []),
                escalation_reason=c.get("escalation_reason"),
                resolution=c.get("resolution"),
            )
            session.add(case)

        # ── Investigation Notes ──────────────────────
        for case_id, notes in CASE_NOTES.items():
            for n in notes:
                note = InvestigationNote(
                    note_id=n["note_id"],
                    case_id=case_id,
                    content=n["content"],
                    note_type=n.get("note_type", "general"),
                    created_by=n.get("author"),
                )
                session.add(note)

        # ── SAR Reports ─────────────────────────────
        for s in SAR_REPORTS:
            sar = SuspiciousActivityReport(
                report_id=s["report_id"],
                case_id=s.get("case_id"),
                status=s["status"],
                subject_name=s.get("subject_name"),
                customer_id=s.get("customer_id"),
                customer_name=s.get("customer_name"),
                filing_type=s.get("filing_type"),
                suspicious_activity_type=s.get("suspicious_activity_type"),
                narrative=s.get("narrative"),
                amount_involved=s.get("amount_involved"),
                filing_reference=s.get("filing_reference"),
            )
            session.add(sar)

        # ── CTR Reports ─────────────────────────────
        for r in CTR_REPORTS:
            ctr = CurrencyTransactionReport(
                report_id=r["report_id"],
                customer_id=r.get("customer_id"),
                customer_name=r.get("customer_name"),
                amount=r["amount"],
                transaction_id=r.get("transaction_id"),
                status=r.get("status", "filed"),
            )
            session.add(ctr)

        # ── Audit Logs ──────────────────────────────
        for l in AUDIT_LOGS:
            log = AuditLog(
                event_id=l["event_id"],
                user_id=l.get("user_id"),
                username=l.get("username"),
                action=l["action"],
                resource_type=l.get("resource_type"),
                resource_id=l.get("resource_id"),
                service=l.get("service"),
                ip_address=l.get("ip_address"),
                details=l.get("details"),
                status=l.get("status", "success"),
            )
            session.add(log)

        await session.commit()
        logger.info("Seed complete — %d alerts, %d cases, %d SARs, %d CTRs, %d audit logs",
                     len(ALERTS), len(CASES), len(SAR_REPORTS), len(CTR_REPORTS), len(AUDIT_LOGS))
