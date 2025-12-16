-- -----------------------------------------------------
-- 1. ROLLER & RÄTTIGHETER
-- ----------------------------------------------------
-- 1. CLEANUP (Drop old tables to start fresh)
DROP TABLE IF EXISTS participant_answer CASCADE;
DROP TABLE IF EXISTS session_participant CASCADE;
DROP TABLE IF EXISTS game_session CASCADE;
DROP TABLE IF EXISTS documents CASCADE;     -- Added this
DROP TABLE IF EXISTS support_case CASCADE;  -- Added this
DROP TABLE IF EXISTS course_content CASCADE;
DROP TABLE IF EXISTS course CASCADE;
DROP TABLE IF EXISTS story_content CASCADE;
DROP TABLE IF EXISTS story CASCADE;
DROP TABLE IF EXISTS quiz_answer CASCADE;
DROP TABLE IF EXISTS quiz_question CASCADE;
DROP TABLE IF EXISTS quiz CASCADE;
DROP TABLE IF EXISTS creation_method CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS subscription CASCADE;
DROP TABLE IF EXISTS user_company CASCADE;
DROP TABLE IF EXISTS user_teacher CASCADE;
DROP TABLE IF EXISTS user_student CASCADE;
DROP TABLE IF EXISTS user_role CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS subscription_features CASCADE;
DROP TABLE IF EXISTS features CASCADE;
DROP TABLE IF EXISTS subscription_plan CASCADE;
DROP TABLE IF EXISTS media_gif CASCADE;
DROP TABLE IF EXISTS media_image CASCADE;
DROP TABLE IF EXISTS media_video CASCADE;
DROP TABLE IF EXISTS media CASCADE;
DROP TABLE IF EXISTS role_permission CASCADE;
DROP TABLE IF EXISTS permission CASCADE;
DROP TABLE IF EXISTS role CASCADE;

-- ... Your CREATE TABLE code starts here ...

CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE permission (
    permission_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE role_permission (
    role_id INTEGER REFERENCES role(role_id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permission(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- -----------------------------------------------------
-- 2. MEDIA
-- -----------------------------------------------------

CREATE TABLE media (
    media_id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    -- Ersatt ENUM med VARCHAR + CHECK
    type VARCHAR(20) NOT NULL CHECK (type IN ('image', 'video', 'gif')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    filename VARCHAR(255)
);

CREATE TABLE media_video (
    media_id INTEGER PRIMARY KEY REFERENCES media(media_id) ON DELETE CASCADE,
    url TEXT,
    provider VARCHAR(50),
    duration INTEGER
);

CREATE TABLE media_image (
    media_id INTEGER PRIMARY KEY REFERENCES media(media_id) ON DELETE CASCADE,
    url TEXT,
    width INTEGER,
    height INTEGER
);

CREATE TABLE media_gif (
    media_id INTEGER PRIMARY KEY REFERENCES media(media_id) ON DELETE CASCADE,
    url TEXT,
    width INTEGER,
    height INTEGER
);

-- -----------------------------------------------------
-- 3. PRENUMERATIONER PLANER
-- -----------------------------------------------------

CREATE TABLE subscription_plan (
    plan_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price_per_month DECIMAL(10, 2),
    description TEXT
);

CREATE TABLE features (
    feature_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    value_type VARCHAR(50)
);

CREATE TABLE subscription_features (
    subscription_plan_id INTEGER REFERENCES subscription_plan(plan_id) ON DELETE CASCADE,
    feature_id INTEGER REFERENCES features(feature_id) ON DELETE CASCADE,
    value VARCHAR(255),
    PRIMARY KEY (subscription_plan_id, feature_id)
);

-- -----------------------------------------------------
-- 4. ANVÄNDARE (users)
-- -----------------------------------------------------

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    language VARCHAR(10) DEFAULT 'sv',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_subscription_id INTEGER 
);

CREATE TABLE user_role (
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES role(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE user_student (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    class_name VARCHAR(50),
    can_create_quiz BOOLEAN DEFAULT FALSE,
    teacher_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE user_teacher (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    subject VARCHAR(100),
    school_name VARCHAR(100),
    can_create_quiz BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_company (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    company_name VARCHAR(100),
    company_role VARCHAR(100),
    organization_number VARCHAR(50),
    department VARCHAR(100)
);

-- Subscription
CREATE TABLE subscription (
    subscription_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, 
    plan_id INTEGER NOT NULL REFERENCES subscription_plan(plan_id),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    -- Ersatt ENUM med VARCHAR + CHECK
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'expired'))
);

CREATE TABLE payment (
    payment_id SERIAL PRIMARY KEY,
    subscription_id INTEGER REFERENCES subscription(subscription_id),
    amount DECIMAL(10, 2),
    paid_at TIMESTAMP,
    payment_method VARCHAR(50)
);

-- -----------------------------------------------------
-- 5. INNEHÅLL (QUIZ & STORIES)
-- -----------------------------------------------------

CREATE TABLE creation_method (
    method_id SERIAL PRIMARY KEY,
    method_name VARCHAR(50),
    is_ai_assisted BOOLEAN
);

CREATE TABLE quiz (
    quiz_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    creation_method_id INTEGER REFERENCES creation_method(method_id),
    creator_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    media_id INTEGER REFERENCES media(media_id)
);

CREATE TABLE quiz_question (
    question_id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    question_text TEXT,
    -- Ersatt ENUM med VARCHAR + CHECK
    question_type VARCHAR(20) CHECK (question_type IN ('multiple_choice', 'boolean', 'slider')),
    time_limit INTEGER,
    points INTEGER,
    sort_order INTEGER,
    media_id INTEGER REFERENCES media(media_id)
);

CREATE TABLE quiz_answer (
    answer_id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES quiz_question(question_id) ON DELETE CASCADE,
    answer_text TEXT,
    is_correct BOOLEAN,
    sort_order INTEGER,
    media_id INTEGER REFERENCES media(media_id)
);

CREATE TABLE story (
    story_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    created_at TIMESTAMP,
    creator_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE 
);

CREATE TABLE story_content (
    block_id SERIAL PRIMARY KEY,
    story_id INTEGER REFERENCES story(story_id) ON DELETE CASCADE,
    block_order INTEGER,
    block_type VARCHAR(50),
    content_text TEXT,
    media_id INTEGER REFERENCES media(media_id)
);

CREATE TABLE course (
    course_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    creator_id INTEGER REFERENCES users(user_id)
);

CREATE TABLE course_content (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES course(course_id) ON DELETE CASCADE,
    content_order INTEGER,
    -- Ersatt ENUM med VARCHAR + CHECK
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('story', 'quiz', 'media')),
    content_id INTEGER NOT NULL 
);

-- -----------------------------------------------------
-- 6. SPELSESSIONER
-- -----------------------------------------------------

CREATE TABLE game_session (
    session_id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    host_id INTEGER REFERENCES users(user_id),
    access_code VARCHAR(10),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    current_question_index INTEGER DEFAULT 0
);

CREATE TABLE session_participant (
    participant_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES game_session(session_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    nickname VARCHAR(50),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER DEFAULT 0
);

CREATE TABLE participant_answer (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES session_participant(participant_id),
    question_id INTEGER REFERENCES quiz_question(question_id),
    chosen_answer_id INTEGER REFERENCES quiz_answer(answer_id),
    is_correct BOOLEAN,
    points_awarded INTEGER,
    answered_at TIMESTAMP
);

-- -----------------------------------------------------
-- 7. ÖVRIGT
-- -----------------------------------------------------

CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    file_url VARCHAR(255),
    course_id INTEGER REFERENCES course(course_id)
);

CREATE TABLE support_case (
    case_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    subject VARCHAR(255),
    status VARCHAR(50),
    created_date TIMESTAMP
);

-- Roller
INSERT INTO role (name, description) VALUES 
('student', 'Kan delta i quiz och se kurser'),
('teacher', 'Kan skapa innehåll och bjuda in studenter'),
('company_admin', 'Kan hantera företagets team och innehåll');

-- Skapandemetoder (för Quiz)
INSERT INTO creation_method (method_name, is_ai_assisted) VALUES 
('manual', FALSE),
('ai_generated', TRUE);

-- Prenumerationsplaner
INSERT INTO subscription_plan (name, price_per_month, description) VALUES 
('Free', 0.00, 'Grundläggande funktioner'),
('Pro', 99.00, 'För lärare och skapare'),
('Enterprise', 999.00, 'För företag');

-- -----------------------------------------------------
-- 2. MEDIA (Bilder och Videos)
-- -----------------------------------------------------

-- Infoga i huvudtabellen först
INSERT INTO media (title, type, filename) VALUES 
('Profilbild Anna', 'image', 'avatar_anna.jpg'),
('Quiz Omslag Natur', 'image', 'nature_cover.jpg'),
('Intro Video', 'video', 'intro_course.mp4');

-- Infoga metadata i sub-tabellerna
INSERT INTO media_image (media_id, url, width, height) VALUES 
(1, 'https://example.com/avatar_anna.jpg', 500, 500),
(2, 'https://example.com/nature_cover.jpg', 1920, 1080);

INSERT INTO media_video (media_id, url, provider, duration) VALUES 
(3, 'https://vimeo.com/123456', 'vimeo', 120);

-- -----------------------------------------------------
-- 3. ANVÄNDARE & PRENUMERATIONER
-- -----------------------------------------------------

-- Skapa Användare (Lösenord är 'password123' hashade - detta är bara exempelsträngar)
INSERT INTO users (username, email, password_hash, is_verified, is_active) VALUES 
('anna_teacher', 'anna@skola.se', '$2b$10$DUMMYHASH1234567890', TRUE, TRUE), -- ID 1
('kalle_student', 'kalle@student.se', '$2b$10$DUMMYHASH1234567890', TRUE, TRUE), -- ID 2
('boss_tech', 'ceo@techcorp.com', '$2b$10$DUMMYHASH1234567890', TRUE, TRUE);    -- ID 3

-- Koppla användare till specifika roll-tabeller
INSERT INTO user_teacher (user_id, subject, school_name) VALUES 
(1, 'Biologi', 'Centralskolan');

INSERT INTO user_student (user_id, class_name, teacher_id) VALUES 
(2, '9B', 1);

INSERT INTO user_company (user_id, company_name, organization_number) VALUES 
(3, 'TechCorp AB', '556000-0000');

-- Skapa Prenumerationer
INSERT INTO subscription (user_id, plan_id, start_date, status) VALUES 
(1, 2, NOW(), 'active'), -- Anna har Pro
(2, 1, NOW(), 'active'), -- Kalle har Free
(3, 3, NOW(), 'active'); -- Företaget har Enterprise

-- UPPDATERA users-tabellen med den nya subscription_id (Cirkelberoendet)
UPDATE users SET current_subscription_id = 1 WHERE user_id = 1;
UPDATE users SET current_subscription_id = 2 WHERE user_id = 2;
UPDATE users SET current_subscription_id = 3 WHERE user_id = 3;

-- -----------------------------------------------------
-- 4. INNEHÅLL (Quiz, Frågor, Svar)
-- -----------------------------------------------------

-- Skapa ett Quiz (Skapat av Anna)
INSERT INTO quiz (name, creation_method_id, creator_id, media_id) VALUES 
('Naturkunskap Grund', 1, 1, 2); -- ID 1

-- Fråga 1: Multiple Choice
INSERT INTO quiz_question (quiz_id, question_text, question_type, time_limit, points, sort_order) VALUES 
(1, 'Vilket djur är störst?', 'multiple_choice', 30, 1000, 1); -- ID 1

    -- Svar till Fråga 1
    INSERT INTO quiz_answer (question_id, answer_text, is_correct, sort_order) VALUES 
    (1, 'Elefant', FALSE, 1),
    (1, 'Blåval', TRUE, 2),
    (1, 'Myra', FALSE, 3),
    (1, 'Giraff', FALSE, 4);

-- Fråga 2: Boolean
INSERT INTO quiz_question (quiz_id, question_text, question_type, time_limit, points, sort_order) VALUES 
(1, 'Är jorden platt?', 'boolean', 10, 500, 2); -- ID 2

    -- Svar till Fråga 2
    INSERT INTO quiz_answer (question_id, answer_text, is_correct, sort_order) VALUES 
    (2, 'Sant', FALSE, 1),
    (2, 'Falskt', TRUE, 2);

-- -----------------------------------------------------
-- 5. STORIES & KURSER
-- -----------------------------------------------------

-- Skapa en Story
INSERT INTO story (name, created_at, creator_id) VALUES 
('Vattnets Kretslopp', NOW(), 1); -- ID 1

INSERT INTO story_content (story_id, block_order, block_type, content_text) VALUES 
(1, 1, 'text', 'Vattnet dunstar från havet...'),
(1, 2, 'text', '...och bildar moln.');

-- Skapa en Kurs som samlar allt
INSERT INTO course (name, description, creator_id) VALUES 
('Biologi A', 'En introkurs till naturen', 1); -- ID 1

-- Koppla Story och Quiz till Kursen
INSERT INTO course_content (course_id, content_order, content_type, content_id) VALUES 
(1, 1, 'story', 1), -- Först kommer storyn (ID 1)
(1, 2, 'quiz', 1);  -- Sen kommer quizet (ID 1)

-- -----------------------------------------------------
-- 6. SPELSESSION (Gameplay)
-- -----------------------------------------------------

-- Anna startar en session av sitt quiz
INSERT INTO game_session (quiz_id, host_id, access_code, started_at) VALUES 
(1, 1, 'GAME123', NOW()); -- Session ID 1

-- Kalle går med i spelet
INSERT INTO session_participant (session_id, user_id, nickname, joined_at) VALUES 
(1, 2, 'KalleKula', NOW()); -- Participant ID 1

-- Kalle svarar på första frågan (Blåval = Rätt)
-- Vi måste veta ID på svaret "Blåval". I detta script är det svar nr 2.
INSERT INTO participant_answer (participant_id, question_id, chosen_answer_id, is_correct, points_awarded, answered_at) VALUES 
(1, 1, 2, TRUE, 950, NOW());