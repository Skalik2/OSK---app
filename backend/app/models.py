from typing import Optional
import datetime
import uuid

from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class AuUsers(Base):
    __tablename__ = 'au_users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='au_users_pkey'),
        UniqueConstraint('email', name='au_users_email_key'),
        {'schema': 'auth'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    ad_profiles: Mapped['AdProfiles'] = relationship('AdProfiles', uselist=False, back_populates='user')
    in_profiles: Mapped['InProfiles'] = relationship('InProfiles', uselist=False, back_populates='user')
    st_profiles: Mapped['StProfiles'] = relationship('StProfiles', uselist=False, back_populates='user')


class AdProfiles(Base):
    __tablename__ = 'ad_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['auth.au_users.id'], ondelete='CASCADE', name='ad_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='ad_profiles_pkey'),
        UniqueConstraint('user_id', name='ad_profiles_user_id_key'),
        {'schema': 'admin'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['AuUsers'] = relationship('AuUsers', back_populates='ad_profiles')


class InProfiles(Base):
    __tablename__ = 'in_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['auth.au_users.id'], ondelete='CASCADE', name='in_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='in_profiles_pkey'),
        UniqueConstraint('user_id', name='in_profiles_user_id_key'),
        {'schema': 'instructor'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    license_number: Mapped[Optional[str]] = mapped_column(String(50))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['AuUsers'] = relationship('AuUsers', back_populates='in_profiles')
    ca_lessons: Mapped[list['CaLessons']] = relationship('CaLessons', back_populates='instructor')
    in_specialties: Mapped[list['InSpecialties']] = relationship('InSpecialties', back_populates='instructor_profile')


class StProfiles(Base):
    __tablename__ = 'st_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['auth.au_users.id'], ondelete='CASCADE', name='st_profiles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='st_profiles_pkey'),
        UniqueConstraint('user_id', name='st_profiles_user_id_key'),
        {'schema': 'student'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    user: Mapped['AuUsers'] = relationship('AuUsers', back_populates='st_profiles')
    ca_lessons: Mapped[list['CaLessons']] = relationship('CaLessons', back_populates='student')
    st_courses: Mapped[list['StCourses']] = relationship('StCourses', back_populates='student_profile')


class CaLessons(Base):
    __tablename__ = 'ca_lessons'
    __table_args__ = (
        ForeignKeyConstraint(['instructor_id'], ['instructor.in_profiles.id'], name='ca_lessons_instructor_id_fkey'),
        ForeignKeyConstraint(['student_id'], ['student.st_profiles.id'], name='ca_lessons_student_id_fkey'),
        PrimaryKeyConstraint('id', name='ca_lessons_pkey'),
        {'schema': 'calendar'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    instructor_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'SCHEDULED'::character varying"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    instructor: Mapped['InProfiles'] = relationship('InProfiles', back_populates='ca_lessons')
    student: Mapped['StProfiles'] = relationship('StProfiles', back_populates='ca_lessons')


class InSpecialties(Base):
    __tablename__ = 'in_specialties'
    __table_args__ = (
        ForeignKeyConstraint(['instructor_profile_id'], ['instructor.in_profiles.id'], ondelete='CASCADE', name='in_specialties_instructor_profile_id_fkey'),
        PrimaryKeyConstraint('id', name='in_specialties_pkey'),
        {'schema': 'instructor'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    category: Mapped[str] = mapped_column(String(10), nullable=False)
    instructor_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    instructor_profile: Mapped[Optional['InProfiles']] = relationship('InProfiles', back_populates='in_specialties')


class StCourses(Base):
    __tablename__ = 'st_courses'
    __table_args__ = (
        ForeignKeyConstraint(['student_profile_id'], ['student.st_profiles.id'], ondelete='CASCADE', name='st_courses_student_profile_id_fkey'),
        PrimaryKeyConstraint('id', name='st_courses_pkey'),
        {'schema': 'student'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    student_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    category: Mapped[str] = mapped_column(String(10), nullable=False)
    required_hours: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('30'))
    completed_hours: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    payment_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'PENDING'::character varying"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    student_profile: Mapped['StProfiles'] = relationship('StProfiles', back_populates='st_courses')
