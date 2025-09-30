-- BlogCraft Pro SaaS Database Schema
-- Database: blogcraft_pro
-- Version: 1.0.0
-- Created: 2025

-- =============================================
-- 1. USERS TABLE
-- =============================================
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    profile_image VARCHAR(500),
    role ENUM('user', 'admin', 'super_admin') DEFAULT 'user',
    status ENUM('active', 'inactive', 'suspended', 'deleted') DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires DATETIME,
    last_login_at DATETIME,
    login_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 2. SUBSCRIPTION PLANS TABLE
-- =============================================
CREATE TABLE subscription_plans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2) NOT NULL,
    
    -- Plan Limits
    blog_posts_limit INT DEFAULT NULL, -- NULL means unlimited
    sns_conversions_limit INT DEFAULT NULL,
    api_calls_limit INT DEFAULT NULL,
    team_members_limit INT DEFAULT 1,
    storage_limit_gb INT DEFAULT 10,
    
    -- Features
    features JSON, -- Store features as JSON array
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default plans
INSERT INTO subscription_plans (name, slug, description, price_monthly, price_yearly, 
    blog_posts_limit, sns_conversions_limit, api_calls_limit, team_members_limit, features) 
VALUES 
    ('Free', 'free', '개인 블로거를 위한 무료 플랜', 0, 0, 
     5, 0, 0, 1, 
     '["기본 SEO 최적화", "네이버 블로그 지원", "이메일 지원"]'),
    
    ('Professional', 'professional', '전문 콘텐츠 크리에이터용', 49000, 470400, 
     100, 500, 50000, 5, 
     '["고급 SEO 최적화", "모든 플랫폼 지원", "SNS 변환 무제한", "우선 지원", "API 접근"]'),
    
    ('Enterprise', 'enterprise', '대규모 팀과 기업용', 149000, 1430400, 
     NULL, NULL, NULL, NULL, 
     '["엔터프라이즈 SEO", "팀 협업 기능", "무제한 사용", "전담 계정 관리자", "커스텀 API"]');

-- =============================================
-- 3. USER SUBSCRIPTIONS TABLE
-- =============================================
CREATE TABLE user_subscriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    plan_id INT NOT NULL,
    status ENUM('active', 'canceled', 'expired', 'suspended') DEFAULT 'active',
    billing_cycle ENUM('monthly', 'yearly') DEFAULT 'monthly',
    
    -- Subscription dates
    trial_ends_at DATETIME,
    starts_at DATETIME NOT NULL,
    ends_at DATETIME,
    canceled_at DATETIME,
    
    -- Payment info
    payment_method VARCHAR(50),
    last_payment_date DATETIME,
    next_payment_date DATETIME,
    payment_amount DECIMAL(10,2),
    
    -- Usage tracking reset dates
    usage_reset_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES subscription_plans(id),
    INDEX idx_user_status (user_id, status),
    INDEX idx_ends_at (ends_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 4. USAGE TRACKING TABLE
-- =============================================
CREATE TABLE usage_tracking (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    subscription_id BIGINT NOT NULL,
    
    -- Monthly usage counters
    blog_posts_used INT DEFAULT 0,
    sns_conversions_used INT DEFAULT 0,
    api_calls_used INT DEFAULT 0,
    storage_used_mb INT DEFAULT 0,
    
    -- Period
    usage_month DATE NOT NULL, -- First day of the month
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_month (user_id, usage_month),
    INDEX idx_usage_month (usage_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 5. BLOG POSTS TABLE
-- =============================================
CREATE TABLE blog_posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    
    -- Content
    title VARCHAR(500) NOT NULL,
    content LONGTEXT NOT NULL,
    excerpt TEXT,
    
    -- Platform & SEO
    platform ENUM('naver', 'tistory', 'wordpress') NOT NULL,
    seo_score INT DEFAULT 0,
    keywords VARCHAR(500),
    meta_description TEXT,
    
    -- AI Model used
    ai_model VARCHAR(50),
    ai_tokens_used INT DEFAULT 0,
    
    -- Stats
    word_count INT DEFAULT 0,
    char_count INT DEFAULT 0,
    reading_time INT DEFAULT 0, -- in minutes
    
    -- Status
    status ENUM('draft', 'published', 'archived', 'deleted') DEFAULT 'draft',
    published_at DATETIME,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_platform (platform),
    INDEX idx_created_at (created_at),
    FULLTEXT idx_fulltext (title, content, keywords)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 6. SNS CONVERSIONS TABLE
-- =============================================
CREATE TABLE sns_conversions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    blog_post_id BIGINT,
    
    -- Platform
    platform ENUM('instagram', 'threads', 'youtube', 'twitter', 'linkedin') NOT NULL,
    
    -- Content
    content LONGTEXT NOT NULL,
    hashtags VARCHAR(500),
    
    -- Stats
    slides_count INT DEFAULT 0, -- For Instagram
    threads_count INT DEFAULT 0, -- For Threads
    video_duration INT DEFAULT 0, -- For YouTube (seconds)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (blog_post_id) REFERENCES blog_posts(id) ON DELETE SET NULL,
    INDEX idx_user_platform (user_id, platform),
    INDEX idx_blog_post (blog_post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 7. API KEYS TABLE
-- =============================================
CREATE TABLE api_keys (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    
    -- API Key info
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    description TEXT,
    
    -- Permissions
    permissions JSON, -- Store permissions as JSON
    rate_limit INT DEFAULT 1000, -- requests per hour
    
    -- Usage
    last_used_at DATETIME,
    usage_count BIGINT DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at DATETIME,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_key_hash (key_hash),
    INDEX idx_user_active (user_id, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 8. PAYMENT HISTORY TABLE
-- =============================================
CREATE TABLE payment_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    subscription_id BIGINT,
    
    -- Payment details
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KRW',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    
    -- Status
    status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    
    -- Billing info
    billing_name VARCHAR(255),
    billing_email VARCHAR(255),
    billing_address TEXT,
    
    -- Invoice
    invoice_number VARCHAR(100) UNIQUE,
    invoice_url VARCHAR(500),
    
    -- Dates
    paid_at DATETIME,
    failed_at DATETIME,
    refunded_at DATETIME,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES user_subscriptions(id) ON DELETE SET NULL,
    INDEX idx_user_status (user_id, status),
    INDEX idx_transaction (transaction_id),
    INDEX idx_invoice (invoice_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 9. TEAM MEMBERS TABLE
-- =============================================
CREATE TABLE team_members (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    owner_user_id BIGINT NOT NULL, -- Team owner
    member_user_id BIGINT NOT NULL, -- Team member
    
    -- Role & Permissions
    role ENUM('admin', 'editor', 'viewer') DEFAULT 'editor',
    permissions JSON,
    
    -- Status
    status ENUM('pending', 'active', 'suspended', 'removed') DEFAULT 'pending',
    invited_at DATETIME,
    joined_at DATETIME,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (member_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_team_member (owner_user_id, member_user_id),
    INDEX idx_member_status (member_user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 10. ACTIVITY LOGS TABLE
-- =============================================
CREATE TABLE activity_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    
    -- Activity info
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- 'blog_post', 'sns_conversion', etc.
    entity_id BIGINT,
    
    -- Details
    details JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_action (user_id, action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 11. NOTIFICATIONS TABLE
-- =============================================
CREATE TABLE notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    
    -- Notification content
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    action_url VARCHAR(500),
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at DATETIME,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_unread (user_id, is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 12. ADMIN SETTINGS TABLE
-- =============================================
CREATE TABLE admin_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50), -- 'string', 'number', 'json', 'boolean'
    description TEXT,
    updated_by BIGINT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_setting_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default admin settings
INSERT INTO admin_settings (setting_key, setting_value, setting_type, description) VALUES
    ('maintenance_mode', 'false', 'boolean', '유지보수 모드 활성화'),
    ('free_trial_days', '7', 'number', '무료 체험 기간 (일)'),
    ('max_api_rate_limit', '10000', 'number', '최대 API 요청 제한 (시간당)'),
    ('signup_enabled', 'true', 'boolean', '신규 회원가입 허용'),
    ('payment_gateway', 'stripe', 'string', '결제 게이트웨이 (stripe, paypal, toss)');

-- =============================================
-- 13. ANALYTICS TABLE
-- =============================================
CREATE TABLE analytics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    
    -- User metrics
    total_users INT DEFAULT 0,
    new_users INT DEFAULT 0,
    active_users INT DEFAULT 0,
    
    -- Content metrics
    blog_posts_created INT DEFAULT 0,
    sns_conversions_created INT DEFAULT 0,
    total_api_calls INT DEFAULT 0,
    
    -- Revenue metrics
    revenue DECIMAL(12,2) DEFAULT 0,
    new_subscriptions INT DEFAULT 0,
    canceled_subscriptions INT DEFAULT 0,
    
    -- Platform breakdown (JSON)
    platform_stats JSON,
    ai_model_stats JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_date (date),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- VIEWS
-- =============================================

-- Active Subscriptions View
CREATE VIEW active_subscriptions AS
SELECT 
    u.id as user_id,
    u.email,
    u.username,
    sp.name as plan_name,
    us.billing_cycle,
    us.starts_at,
    us.ends_at,
    ut.blog_posts_used,
    sp.blog_posts_limit,
    ut.sns_conversions_used,
    sp.sns_conversions_limit,
    ut.api_calls_used,
    sp.api_calls_limit
FROM users u
JOIN user_subscriptions us ON u.id = us.user_id
JOIN subscription_plans sp ON us.plan_id = sp.id
LEFT JOIN usage_tracking ut ON u.id = ut.user_id 
    AND ut.usage_month = DATE_FORMAT(NOW(), '%Y-%m-01')
WHERE us.status = 'active';

-- Revenue Summary View
CREATE VIEW revenue_summary AS
SELECT 
    DATE_FORMAT(paid_at, '%Y-%m') as month,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction,
    COUNT(DISTINCT user_id) as unique_customers
FROM payment_history
WHERE status = 'completed'
GROUP BY DATE_FORMAT(paid_at, '%Y-%m');

-- =============================================
-- STORED PROCEDURES
-- =============================================

DELIMITER //

-- Update Usage Counter
CREATE PROCEDURE UpdateUsageCounter(
    IN p_user_id BIGINT,
    IN p_counter_type VARCHAR(50),
    IN p_increment INT
)
BEGIN
    DECLARE v_subscription_id BIGINT;
    DECLARE v_current_month DATE;
    
    SET v_current_month = DATE_FORMAT(NOW(), '%Y-%m-01');
    
    SELECT id INTO v_subscription_id
    FROM user_subscriptions
    WHERE user_id = p_user_id AND status = 'active'
    LIMIT 1;
    
    IF v_subscription_id IS NOT NULL THEN
        INSERT INTO usage_tracking (user_id, subscription_id, usage_month)
        VALUES (p_user_id, v_subscription_id, v_current_month)
        ON DUPLICATE KEY UPDATE updated_at = NOW();
        
        CASE p_counter_type
            WHEN 'blog_posts' THEN
                UPDATE usage_tracking 
                SET blog_posts_used = blog_posts_used + p_increment
                WHERE user_id = p_user_id AND usage_month = v_current_month;
            WHEN 'sns_conversions' THEN
                UPDATE usage_tracking 
                SET sns_conversions_used = sns_conversions_used + p_increment
                WHERE user_id = p_user_id AND usage_month = v_current_month;
            WHEN 'api_calls' THEN
                UPDATE usage_tracking 
                SET api_calls_used = api_calls_used + p_increment
                WHERE user_id = p_user_id AND usage_month = v_current_month;
        END CASE;
    END IF;
END //

DELIMITER ;

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================
CREATE INDEX idx_blogs_created_month ON blog_posts(user_id, created_at);
CREATE INDEX idx_sns_created_month ON sns_conversions(user_id, created_at);
CREATE INDEX idx_payments_month ON payment_history(user_id, paid_at);
CREATE INDEX idx_usage_user_month ON usage_tracking(user_id, usage_month);

-- =============================================
-- TRIGGERS
-- =============================================

DELIMITER //

-- Auto-increment usage when blog post is created
CREATE TRIGGER after_blog_post_insert
AFTER INSERT ON blog_posts
FOR EACH ROW
BEGIN
    CALL UpdateUsageCounter(NEW.user_id, 'blog_posts', 1);
END //

-- Auto-increment usage when SNS conversion is created
CREATE TRIGGER after_sns_conversion_insert
AFTER INSERT ON sns_conversions
FOR EACH ROW
BEGIN
    CALL UpdateUsageCounter(NEW.user_id, 'sns_conversions', 1);
END //

DELIMITER ;