# Original models.py Backup

```python
import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Float, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Join table for Buyer Favourite Farmer
buyer_favourite_farmers = Table(
    "buyer_favourite_farmers",
    Base.metadata,
    Column("buyer_id", UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), primary_key=True),
    Column("farmer_id", UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), primary_key=True),
)


class Admin(Base):
    __tablename__ = "admins"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="admin", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    phone_number = Column(String, default="Not Provided", nullable=False)
    address = Column(String, default="Not Provided", nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    rejected = Column(Boolean, default=False, nullable=False)
    suspended = Column(Boolean, default=False, nullable=False)
    status = Column(String, default="ACTIVE", nullable=False)
    status_change_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # New profile expansion fields
    soil_type = Column(String, default="Alluvial", nullable=True)
    land_document = Column(String, nullable=True)
    exact_location = Column(String, nullable=True)
    water_availability = Column(String, default="Yes", nullable=True)
    previous_crops = Column(String, nullable=True)
    loan_amount = Column(Float, default=0.0, nullable=True)
    
    crops = relationship("CropBatch", back_populates="farmer", cascade="all, delete-orphan")


class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone_number = Column(String, default="Not Provided", nullable=False)
    address = Column(String, default="Not Provided", nullable=False)
    location = Column(String, default="Not Provided", nullable=False)
    suspended = Column(Boolean, default=False, nullable=False)
    status = Column(String, default="ACTIVE", nullable=False)
    status_change_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    favourite_farmers = relationship(
        "Farmer",
        secondary=buyer_favourite_farmers,
        backref="favourited_by"
    )


class CropBatch(Base):
    __tablename__ = "crop_batches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(String, unique=True, nullable=False, index=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_name = Column(String, nullable=False)
    harvest_date = Column(String, nullable=False)
    farming_method = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    image_file_hash = Column(String, nullable=False)
    data_hash = Column(String, nullable=False)
    blockchain_tx_hash = Column(String, nullable=True)
    blockchain_hash = Column(String, nullable=True)
    verification_status = Column(String, default="UNVERIFIED", nullable=True)
    verified_at = Column(DateTime, nullable=True)
    qr_url = Column(String, nullable=False)
    quantity = Column(Float, default=100.0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    farmer = relationship("Farmer", back_populates="crops")


class VerificationLog(Base):
    __tablename__ = "verification_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(String, nullable=False, index=True)
    scan_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    verified_by_buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="SET NULL"), nullable=True)
    current_hash = Column(String, nullable=True)
    blockchain_hash = Column(String, nullable=True)
    device_type = Column(String, default="Unknown", nullable=True)


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(String, nullable=False, index=True)
    crop_name = Column(String, nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False)
    buyer_name = Column(String, nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    farmer_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    quantity = Column(Float, default=10.0, nullable=False)
    status = Column(String, default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    type = Column(String, nullable=False)


class OTPStore(Base):
    __tablename__ = "otps"
    email = Column(String, primary_key=True, index=True)
    otp = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)


class AdminLog(Base):
    __tablename__ = "admin_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    remarks = Column(String, nullable=True)


class SupportMessage(Base):
    __tablename__ = "support_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(String, nullable=False, index=True)
    sender_name = Column(String, nullable=False)
    sender_role = Column(String, nullable=False)
    recipient_id = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)



class AIFraudReport(Base):
    __tablename__ = "ai_fraud_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    farmer_name = Column(String, nullable=False)
    risk_score = Column(Float, nullable=False)
    reasons = Column(String, nullable=False)
    status = Column(String, default="PENDING_REVIEW", nullable=False)
    remarks = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_batch_id = Column(String, nullable=True)
    crop_name = Column(String, nullable=False)
    uploaded_image = Column(String, nullable=False)
    predicted_disease = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    organic_treatment = Column(String, nullable=False)
    chemical_treatment = Column(String, nullable=False)
    prevention = Column(String, nullable=False)
    description = Column(String, nullable=True)
    possible_causes = Column(String, nullable=True)
    expected_recovery_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class FraudAnalysis(Base):
    __tablename__ = "fraud_analyses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_batch_id = Column(String, ForeignKey("crop_batches.batch_id", ondelete="CASCADE"), nullable=False)
    risk_score = Column(Float, nullable=False)
    season_score = Column(Float, nullable=False)
    location_score = Column(Float, nullable=False)
    image_score = Column(Float, nullable=False)
    duplicate_score = Column(Float, nullable=False)
    final_status = Column(String, default="PENDING", nullable=False) # e.g. PENDING, FLAGGED, APPROVED, REJECTED
    recommendation = Column(Text, nullable=True)
    analysis_report = Column(Text, nullable=True)
    farmer_explanation = Column(Text, nullable=True)
    farmer_explanation_submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    farmer = relationship("Farmer")
    crop_batch = relationship("CropBatch")


class MarketPrice(Base):
    __tablename__ = "market_prices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    market = Column(String, nullable=False)
    price_min = Column(Float, nullable=False)
    price_max = Column(Float, nullable=False)
    price_avg = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    source = Column(String, default="eNAM", nullable=False)


class CropDemand(Base):
    __tablename__ = "crop_demand"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    demand_quantity = Column(Float, default=0.0, nullable=False)
    search_clicks = Column(Integer, default=0, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class CropSupply(Base):
    __tablename__ = "crop_supply"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    supply_quantity = Column(Float, default=0.0, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_type = Column(String, nullable=False) # FARMER, BUYER, ADMIN
    target_id = Column(String, nullable=False) # 'platform' or specific user UUID
    data = Column(Text, nullable=False) # JSON serialized analytics data
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_name = Column(String, nullable=False, index=True)
    prediction_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    target_month = Column(Integer, nullable=False)
    predicted_price_avg = Column(Float, nullable=False)
    predicted_demand_index = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String, default="v1.0", nullable=False)


class AgriExpert(Base):
    __tablename__ = "agri_experts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    location = Column(String, nullable=False, index=True) # e.g. Kolar, Nashik
    expertise = Column(String, nullable=False) # e.g. Pest Control, Soil Nutrition
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class VisionAnalysis(Base):
    """Stores results from the Computer Vision analysis pipeline."""
    __tablename__ = "vision_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_batch_id = Column(String, nullable=True, index=True)
    uploaded_image = Column(String, nullable=False)
    annotated_image = Column(String, nullable=True)

    # Crop detection
    predicted_crop = Column(String, nullable=True)
    crop_confidence = Column(Float, default=0.0)
    crop_bbox = Column(String, nullable=True)  # JSON string

    # Disease detection
    predicted_disease = Column(String, nullable=True)
    disease_confidence = Column(Float, default=0.0)
    disease_severity = Column(String, nullable=True)
    disease_description = Column(String, nullable=True)
    is_healthy = Column(Boolean, default=True)
    recommendation = Column(String, nullable=True)
    
    # AI Assistant copied treatment fields
    organic_treatment = Column(String, nullable=True)
    chemical_treatment = Column(String, nullable=True)
    prevention = Column(String, nullable=True)
    expected_recovery_time = Column(String, nullable=True)
    possible_causes = Column(String, nullable=True)

    # Image quality
    image_quality = Column(Float, default=0.0)
    quality_metrics = Column(String, nullable=True)  # JSON string
    quality_grade = Column(String, nullable=True)

    # Validation
    image_valid = Column(String, default="PASS")
    validation_issues = Column(String, nullable=True)  # JSON string

    # Duplicate detection
    duplicate_probability = Column(Float, default=0.0)
    image_hash = Column(String, nullable=True, index=True)

    # Metadata
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class VisionCorrection(Base):
    """Stores admin-corrected crop & disease labels for specific image hashes."""
    __tablename__ = "vision_corrections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_hash = Column(String, nullable=False, unique=True, index=True)
    correct_crop = Column(String, nullable=False)
    correct_disease = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class RAGDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    crop_category = Column(String, nullable=True)
    language = Column(String, default="en")
    source = Column(String, default="Government")
    chunk_count = Column(Integer, default=0)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(String, default="ACTIVE")


class RAGChatHistory(Base):
    __tablename__ = "rag_chat_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_role = Column(String, nullable=False)  # "farmer" or "buyer"
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    sources = Column(String, nullable=True)  # JSON string
    confidence = Column(Float, default=0.0)
    language = Column(String, default="en")
    search_type = Column(String, default="hybrid")
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WeatherHistory(Base):
    __tablename__ = "weather_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    rainfall = Column(Float, default=0.0)
    wind_speed = Column(Float, default=0.0)
    pressure = Column(Float, default=1013.0)
    uv_index = Column(Float, default=0.0)
    cloud_cover = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=False, index=True)
    forecast_time = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    rainfall = Column(Float, default=0.0)
    wind_speed = Column(Float, default=0.0)
    pressure = Column(Float, default=1013.0)
    uv_index = Column(Float, default=0.0)
    cloud_cover = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WeatherAlert(Base):
    __tablename__ = "weather_alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=False, index=True)
    alert_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WeatherRecommendation(Base):
    __tablename__ = "weather_recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=False, index=True)
    crop_type = Column(String, nullable=False)
    recommendation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WeatherCache(Base):
    __tablename__ = "weather_cache"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=False, unique=True, index=True)
    current_data = Column(Text, nullable=False)
    forecast_data = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WhatsappUser(Base):
    __tablename__ = "whatsapp_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    role = Column(String, nullable=False)  # 'farmer', 'buyer', 'admin'
    verified = Column(Boolean, default=False, nullable=False)
    verification_otp = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WhatsappConversation(Base):
    __tablename__ = "whatsapp_conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'ai'
    message_type = Column(String, default="text", nullable=False)  # 'text', 'image', 'voice', 'location', 'document'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WhatsappMedia(Base):
    __tablename__ = "whatsapp_media"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False)
    media_url = Column(String, nullable=False)
    media_type = Column(String, nullable=False)  # 'image', 'voice', 'pdf'
    processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class WhatsappNotification(Base):
    __tablename__ = "whatsapp_notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # 'pending', 'sent', 'failed'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class TelegramUser(Base):
    __tablename__ = "telegram_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    role = Column(String, nullable=False)  # 'farmer', 'buyer', 'admin'
    verified = Column(Boolean, default=False, nullable=False)
    verification_otp = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class TelegramConversation(Base):
    __tablename__ = "telegram_conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(String, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    session_id = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    sender = Column(String, nullable=False)  # 'user' or 'ai'
    message_type = Column(String, default="text", nullable=False)  # 'text', 'image', 'voice', 'location', 'document'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class TelegramMedia(Base):
    __tablename__ = "telegram_media"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False)
    media_url = Column(String, nullable=False)
    media_type = Column(String, nullable=False)  # 'image', 'voice', 'pdf'
    processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class TelegramNotification(Base):
    __tablename__ = "telegram_notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # 'pending', 'sent', 'failed'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class AgriShieldReport(Base):
    __tablename__ = "agrishield_reports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_batch_id = Column(String, nullable=False, index=True)
    overall_risk_score = Column(Float, nullable=False)
    final_status = Column(String, default="PENDING_REVIEW", nullable=False)  # APPROVED, WARNED, PENDING_REVIEW
    recommendation = Column(Text, nullable=True)
    analysis_report = Column(Text, nullable=True)  # JSON string
    farmer_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class TrustScore(Base):
    __tablename__ = "trust_scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, unique=True)
    score = Column(Float, default=80.0, nullable=False)  # Default trust starts at 80
    verified_uploads_count = Column(Integer, default=0, nullable=False)
    successful_sales_count = Column(Integer, default=0, nullable=False)
    fraud_reports_count = Column(Integer, default=0, nullable=False)
    rejected_uploads_count = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_batch_id = Column(String, nullable=True, index=True)
    alert_type = Column(String, nullable=False)  # e.g., "season_mismatch", "weather_anomaly", "duplicate_image", "ip_jump"
    message = Column(Text, nullable=False)
    severity = Column(String, default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH
    resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class BehaviorLog(Base):
    __tablename__ = "behavior_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_role = Column(String, nullable=False)  # farmer, buyer, admin
    action = Column(String, nullable=False)  # e.g. login, add_crop, delete_crop, scan_qr
    ip_address = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_batch_id = Column(String, nullable=False, unique=True, index=True)
    season_score = Column(Float, default=0.0)
    location_score = Column(Float, default=0.0)
    image_score = Column(Float, default=0.0)
    duplicate_score = Column(Float, default=0.0)
    weather_score = Column(Float, default=0.0)
    blockchain_score = Column(Float, default=0.0)
    cv_score = Column(Float, default=0.0)
    marketplace_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
```
