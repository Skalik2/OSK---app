-- Czyszczenie starych danych (opcjonalne, zachowaj kolejność ze względu na klucze obce)
TRUNCATE TABLE calendar.ca_lessons CASCADE;
TRUNCATE TABLE instructor.in_specialties CASCADE;
TRUNCATE TABLE instructor.in_profiles CASCADE;
TRUNCATE TABLE student.st_courses CASCADE;
TRUNCATE TABLE student.st_profiles CASCADE;
TRUNCATE TABLE admin.ad_profiles CASCADE;
TRUNCATE TABLE auth.au_users CASCADE;

-------------------------------------------------------------------------------
-- 1. DODAWANIE UŻYTKOWNIKÓW (auth.au_users) I ICH PROFILI
-------------------------------------------------------------------------------

-- ADMIN (Hasło: password123)
WITH inserted_admin AS (
    INSERT INTO auth.au_users (email, password_hash, role)
    VALUES ('admin@szkolajazdy.pl', '$argon2id$v=19$m=65536,t=3,p=4$4zyHEAKA0FrrHcP4H0OodQ$iCYk3OaSx8bcV2d9Kg5LU7e0HVOoG/8OjRYJu42QWj0', 'admin')
    RETURNING id
)
INSERT INTO admin.ad_profiles (user_id, first_name, last_name, position)
SELECT id, 'Janusz', 'Kowalski', 'Dyrektor Zarządzający' FROM inserted_admin;


-- INSTRUKTORZY (Hasło: password123)
WITH ins1 AS (
    INSERT INTO auth.au_users (email, password_hash, role)
    VALUES ('tomasz.nowak@szkolajazdy.pl', '$argon2id$v=19$m=65536,t=3,p=4$4zyHEAKA0FrrHcP4H0OodQ$iCYk3OaSx8bcV2d9Kg5LU7e0HVOoG/8OjRYJu42QWj0', 'instructor')
    RETURNING id
), prof1 AS (
    INSERT INTO instructor.in_profiles (user_id, first_name, last_name, phone, license_number, bio)
    SELECT id, 'Tomasz', 'Nowak', '+48123456789', 'INSTR-B-9982', 'Instruktor kat. B z 10-letnim stażem. Cierpliwy i wymagający.' FROM ins1
    RETURNING id
)
INSERT INTO instructor.in_specialties (instructor_profile_id, category)
SELECT id, 'B' FROM prof1;

WITH ins2 AS (
    INSERT INTO auth.au_users (email, password_hash, role)
    VALUES ('anna.wisniewska@szkolajazdy.pl', '$argon2id$v=19$m=65536,t=3,p=4$4zyHEAKA0FrrHcP4H0OodQ$iCYk3OaSx8bcV2d9Kg5LU7e0HVOoG/8OjRYJu42QWj0', 'instructor')
    RETURNING id
), prof2 AS (
    INSERT INTO instructor.in_profiles (user_id, first_name, last_name, phone, license_number, bio)
    SELECT id, 'Anna', 'Wiśniewska', '+48987654321', 'INSTR-AM-5541', 'Pasjonatka motocykli. Szkoli przyszłych mistrzów dwóch kółek na kat. AM.' FROM ins2
    RETURNING id
)
INSERT INTO instructor.in_specialties (instructor_profile_id, category)
SELECT id, 'AM' FROM prof2;


-- KURSANCI (Hasło: password123)
WITH stu1 AS (
    INSERT INTO auth.au_users (email, password_hash, role)
    VALUES ('mateusz.zielinski@poczta.pl', '$argon2id$v=19$m=65536,t=3,p=4$4zyHEAKA0FrrHcP4H0OodQ$iCYk3OaSx8bcV2d9Kg5LU7e0HVOoG/8OjRYJu42QWj0', 'student')
    RETURNING id
), prof_stu1 AS (
    INSERT INTO student.st_profiles (user_id, first_name, last_name, phone)
    SELECT id, 'Mateusz', 'Zieliński', '+48601602603' FROM stu1
    RETURNING id
)
INSERT INTO student.st_courses (student_profile_id, category, required_hours, completed_hours, payment_status)
SELECT id, 'B', 30, 12, 'PAID' FROM prof_stu1;

WITH stu2 AS (
    INSERT INTO auth.au_users (email, password_hash, role)
    VALUES ('katarzyna.wojcik@gmail.com', '$argon2id$v=19$m=65536,t=3,p=4$4zyHEAKA0FrrHcP4H0OodQ$iCYk3OaSx8bcV2d9Kg5LU7e0HVOoG/8OjRYJu42QWj0', 'student')
    RETURNING id
), prof_stu2 AS (
    INSERT INTO student.st_profiles (user_id, first_name, last_name, phone)
    SELECT id, 'Katarzyna', 'Wójcik', '+48505506507' FROM stu2
    RETURNING id
)
INSERT INTO student.st_courses (student_profile_id, category, required_hours, completed_hours, payment_status)
SELECT id, 'AM', 20, 2, 'PENDING' FROM prof_stu2;


-------------------------------------------------------------------------------
-- 2. DODAWANIE LEKCJI DO KALENDARZA (calendar.ca_lessons)
-------------------------------------------------------------------------------

INSERT INTO calendar.ca_lessons (instructor_id, student_id, start_time, end_time, status)
VALUES
(
    (SELECT id FROM instructor.in_profiles WHERE last_name = 'Nowak' LIMIT 1),
    (SELECT id FROM student.st_profiles WHERE last_name = 'Zieliński' LIMIT 1),
    CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '10 hours', -- Jutro o 10:00
    CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '12 hours', -- Jutro do 12:00
    'SCHEDULED'
),
(
    (SELECT id FROM instructor.in_profiles WHERE last_name = 'Nowak' LIMIT 1),
    (SELECT id FROM student.st_profiles WHERE last_name = 'Zieliński' LIMIT 1),
    CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '14 hours', -- 2 dni temu o 14:00
    CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '16 hours',
    'COMPLETED'
),
(
    (SELECT id FROM instructor.in_profiles WHERE last_name = 'Wiśniewska' LIMIT 1),
    (SELECT id FROM student.st_profiles WHERE last_name = 'Wójcik' LIMIT 1),
    CURRENT_TIMESTAMP + INTERVAL '2 days' + INTERVAL '08 hours', -- Za dwa dni o 08:00
    CURRENT_TIMESTAMP + INTERVAL '2 days' + INTERVAL '10 hours',
    'SCHEDULED'
);