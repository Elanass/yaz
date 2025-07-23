"""
Database migration script for cohort management tables
Run this script to create the necessary tables for cohort functionality
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL - adjust as needed
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/gastric_adci")

async def create_cohort_tables():
    """Create cohort management tables"""
    
    engine = create_async_engine(DATABASE_URL)
    
    # SQL for creating tables
    create_tables_sql = """
    -- Create enum types for cohort management
    DO $$ BEGIN
        CREATE TYPE cohort_upload_format AS ENUM ('manual', 'csv', 'json', 'fhir');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    
    DO $$ BEGIN
        CREATE TYPE cohort_status AS ENUM ('draft', 'uploading', 'validating', 'ready', 'processing', 'completed', 'failed');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    
    DO $$ BEGIN
        CREATE TYPE inference_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    
    -- Create cohort_studies table
    CREATE TABLE IF NOT EXISTS cohort_studies (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        study_name VARCHAR(255) NOT NULL,
        description TEXT,
        uploaded_by VARCHAR(255) NOT NULL,
        format_type cohort_upload_format NOT NULL DEFAULT 'manual',
        status cohort_status NOT NULL DEFAULT 'draft',
        total_patients INTEGER DEFAULT 0,
        engine_name VARCHAR(50) NOT NULL,
        include_alternatives BOOLEAN DEFAULT TRUE,
        confidence_threshold FLOAT DEFAULT 0.75,
        ipfs_hash VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP WITH TIME ZONE,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    
    -- Create cohort_patients table
    CREATE TABLE IF NOT EXISTS cohort_patients (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        cohort_study_id UUID NOT NULL REFERENCES cohort_studies(id) ON DELETE CASCADE,
        patient_id VARCHAR(255) NOT NULL,
        age INTEGER,
        gender VARCHAR(20),
        clinical_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
        validation_status VARCHAR(50) DEFAULT 'pending',
        validation_errors JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(cohort_study_id, patient_id)
    );
    
    -- Create inference_sessions table
    CREATE TABLE IF NOT EXISTS inference_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        cohort_study_id UUID NOT NULL REFERENCES cohort_studies(id) ON DELETE CASCADE,
        session_name VARCHAR(255) NOT NULL,
        status inference_status NOT NULL DEFAULT 'pending',
        processed_by VARCHAR(255) NOT NULL,
        total_patients INTEGER DEFAULT 0,
        processed_patients INTEGER DEFAULT 0,
        failed_patients INTEGER DEFAULT 0,
        engine_name VARCHAR(50) NOT NULL,
        engine_version VARCHAR(20),
        confidence_threshold FLOAT DEFAULT 0.75,
        processing_start_time TIMESTAMP WITH TIME ZONE,
        processing_end_time TIMESTAMP WITH TIME ZONE,
        summary_stats JSONB DEFAULT '{}'::jsonb,
        ipfs_hash VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create patient_decision_results table
    CREATE TABLE IF NOT EXISTS patient_decision_results (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL REFERENCES inference_sessions(id) ON DELETE CASCADE,
        patient_id VARCHAR(255) NOT NULL,
        engine_name VARCHAR(50) NOT NULL,
        engine_version VARCHAR(20),
        recommendation JSONB NOT NULL,
        confidence_score FLOAT NOT NULL,
        confidence_level VARCHAR(20) NOT NULL,
        risk_score FLOAT,
        risk_level VARCHAR(20),
        evidence_summary JSONB DEFAULT '[]'::jsonb,
        reasoning_chain JSONB DEFAULT '[]'::jsonb,
        alternative_options JSONB DEFAULT '[]'::jsonb,
        warnings JSONB DEFAULT '[]'::jsonb,
        processing_time_ms FLOAT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(session_id, patient_id)
    );
    
    -- Create cohort_export_tasks table
    CREATE TABLE IF NOT EXISTS cohort_export_tasks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL REFERENCES inference_sessions(id) ON DELETE CASCADE,
        export_format VARCHAR(20) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        requested_by VARCHAR(255) NOT NULL,
        filters JSONB DEFAULT '{}'::jsonb,
        file_size BIGINT,
        ipfs_hash VARCHAR(255),
        download_count INTEGER DEFAULT 0,
        expires_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP WITH TIME ZONE
    );
    
    -- Create cohort_hypotheses table
    CREATE TABLE IF NOT EXISTS cohort_hypotheses (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL REFERENCES inference_sessions(id) ON DELETE CASCADE,
        hypothesis_name VARCHAR(255) NOT NULL,
        description TEXT,
        hypothesis_type VARCHAR(50) NOT NULL,
        parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
        results JSONB DEFAULT '{}'::jsonb,
        statistical_significance FLOAT,
        p_value FLOAT,
        confidence_interval JSONB,
        created_by VARCHAR(255) NOT NULL,
        status VARCHAR(20) DEFAULT 'draft',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_cohort_studies_uploaded_by ON cohort_studies(uploaded_by);
    CREATE INDEX IF NOT EXISTS idx_cohort_studies_status ON cohort_studies(status);
    CREATE INDEX IF NOT EXISTS idx_cohort_studies_created_at ON cohort_studies(created_at);
    
    CREATE INDEX IF NOT EXISTS idx_cohort_patients_cohort_id ON cohort_patients(cohort_study_id);
    CREATE INDEX IF NOT EXISTS idx_cohort_patients_patient_id ON cohort_patients(patient_id);
    
    CREATE INDEX IF NOT EXISTS idx_inference_sessions_cohort_id ON inference_sessions(cohort_study_id);
    CREATE INDEX IF NOT EXISTS idx_inference_sessions_status ON inference_sessions(status);
    CREATE INDEX IF NOT EXISTS idx_inference_sessions_processed_by ON inference_sessions(processed_by);
    
    CREATE INDEX IF NOT EXISTS idx_patient_results_session_id ON patient_decision_results(session_id);
    CREATE INDEX IF NOT EXISTS idx_patient_results_patient_id ON patient_decision_results(patient_id);
    CREATE INDEX IF NOT EXISTS idx_patient_results_confidence ON patient_decision_results(confidence_score);
    CREATE INDEX IF NOT EXISTS idx_patient_results_risk ON patient_decision_results(risk_score);
    
    CREATE INDEX IF NOT EXISTS idx_export_tasks_session_id ON cohort_export_tasks(session_id);
    CREATE INDEX IF NOT EXISTS idx_export_tasks_status ON cohort_export_tasks(status);
    CREATE INDEX IF NOT EXISTS idx_export_tasks_requested_by ON cohort_export_tasks(requested_by);
    
    CREATE INDEX IF NOT EXISTS idx_hypotheses_session_id ON cohort_hypotheses(session_id);
    CREATE INDEX IF NOT EXISTS idx_hypotheses_created_by ON cohort_hypotheses(created_by);
    
    -- Update timestamp triggers
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    
    DROP TRIGGER IF EXISTS update_cohort_studies_updated_at ON cohort_studies;
    CREATE TRIGGER update_cohort_studies_updated_at 
        BEFORE UPDATE ON cohort_studies 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_cohort_patients_updated_at ON cohort_patients;
    CREATE TRIGGER update_cohort_patients_updated_at 
        BEFORE UPDATE ON cohort_patients 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_inference_sessions_updated_at ON inference_sessions;
    CREATE TRIGGER update_inference_sessions_updated_at 
        BEFORE UPDATE ON inference_sessions 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    DROP TRIGGER IF EXISTS update_cohort_hypotheses_updated_at ON cohort_hypotheses;
    CREATE TRIGGER update_cohort_hypotheses_updated_at 
        BEFORE UPDATE ON cohort_hypotheses 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
    
    try:
        async with engine.begin() as conn:
            # Execute the SQL
            await conn.execute(text(create_tables_sql))
            logger.info("Successfully created cohort management tables")
            
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

async def create_sample_data():
    """Create sample cohort data for testing"""
    
    engine = create_async_engine(DATABASE_URL)
    
    sample_data_sql = """
    -- Insert sample cohort study
    INSERT INTO cohort_studies (
        id, study_name, description, uploaded_by, format_type, status, 
        total_patients, engine_name, confidence_threshold
    ) VALUES (
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'Sample Gastric Cancer Cohort',
        'A sample cohort for testing the cohort management system',
        'sample_user',
        'manual',
        'ready',
        3,
        'adci',
        0.75
    ) ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample patients
    INSERT INTO cohort_patients (
        cohort_study_id, patient_id, age, gender, clinical_parameters, validation_status
    ) VALUES 
    (
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'SAMPLE_001',
        65,
        'male',
        '{"tumor_stage": "T2N1M0", "histology": "adenocarcinoma", "ecog_score": 1, "comorbidities": ["diabetes"]}',
        'valid'
    ),
    (
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'SAMPLE_002',
        72,
        'female',
        '{"tumor_stage": "T3N2M0", "histology": "signet_ring", "ecog_score": 0, "comorbidities": []}',
        'valid'
    ),
    (
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'SAMPLE_003',
        58,
        'male',
        '{"tumor_stage": "T1N0M0", "histology": "adenocarcinoma", "ecog_score": 0, "comorbidities": ["hypertension"]}',
        'valid'
    )
    ON CONFLICT (cohort_study_id, patient_id) DO NOTHING;
    
    -- Insert sample inference session
    INSERT INTO inference_sessions (
        id, cohort_study_id, session_name, status, processed_by, 
        total_patients, processed_patients, engine_name, engine_version,
        confidence_threshold, processing_start_time, processing_end_time,
        summary_stats
    ) VALUES (
        'b2c3d4e5-f6g7-8901-bcde-f21234567890',
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'Initial Processing Session',
        'completed',
        'sample_user',
        3,
        3,
        'adci',
        '2.1.0',
        0.75,
        CURRENT_TIMESTAMP - INTERVAL '10 minutes',
        CURRENT_TIMESTAMP - INTERVAL '2 minutes',
        '{"avg_confidence": 0.82, "high_confidence_count": 2, "processing_time": 480}'
    ) ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample decision results
    INSERT INTO patient_decision_results (
        session_id, patient_id, engine_name, engine_version, recommendation,
        confidence_score, confidence_level, risk_score, risk_level,
        evidence_summary, reasoning_chain, processing_time_ms
    ) VALUES 
    (
        'b2c3d4e5-f6g7-8901-bcde-f21234567890',
        'SAMPLE_001',
        'adci',
        '2.1.0',
        '{"type": "neoadjuvant_therapy", "protocol": "FLOT", "surgery": "D2_gastrectomy"}',
        0.85,
        'high',
        0.4,
        'medium',
        '[{"evidence_id": "E001", "level": "1", "description": "FLOT superior to ECF in perioperative setting"}]',
        '[{"step": 1, "reasoning": "T2N1 staging indicates locally advanced disease"}]',
        150.5
    ),
    (
        'b2c3d4e5-f6g7-8901-bcde-f21234567890',
        'SAMPLE_002',
        'adci',
        '2.1.0',
        '{"type": "surgery_first", "protocol": "D2_gastrectomy", "adjuvant": "S1"}',
        0.78,
        'high',
        0.6,
        'high',
        '[{"evidence_id": "E002", "level": "1", "description": "S1 adjuvant therapy shows benefit in Asian populations"}]',
        '[{"step": 1, "reasoning": "T3N2 staging with good performance status"}]',
        175.2
    ),
    (
        'b2c3d4e5-f6g7-8901-bcde-f21234567890',
        'SAMPLE_003',
        'adci',
        '2.1.0',
        '{"type": "surgery_only", "protocol": "D1_plus_gastrectomy", "surveillance": "standard"}',
        0.92,
        'high',
        0.2,
        'low',
        '[{"evidence_id": "E003", "level": "1", "description": "Early stage disease, surgery curative"}]',
        '[{"step": 1, "reasoning": "T1N0 early stage, minimal risk"}]',
        95.8
    )
    ON CONFLICT (session_id, patient_id) DO NOTHING;
    """
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(sample_data_sql))
            logger.info("Successfully created sample cohort data")
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        raise
    finally:
        await engine.dispose()

async def main():
    """Main migration function"""
    logger.info("Starting cohort management database migration...")
    
    try:
        await create_cohort_tables()
        await create_sample_data()
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
