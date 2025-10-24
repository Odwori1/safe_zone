-- Professional Directory Schema for Phase 3, Item 7
-- Following EXACT same patterns as enhanced_moderation_schema_fixed.sql

-- Professional Profiles Table (extends users table with professional-specific data)
CREATE TABLE IF NOT EXISTS professional_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Professional Information
    professional_title VARCHAR(100) NOT NULL,
    license_number VARCHAR(100),
    license_state VARCHAR(50),
    years_of_experience INTEGER,
    hourly_rate DECIMAL(10,2),
    bio TEXT,
    approach TEXT,
    specialties TEXT[],
    
    -- Contact Information (professional use only)
    professional_email VARCHAR(255),
    professional_phone VARCHAR(50),
    website_url VARCHAR(500),
    
    -- Verification Status
    verification_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'verified', 'rejected', 'suspended'
    verification_notes TEXT,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    
    -- Availability Settings
    accepts_new_clients BOOLEAN DEFAULT true,
    session_types TEXT[] DEFAULT '{"video", "audio", "chat"}', -- Available session types
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one profile per user
    UNIQUE(user_id)
);

-- Professional Verifications Table (credential documents)
CREATE TABLE IF NOT EXISTS professional_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    -- Verification Document Information
    document_type VARCHAR(50) NOT NULL, -- 'license', 'certification', 'diploma', 'insurance'
    document_name VARCHAR(255) NOT NULL,
    s3_key VARCHAR(500) NOT NULL, -- Secure S3 key for document storage
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- Verification Status
    verification_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Professional Availability Table (scheduling)
CREATE TABLE IF NOT EXISTS professional_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    -- Availability Slots
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Slot Configuration
    slot_duration_minutes INTEGER DEFAULT 60,
    buffer_minutes INTEGER DEFAULT 15,
    
    -- Recurrence
    is_recurring BOOLEAN DEFAULT true,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_until DATE,
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure no overlapping slots
    EXCLUDE USING gist (
        professional_id WITH =,
        day_of_week WITH =,
        tstzrange(
            (date '2000-01-01' + day_of_week) + start_time,
            (date '2000-01-01' + day_of_week) + end_time
        ) WITH &&
    )
);

-- Professional Services Table (session types & pricing)
CREATE TABLE IF NOT EXISTS professional_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    
    -- Service Details
    service_name VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL, -- 'individual', 'couples', 'group', 'workshop'
    modality VARCHAR(50) NOT NULL, -- 'video', 'audio', 'chat', 'in_person'
    duration_minutes INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Service Description
    description TEXT,
    preparation_instructions TEXT,
    
    -- Availability
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Appointments Table (booking system)
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Participants
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES professional_services(id),
    
    -- Appointment Details
    appointment_date DATE NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Session Information
    session_type VARCHAR(50) NOT NULL, -- 'video', 'audio', 'chat'
    session_link VARCHAR(500), -- For video/audio sessions
    meeting_id VARCHAR(100), -- Unique meeting identifier
    
    -- Status & Payment
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
    payment_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'refunded', 'failed'
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Client Notes
    client_concerns TEXT,
    emergency_contact TEXT,
    
    -- Professional Notes (only visible to professional)
    session_notes TEXT,
    follow_up_required BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure no overlapping appointments for professionals
    EXCLUDE USING gist (
        professional_id WITH =,
        tstzrange(start_time, end_time) WITH &&
    )
);

-- Professional Reviews Table
CREATE TABLE IF NOT EXISTS professional_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id UUID NOT NULL REFERENCES professional_profiles(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    
    -- Review Details
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(200),
    review_text TEXT,
    
    -- Review Categories
    communication_rating INTEGER CHECK (communication_rating BETWEEN 1 AND 5),
    professionalism_rating INTEGER CHECK (professionalism_rating BETWEEN 1 AND 5),
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    
    -- Moderation
    is_approved BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure one review per appointment
    UNIQUE(appointment_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_professional_profiles_user_id ON professional_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_professional_profiles_verification_status ON professional_profiles(verification_status);
CREATE INDEX IF NOT EXISTS idx_professional_profiles_is_active ON professional_profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_professional_verifications_professional_id ON professional_verifications(professional_id);
CREATE INDEX IF NOT EXISTS idx_professional_availability_professional_id ON professional_availability(professional_id);
CREATE INDEX IF NOT EXISTS idx_professional_services_professional_id ON professional_services(professional_id);
CREATE INDEX IF NOT EXISTS idx_appointments_professional_id ON appointments(professional_id);
CREATE INDEX IF NOT EXISTS idx_appointments_client_id ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_datetime ON appointments(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_professional_reviews_professional_id ON professional_reviews(professional_id);
CREATE INDEX IF NOT EXISTS idx_professional_reviews_client_id ON professional_reviews(client_id);

-- Enable RLS on all tables
ALTER TABLE professional_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE professional_verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE professional_availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE professional_services ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE professional_reviews ENABLE ROW LEVEL SECURITY;

-- RLS Policies - FOLLOWING EXACT SAME SECURITY PATTERN

-- Professional Profiles Policies
-- Users can see their own profile and public verified profiles
CREATE POLICY professional_profiles_select_policy ON professional_profiles
    FOR SELECT USING (
        user_id = current_setting('app.current_user_id')::UUID 
        OR (verification_status = 'verified' AND is_active = true)
    );

-- Users can only insert/update their own profile
CREATE POLICY professional_profiles_insert_policy ON professional_profiles
    FOR INSERT WITH CHECK (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY professional_profiles_update_policy ON professional_profiles
    FOR UPDATE USING (user_id = current_setting('app.current_user_id')::UUID);

-- Professional Verifications Policies
-- Users can see their own verifications
CREATE POLICY professional_verifications_select_policy ON professional_verifications
    FOR SELECT USING (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
        OR EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Users can only insert their own verifications
CREATE POLICY professional_verifications_insert_policy ON professional_verifications
    FOR INSERT WITH CHECK (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Only admins/moderators can update verification status
CREATE POLICY professional_verifications_update_policy ON professional_verifications
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Professional Availability Policies
-- Users can see availability of verified professionals
CREATE POLICY professional_availability_select_policy ON professional_availability
    FOR SELECT USING (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE verification_status = 'verified' AND is_active = true
        )
    );

-- Professionals can only manage their own availability
CREATE POLICY professional_availability_insert_policy ON professional_availability
    FOR INSERT WITH CHECK (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY professional_availability_update_policy ON professional_availability
    FOR UPDATE USING (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Professional Services Policies
-- Users can see services of verified professionals
CREATE POLICY professional_services_select_policy ON professional_services
    FOR SELECT USING (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE verification_status = 'verified' AND is_active = true
        )
    );

-- Professionals can only manage their own services
CREATE POLICY professional_services_insert_policy ON professional_services
    FOR INSERT WITH CHECK (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

CREATE POLICY professional_services_update_policy ON professional_services
    FOR UPDATE USING (
        professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Appointments Policies
-- Users can see their own appointments (as client or professional)
CREATE POLICY appointments_select_policy ON appointments
    FOR SELECT USING (
        client_id = current_setting('app.current_user_id')::UUID
        OR professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Clients can book appointments with verified professionals
CREATE POLICY appointments_insert_policy ON appointments
    FOR INSERT WITH CHECK (
        client_id = current_setting('app.current_user_id')::UUID
        AND professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE verification_status = 'verified' AND is_active = true
        )
    );

-- Participants can update their appointments with restrictions
CREATE POLICY appointments_update_policy ON appointments
    FOR UPDATE USING (
        client_id = current_setting('app.current_user_id')::UUID
        OR professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Professional Reviews Policies
-- Users can see approved reviews for verified professionals
CREATE POLICY professional_reviews_select_policy ON professional_reviews
    FOR SELECT USING (
        is_approved = true
        AND professional_id IN (
            SELECT id FROM professional_profiles 
            WHERE verification_status = 'verified' AND is_active = true
        )
    );

-- Clients can only review their own completed appointments
CREATE POLICY professional_reviews_insert_policy ON professional_reviews
    FOR INSERT WITH CHECK (
        client_id = current_setting('app.current_user_id')::UUID
        AND appointment_id IN (
            SELECT id FROM appointments 
            WHERE client_id = current_setting('app.current_user_id')::UUID
            AND status = 'completed'
        )
    );

-- Only admins/moderators can approve reviews
CREATE POLICY professional_reviews_update_policy ON professional_reviews
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::UUID 
            AND role IN ('admin', 'moderator')
        )
    );

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_professional_profiles_updated_at
    BEFORE UPDATE ON professional_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_professional_verifications_updated_at
    BEFORE UPDATE ON professional_verifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_professional_availability_updated_at
    BEFORE UPDATE ON professional_availability
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_professional_services_updated_at
    BEFORE UPDATE ON professional_services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_professional_reviews_updated_at
    BEFORE UPDATE ON professional_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (following existing pattern)
GRANT SELECT, INSERT, UPDATE ON professional_profiles TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON professional_verifications TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON professional_availability TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON professional_services TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON appointments TO safe_zone_app_user;
GRANT SELECT, INSERT, UPDATE ON professional_reviews TO safe_zone_app_user;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO safe_zone_app_user;

-- Create view for professional directory (public facing)
CREATE OR REPLACE VIEW professional_directory AS
SELECT 
    pp.id,
    pp.user_id,
    u.username,
    u.email,
    u.full_name,
    pp.professional_title,
    pp.license_number,
    pp.license_state,
    pp.years_of_experience,
    pp.hourly_rate,
    pp.bio,
    pp.approach,
    pp.specialties,
    pp.accepts_new_clients,
    pp.session_types,
    pp.verification_status,
    pp.is_active,
    AVG(pr.rating) as average_rating,
    COUNT(pr.id) as review_count,
    COUNT(a.id) as completed_sessions
FROM professional_profiles pp
JOIN users u ON pp.user_id = u.id
LEFT JOIN professional_reviews pr ON pp.id = pr.professional_id AND pr.is_approved = true
LEFT JOIN appointments a ON pp.id = a.professional_id AND a.status = 'completed'
WHERE pp.verification_status = 'verified' 
    AND pp.is_active = true
    AND u.is_active = true
GROUP BY pp.id, u.id, u.username, u.email, u.full_name;

GRANT SELECT ON professional_directory TO safe_zone_app_user;

