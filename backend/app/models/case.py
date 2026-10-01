from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    age_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    wbc: Mapped[float | None] = mapped_column(Float, nullable=True)
    rbc: Mapped[float | None] = mapped_column(Float, nullable=True)
    hemoglobin: Mapped[float | None] = mapped_column(Float, nullable=True)
    hematocrit: Mapped[float | None] = mapped_column(Float, nullable=True)
    platelets: Mapped[float | None] = mapped_column(Float, nullable=True)
    blasts_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    modality: Mapped[str] = mapped_column(String(32), default="unknown")
    predicted_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    predicted_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    routing: Mapped[str | None] = mapped_column(String(64), nullable=True)
    xai_heatmap_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    xai_shap_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    doctor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    patient: Mapped["User"] = relationship(back_populates="cases", foreign_keys=[patient_id])  # noqa: F821
    events: Mapped[list["HistoryEvent"]] = relationship(back_populates="case")  # noqa: F821
