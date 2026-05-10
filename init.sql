CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

---------------------------------------------------------
-- 1. AUTH SERVICE (Nadal jako oddzielny schemat/mikroserwis)
---------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'KURSANT', 'INSTRUKTOR', 'ADMIN'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

---------------------------------------------------------
-- 2. STUDENT MODULE
---------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS student;

CREATE TABLE student.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE, -- Klucz obcy do Auth
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20)
);

CREATE TABLE student.courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student.profiles(id) ON DELETE CASCADE,
    category VARCHAR(10) NOT NULL, -- 'AM', 'B', 'C'
    required_hours INT DEFAULT 30,
    completed_hours INT DEFAULT 0,
    payment_status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

---------------------------------------------------------
-- 4. INSTRUCTOR MODULE
---------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS instructor;

CREATE TABLE instructor.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE, -- Klucz obcy do Auth
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    license_number VARCHAR(50),
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE instructor.specialties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instructor_profile_id UUID REFERENCES instructor.profiles(id) ON DELETE CASCADE,
    category VARCHAR(10) NOT NULL
);

---------------------------------------------------------
-- 3. CALENDAR MODULE (Teraz z silnymi relacjami)
---------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS calendar;

CREATE TABLE calendar.lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instructor_id UUID NOT NULL REFERENCES instructor.profiles(id), -- Relacja do profilu instruktora
    student_id UUID NOT NULL REFERENCES student.profiles(id),       -- Relacja do profilu kursanta
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'SCHEDULED', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

---------------------------------------------------------
-- 5. ADMIN MODULE
---------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS admin;

CREATE TABLE admin.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE, -- Klucz obcy do Auth
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    position VARCHAR(100), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);