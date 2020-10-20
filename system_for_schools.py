#!/usr/bin/env python
#database system for schools
#-*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Sequence, ForeignKey, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import exists

#create Engine object
engine = create_engine('sqlite:///:memory:')
#create home class
Base = declarative_base()

#object association table
instructor_course = Table('instructor_course', Base.metadata, Column('instructor_id', ForeignKey('instructor.id'),\
						  primary_key = True), Column('course_id', ForeignKey('course.id'), primary_key = True))
#top class (extra addition)
class University(Base):
	__tablename__ = 'university'
	id = Column(Integer, Sequence('university_id_seq'), primary_key = True)
	name = Column(String)

	#one-to-many relationship between "University" and "Course" classes
	courses = relationship('Course', order_by = 'Course.name', back_populates = 'university')

	def __repr__(self):
		return "{}".format(self.name)

class Course(Base):
	__tablename__ = 'course'
	id = Column(Integer, Sequence('course_id_seq'), primary_key = True)
	name = Column(String)
	#parent table reference
	university_id = Column(Integer, ForeignKey('university.id'))
	
	#one-to-many relationship between "University" and "Course" classes
	university = relationship('University', back_populates = 'courses')
	#one-to-many relationship between "Course" and "Student" classes
	students = relationship('Student', order_by = 'Student.lastname', back_populates = 'course')
	#many-to-many relationship between "Course" and "Instructor" classes
	instructors = relationship('Instructor', secondary = instructor_course, back_populates = 'courses')
	#one-to-many relationship between "Course" and "Schedule" classes
	schedules = relationship('Schedule', order_by = 'Schedule.id', back_populates = 'course')

	def __repr__(self):
		return '{}'.format(self.name)

class Student(Base):
	__tablename__ = 'student'
	id = Column(Integer, Sequence('student_id_seq'), primary_key = True)
	firstname = Column(String)
	lastname = Column(String)
	#parent table reference
	course_id = Column(Integer, ForeignKey('course.id'))
	
	#one-to-many relationship between "Course" and "Student" classes
	course = relationship('Course', back_populates = 'students') # Create a relation between Course and University

	def __repr__(self):
		return '{} {}'.format(self.lastname, self.firstname)

class Instructor(Base):
	__tablename__ = 'instructor'
	id = Column(Integer, Sequence('instructor_id_seq'), primary_key = True)
	firstname = Column(String)
	lastname = Column(String)

	#many-to-many relationship between "Instructor" and "Course" classes
	courses = relationship('Course', secondary = instructor_course, back_populates = 'instructors')
	#one-to-many relationship between "Instructor" and "Schedule" classes
	schedules = relationship('Schedule', order_by = 'Schedule.id', back_populates = 'instructor')

	def __repr__(self):
		return '{} {}'.format(self.lastname, self.firstname)

class Schedule(Base):
	__tablename__ = 'schedule'
	id = Column(Integer, Sequence('schedule_id_seq'), primary_key = True)
	days = ['Monday', 'Thursday', 'Wednesday', 'Tuesday', 'Friday', 'Saturday']
	day = Column(String)
	start_time = Column(String)
	ending_time = Column(String)
	#parent table reference
	instructor_id = Column(Integer, ForeignKey('instructor.id'))
	#parent table reference
	course_id = Column(Integer, ForeignKey('course.id'))

	#one-to-many relationship between "Instructor" and "Schedule" classes
	instructor = relationship('Instructor', back_populates = 'schedules')
	#one-to-many relationship between "Course" and "Schedule" classes
	course = relationship('Course', back_populates = 'schedules')

	def __repr__(self):
		return '{}, {}-{}'.format(self.day, self.start_time, self.ending_time)

#create foreign key constraints
Base.metadata.create_all(engine)
#global scope
Session = sessionmaker(bind = engine)
#create and use a session
session = Session()
#create top object (extra addition)
university = University(name = "Tec de Monterrey")
#establish some initial courses
university.courses = [Course(name = 'Applied Robotic'), Course(name = "Databases"), Course(name = 'Multiprocessors'),\
					  Course(name = 'Networking')]
#establish some initial instructors
#instructor 1
new_instructor = Instructor(firstname = 'Charles', lastname = 'Hawking')
new_instructor.schedules.append(Schedule(day = 'Monday', start_time = '13:00', ending_time = '14:30'))
new_instructor.schedules[0].course = university.courses[0]
university.courses[0].instructors.append(new_instructor)
#instructor 2
new_instructor = Instructor(firstname = 'Marie', lastname = 'Heissenberg')
new_instructor.schedules.append(Schedule(day = 'Thursday', start_time = '13:00', ending_time = '14:30'))
new_instructor.schedules[0].course = university.courses[0]
university.courses[0].instructors.append(new_instructor)
#instructor 3
new_instructor = Instructor(firstname = 'Nikola', lastname = 'Turing')
new_instructor.schedules.append(Schedule(day = 'Saturday', start_time = '11:00', ending_time = '12:00'))
new_instructor.schedules[0].course = university.courses[0]
university.courses[0].instructors.append(new_instructor)
new_instructor.schedules.append(Schedule(day = 'Wednesday', start_time = '13:00', ending_time = '16:00'))
new_instructor.schedules[-1].course = university.courses[2]
university.courses[2].instructors.append(new_instructor)
#instructor 4
new_instructor = Instructor(firstname = 'Agustin', lastname = 'Olmedo')
new_instructor.schedules.extend([Schedule(day = 'Monday', start_time = '10:00', ending_time = '11:30'),\
								 Schedule(day = 'Wednesday', start_time = '16:00', ending_time = '19:00'),\
								 Schedule(day = 'Thursday', start_time = '10:00', ending_time = '11:30')])
new_instructor.schedules[0].course = university.courses[1]
new_instructor.schedules[1].course = university.courses[1]
new_instructor.schedules[2].course = university.courses[1]
university.courses[1].instructors.append(new_instructor)
#establish some initial students
session.add_all([
	Student(firstname='Hedguhar', lastname='Dominguez'),
	Student(firstname='Elle', lastname='Fanning')])
#add university to the session
session.add(university)
#write changes to database
session.commit()

__author__ = "Hedguhar D. G."
__version__ = "1.25"