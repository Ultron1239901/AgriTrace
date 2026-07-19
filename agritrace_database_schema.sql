-- ===================================================
-- AGRITRACE DECENTRALIZED POSTGRESQL DATABASE SCHEMA
-- ===================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE admins (
	id UUID NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	role VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_admins_email ON admins (email);

CREATE TABLE farmers (
	id UUID NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	location VARCHAR NOT NULL, 
	phone_number VARCHAR NOT NULL, 
	address VARCHAR NOT NULL, 
	verified BOOLEAN NOT NULL, 
	rejected BOOLEAN NOT NULL, 
	suspended BOOLEAN NOT NULL, 
	status VARCHAR NOT NULL, 
	status_change_reason VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	soil_type VARCHAR, 
	land_document VARCHAR, 
	exact_location VARCHAR, 
	water_availability VARCHAR, 
	previous_crops VARCHAR, 
	loan_amount FLOAT, 
	security_question VARCHAR, 
	security_question_answer VARCHAR, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_farmers_email ON farmers (email);

CREATE TABLE buyers (
	id UUID NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	phone_number VARCHAR NOT NULL, 
	address VARCHAR NOT NULL, 
	location VARCHAR NOT NULL, 
	suspended BOOLEAN NOT NULL, 
	status VARCHAR NOT NULL, 
	status_change_reason VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	security_question VARCHAR, 
	security_question_answer VARCHAR, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_buyers_email ON buyers (email);

CREATE TABLE notifications (
	id UUID NOT NULL, 
	user_id VARCHAR NOT NULL, 
	message VARCHAR NOT NULL, 
	is_read BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	type VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE TABLE otps (
	email VARCHAR NOT NULL, 
	otp VARCHAR NOT NULL, 
	expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (email)
);

CREATE INDEX ix_otps_email ON otps (email);

CREATE TABLE support_messages (
	id UUID NOT NULL, 
	sender_id VARCHAR NOT NULL, 
	sender_name VARCHAR NOT NULL, 
	sender_role VARCHAR NOT NULL, 
	recipient_id VARCHAR NOT NULL, 
	message VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_support_messages_sender_id ON support_messages (sender_id);

CREATE INDEX ix_support_messages_recipient_id ON support_messages (recipient_id);

CREATE TABLE market_prices (
	id UUID NOT NULL, 
	crop_name VARCHAR NOT NULL, 
	state VARCHAR NOT NULL, 
	district VARCHAR NOT NULL, 
	market VARCHAR NOT NULL, 
	price_min FLOAT NOT NULL, 
	price_max FLOAT NOT NULL, 
	price_avg FLOAT NOT NULL, 
	date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	source VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_market_prices_crop_name ON market_prices (crop_name);

CREATE TABLE crop_demand (
	id UUID NOT NULL, 
	crop_name VARCHAR NOT NULL, 
	state VARCHAR NOT NULL, 
	district VARCHAR NOT NULL, 
	demand_quantity FLOAT NOT NULL, 
	search_clicks INTEGER NOT NULL, 
	month INTEGER NOT NULL, 
	year INTEGER NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_crop_demand_crop_name ON crop_demand (crop_name);

CREATE TABLE crop_supply (
	id UUID NOT NULL, 
	crop_name VARCHAR NOT NULL, 
	state VARCHAR NOT NULL, 
	district VARCHAR NOT NULL, 
	supply_quantity FLOAT NOT NULL, 
	month INTEGER NOT NULL, 
	year INTEGER NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_crop_supply_crop_name ON crop_supply (crop_name);

CREATE TABLE analytics_snapshots (
	id UUID NOT NULL, 
	snapshot_type VARCHAR NOT NULL, 
	target_id VARCHAR NOT NULL, 
	data TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE prediction_history (
	id UUID NOT NULL, 
	crop_name VARCHAR NOT NULL, 
	prediction_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	target_month INTEGER NOT NULL, 
	predicted_price_avg FLOAT NOT NULL, 
	predicted_demand_index FLOAT NOT NULL, 
	confidence FLOAT NOT NULL, 
	model_version VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_prediction_history_crop_name ON prediction_history (crop_name);

CREATE TABLE agri_experts (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	phone_number VARCHAR NOT NULL, 
	location VARCHAR NOT NULL, 
	expertise VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_agri_experts_location ON agri_experts (location);

CREATE TABLE vision_corrections (
	id UUID NOT NULL, 
	image_hash VARCHAR NOT NULL, 
	correct_crop VARCHAR NOT NULL, 
	correct_disease VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_vision_corrections_image_hash ON vision_corrections (image_hash);

CREATE TABLE rag_chat_history (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	user_role VARCHAR NOT NULL, 
	question VARCHAR NOT NULL, 
	answer VARCHAR NOT NULL, 
	sources VARCHAR, 
	confidence FLOAT, 
	language VARCHAR, 
	search_type VARCHAR, 
	processing_time_ms FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE weather_history (
	id UUID NOT NULL, 
	location VARCHAR NOT NULL, 
	temperature FLOAT NOT NULL, 
	humidity FLOAT NOT NULL, 
	rainfall FLOAT, 
	wind_speed FLOAT, 
	pressure FLOAT, 
	uv_index FLOAT, 
	cloud_cover FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_weather_history_location ON weather_history (location);

CREATE TABLE weather_forecasts (
	id UUID NOT NULL, 
	location VARCHAR NOT NULL, 
	forecast_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	temperature FLOAT NOT NULL, 
	humidity FLOAT NOT NULL, 
	rainfall FLOAT, 
	wind_speed FLOAT, 
	pressure FLOAT, 
	uv_index FLOAT, 
	cloud_cover FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_weather_forecasts_location ON weather_forecasts (location);

CREATE TABLE weather_alerts (
	id UUID NOT NULL, 
	location VARCHAR NOT NULL, 
	alert_type VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_weather_alerts_location ON weather_alerts (location);

CREATE TABLE weather_recommendations (
	id UUID NOT NULL, 
	location VARCHAR NOT NULL, 
	crop_type VARCHAR NOT NULL, 
	recommendation TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_weather_recommendations_location ON weather_recommendations (location);

CREATE TABLE weather_cache (
	id UUID NOT NULL, 
	location VARCHAR NOT NULL, 
	current_data TEXT NOT NULL, 
	forecast_data TEXT NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_weather_cache_location ON weather_cache (location);

CREATE TABLE whatsapp_users (
	id UUID NOT NULL, 
	phone_number VARCHAR NOT NULL, 
	user_id UUID, 
	role VARCHAR NOT NULL, 
	verified BOOLEAN NOT NULL, 
	verification_otp VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_whatsapp_users_phone_number ON whatsapp_users (phone_number);

CREATE TABLE whatsapp_conversations (
	id UUID NOT NULL, 
	phone_number VARCHAR NOT NULL, 
	user_id UUID, 
	session_id VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	sender VARCHAR NOT NULL, 
	message_type VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_whatsapp_conversations_session_id ON whatsapp_conversations (session_id);

CREATE INDEX ix_whatsapp_conversations_phone_number ON whatsapp_conversations (phone_number);

CREATE TABLE whatsapp_media (
	id UUID NOT NULL, 
	conversation_id UUID NOT NULL, 
	media_url VARCHAR NOT NULL, 
	media_type VARCHAR NOT NULL, 
	processed BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE whatsapp_notifications (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	title VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	status VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_whatsapp_notifications_user_id ON whatsapp_notifications (user_id);

CREATE TABLE telegram_users (
	id UUID NOT NULL, 
	chat_id VARCHAR NOT NULL, 
	user_id UUID, 
	role VARCHAR NOT NULL, 
	verified BOOLEAN NOT NULL, 
	verification_otp VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_telegram_users_chat_id ON telegram_users (chat_id);

CREATE TABLE telegram_conversations (
	id UUID NOT NULL, 
	chat_id VARCHAR NOT NULL, 
	user_id UUID, 
	session_id VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	sender VARCHAR NOT NULL, 
	message_type VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_telegram_conversations_chat_id ON telegram_conversations (chat_id);

CREATE INDEX ix_telegram_conversations_session_id ON telegram_conversations (session_id);

CREATE TABLE telegram_media (
	id UUID NOT NULL, 
	conversation_id UUID NOT NULL, 
	media_url VARCHAR NOT NULL, 
	media_type VARCHAR NOT NULL, 
	processed BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE telegram_notifications (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	title VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	status VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_telegram_notifications_user_id ON telegram_notifications (user_id);

CREATE TABLE behavior_logs (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	user_role VARCHAR NOT NULL, 
	action VARCHAR NOT NULL, 
	ip_address VARCHAR, 
	metadata_json TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_behavior_logs_user_id ON behavior_logs (user_id);

CREATE TABLE risk_assessments (
	id UUID NOT NULL, 
	crop_batch_id VARCHAR NOT NULL, 
	season_score FLOAT, 
	location_score FLOAT, 
	image_score FLOAT, 
	duplicate_score FLOAT, 
	weather_score FLOAT, 
	blockchain_score FLOAT, 
	cv_score FLOAT, 
	marketplace_score FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_risk_assessments_crop_batch_id ON risk_assessments (crop_batch_id);

CREATE TABLE buyer_favourite_farmers (
	buyer_id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	PRIMARY KEY (buyer_id, farmer_id), 
	FOREIGN KEY(buyer_id) REFERENCES buyers (id) ON DELETE CASCADE, 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE TABLE crop_batches (
	id UUID NOT NULL, 
	batch_id VARCHAR NOT NULL, 
	farmer_id UUID NOT NULL, 
	crop_name VARCHAR NOT NULL, 
	harvest_date VARCHAR NOT NULL, 
	farming_method VARCHAR NOT NULL, 
	image_url VARCHAR NOT NULL, 
	image_file_hash VARCHAR NOT NULL, 
	data_hash VARCHAR NOT NULL, 
	blockchain_tx_hash VARCHAR, 
	blockchain_hash VARCHAR, 
	verification_status VARCHAR, 
	verified_at TIMESTAMP WITHOUT TIME ZONE, 
	qr_url VARCHAR NOT NULL, 
	quantity FLOAT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_crop_batches_batch_id ON crop_batches (batch_id);

CREATE TABLE verification_logs (
	id UUID NOT NULL, 
	batch_id VARCHAR NOT NULL, 
	scan_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	status VARCHAR NOT NULL, 
	ip_address VARCHAR NOT NULL, 
	verified_by_buyer_id UUID, 
	current_hash VARCHAR, 
	blockchain_hash VARCHAR, 
	device_type VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(verified_by_buyer_id) REFERENCES buyers (id) ON DELETE SET NULL
);

CREATE INDEX ix_verification_logs_batch_id ON verification_logs (batch_id);

CREATE TABLE purchase_requests (
	id UUID NOT NULL, 
	batch_id VARCHAR NOT NULL, 
	crop_name VARCHAR NOT NULL, 
	buyer_id UUID NOT NULL, 
	buyer_name VARCHAR NOT NULL, 
	farmer_id UUID NOT NULL, 
	farmer_name VARCHAR NOT NULL, 
	message VARCHAR NOT NULL, 
	quantity FLOAT NOT NULL, 
	status VARCHAR NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(buyer_id) REFERENCES buyers (id) ON DELETE CASCADE, 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE INDEX ix_purchase_requests_batch_id ON purchase_requests (batch_id);

CREATE TABLE admin_logs (
	id UUID NOT NULL, 
	admin_id UUID NOT NULL, 
	action VARCHAR NOT NULL, 
	target_type VARCHAR NOT NULL, 
	target_id VARCHAR NOT NULL, 
	timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	remarks VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_id) REFERENCES admins (id) ON DELETE CASCADE
);

CREATE TABLE ai_fraud_reports (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	farmer_name VARCHAR NOT NULL, 
	risk_score FLOAT NOT NULL, 
	reasons VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	remarks VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE TABLE disease_predictions (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	crop_batch_id VARCHAR, 
	crop_name VARCHAR NOT NULL, 
	uploaded_image VARCHAR NOT NULL, 
	predicted_disease VARCHAR NOT NULL, 
	confidence FLOAT NOT NULL, 
	severity VARCHAR NOT NULL, 
	organic_treatment VARCHAR NOT NULL, 
	chemical_treatment VARCHAR NOT NULL, 
	prevention VARCHAR NOT NULL, 
	description VARCHAR, 
	possible_causes VARCHAR, 
	expected_recovery_time VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE TABLE vision_analyses (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	crop_batch_id VARCHAR, 
	uploaded_image VARCHAR NOT NULL, 
	annotated_image VARCHAR, 
	predicted_crop VARCHAR, 
	crop_confidence FLOAT, 
	crop_bbox VARCHAR, 
	predicted_disease VARCHAR, 
	disease_confidence FLOAT, 
	disease_severity VARCHAR, 
	disease_description VARCHAR, 
	is_healthy BOOLEAN, 
	recommendation VARCHAR, 
	organic_treatment VARCHAR, 
	chemical_treatment VARCHAR, 
	prevention VARCHAR, 
	expected_recovery_time VARCHAR, 
	possible_causes VARCHAR, 
	image_quality FLOAT, 
	quality_metrics VARCHAR, 
	quality_grade VARCHAR, 
	image_valid VARCHAR, 
	validation_issues VARCHAR, 
	duplicate_probability FLOAT, 
	image_hash VARCHAR, 
	processing_time_ms FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE INDEX ix_vision_analyses_image_hash ON vision_analyses (image_hash);

CREATE INDEX ix_vision_analyses_crop_batch_id ON vision_analyses (crop_batch_id);

CREATE INDEX ix_vision_analyses_farmer_id ON vision_analyses (farmer_id);

CREATE TABLE rag_documents (
	id UUID NOT NULL, 
	filename VARCHAR NOT NULL, 
	file_path VARCHAR NOT NULL, 
	file_type VARCHAR NOT NULL, 
	file_size INTEGER NOT NULL, 
	crop_category VARCHAR, 
	language VARCHAR, 
	source VARCHAR, 
	chunk_count INTEGER, 
	uploaded_by UUID, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	status VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uploaded_by) REFERENCES admins (id)
);

CREATE TABLE agrishield_reports (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	crop_batch_id VARCHAR NOT NULL, 
	overall_risk_score FLOAT NOT NULL, 
	final_status VARCHAR NOT NULL, 
	recommendation TEXT, 
	analysis_report TEXT, 
	farmer_explanation TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE INDEX ix_agrishield_reports_crop_batch_id ON agrishield_reports (crop_batch_id);

CREATE TABLE trust_scores (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	score FLOAT NOT NULL, 
	verified_uploads_count INTEGER NOT NULL, 
	successful_sales_count INTEGER NOT NULL, 
	fraud_reports_count INTEGER NOT NULL, 
	rejected_uploads_count INTEGER NOT NULL, 
	last_updated TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (farmer_id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE TABLE fraud_alerts (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	crop_batch_id VARCHAR, 
	alert_type VARCHAR NOT NULL, 
	message TEXT NOT NULL, 
	severity VARCHAR NOT NULL, 
	resolved BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE
);

CREATE INDEX ix_fraud_alerts_crop_batch_id ON fraud_alerts (crop_batch_id);

CREATE TABLE fraud_analyses (
	id UUID NOT NULL, 
	farmer_id UUID NOT NULL, 
	crop_batch_id VARCHAR NOT NULL, 
	risk_score FLOAT NOT NULL, 
	season_score FLOAT NOT NULL, 
	location_score FLOAT NOT NULL, 
	image_score FLOAT NOT NULL, 
	duplicate_score FLOAT NOT NULL, 
	final_status VARCHAR NOT NULL, 
	recommendation TEXT, 
	analysis_report TEXT, 
	farmer_explanation TEXT, 
	farmer_explanation_submitted_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farmer_id) REFERENCES farmers (id) ON DELETE CASCADE, 
	FOREIGN KEY(crop_batch_id) REFERENCES crop_batches (batch_id) ON DELETE CASCADE
);

-- ===================================================
-- INITIAL SYSTEM SEEDS (STANDARD ROLES & SAMPLES)
-- ===================================================

INSERT INTO admins (id, name, email, password_hash, created_at, role) VALUES
('93f39d1b-0294-4d89-b883-9b6f3127818b', 'System Administrator', 'admin@agritrace.com', '$2b$12$R.S1u9pC6n1c2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i', NOW(), 'admin')
ON CONFLICT (id) DO NOTHING;
