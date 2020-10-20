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

def CheckOption(t):
	while True:
		#receive input
		option = input("\nadmin# ")
		#check if valid
		if option.isdigit() == False or int(option) not in t:
			print("\n% Invalid input detected.")
			#loop if not valid
			continue
		#return value in integer type
		return int(option)

def ValidSchedule(d, h1, h2, instr):
	validation = True
	#verify if the day is valid
	if day_to_enroll not in Schedule.days:
		validation = False
	#verify if the time format is valid
	elif len(h1) != 5 or h1[2] != ':' or not (h1[0:2]).isdigit() or not (h1[3:5]).isdigit() or int(h1[0:2]) < 0 or int(h1[0:2]) >\
	     23 or int(h1[3:5]) < 0 or int(h1[3:5]) > 59 or h1 == h2 or len(h2) != 5 or h2[2] != ':' or not (h2[0:2]).isdigit() or\
	     not (h2[3:5]).isdigit() or int(h2[0:2]) < 0 or int(h2[0:2]) > 23 or int(h2[3:5]) < 0 or int(h2[3:5]) > 59 or\
	     int(h2[0:2]) < int(h1[0:2]):
		validation = False
	#verify if the new schedules overlap with the existing ones
	elif len(instr.schedules) != 0:
		for i in instr.schedules:
			if d == i.day:
				if (int(h1[0:2]) + int(h1[3:5])/100 > int(i.start_time[0:2]) + int(i.start_time[3:5])/100 and\
				    int(h1[0:2]) + int(h1[3:5])/100 < int(i.ending_time[0:2]) + int(i.ending_time[3:5])/100) or\
				   (int(h2[0:2]) + int(h2[3:5])/100 > int(i.start_time[0:2]) + int(i.start_time[3:5])/100 and\
				    int(h2[0:2]) + int(h2[3:5])/100 < int(i.ending_time[0:2]) + int(i.ending_time[3:5])/100):
				   validation = False
	return validation

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
while True:
	#command prompt menu
	print('\n' + '-' * 3 + " Database Center " + '-' * 3 + "\n\n[1] Students\n[2] Instructors\n[3] Courses\n\n[0] Exit")
	#options list
	op_list = (1, 2, 3, 0)
	#check option
	option = CheckOption(op_list)
	if option == 1:
		while True:
			#command prompt submenu (students)
			print("\n[1] Show student list\n[2] Add student\n[3] Delete student\n[4] Student schedule\n\n[0] Main menu")
			#option list
			op_list = (1, 2, 3, 4, 0)
			#check option
			option = CheckOption(op_list)
			if option == 1:
				#list of all students ordered by lastname
				student_list_count = session.query(Student).order_by(Student.lastname).count()
				if student_list_count == 0:
					print('\n% Without registered students.')
				else:
					student_list = session.query(Student).order_by(Student.lastname)
					#student list iteration
					for a_student in student_list:
						print('\n- ', a_student, sep = '')
			elif option == 2:
				print("\nEnter the firstname of the new student")
				new_student_firstname = input("\nAdmin# ")
				print("\nEnter the lastname of the new student")
				new_student_lastname = input("\nAdmin# ")
				#number of students with the same name
				existing_student = session.query(Student).filter(Student.firstname == new_student_firstname).\
								   filter(Student.lastname == new_student_lastname).count()
				if existing_student != 0:
					print("\n% Student '", new_student_lastname, new_student_firstname, "' already exists.", sep = "")
				else:
					#create new student
					new_student = Student(firstname = new_student_firstname, lastname = new_student_lastname)
					#add new_student to the session
					session.add(new_student)
					#write changes to database
					session.commit()
					print("\nStudent '", new_student, "' assigned.", sep = "")
			elif option == 3:
				pass
				print("\nEnter the firstname of the student.")
				student_to_eliminate_firstname = input("\nAdmin# ")
				print("\nEnter the lastname of the student.")
				student_to_eliminate_lastname = input("\nAdmin# ")
				#number of students with the same fullname
				existing_student = session.query(Student).filter(Student.firstname == student_to_eliminate_firstname).\
								   filter(Student.lastname == student_to_eliminate_lastname).count()
				if existing_student == 0:
					print("\n% Student '", student_to_eliminate_lastname, ' ', student_to_eliminate_firstname,\
						  "' does not exists.", sep = "")
				else:
					#consult student
					student_to_eliminate = session.query(Student).filter(Student.firstname ==\
										   student_to_eliminate_firstname).\
										   filter(Student.lastname == student_to_eliminate_lastname).one()
					#delete student
					session.delete(student_to_eliminate)
					#write changes to database
					session.commit()
					print("\nStudent '", student_to_eliminate_lastname, ' ', student_to_eliminate_firstname,\
					 	  "' deleted.", sep = "")
			if option == 4:
				print("\nEnter the firstname of the student.")
				student_to_modify_firstname = input('\nAdmin# ')
				print("\nEnter the lastname of the student.")
				student_to_modify_lastname = input('\nAdmin# ')
				#number of student with the same fullname
				existing_student = session.query(Student).filter(Student.firstname == student_to_modify_firstname).\
									  filter(Student.lastname == student_to_modify_lastname).count()
				if existing_student == 0:
					print("\n% Student '", student_to_modify_lastname, ' ', student_to_modify_firstname,\
						  "' does not exists.", sep = "")
				else:
					#student to modify
					student_to_modify = session.query(Student).filter(Student.firstname == student_to_modify_firstname).\
										   filter(Student.lastname == student_to_modify_lastname).one()
					print('\n', student_to_modify, sep = '')
					#student course assigned
					student_course = student_to_modify.course
					if student_course == None:
						print('% Course no assigned.')
						#command prompt submenu (student schedule)
						print("\n[1] Add schedule\n\n[0] Main menu")
						#option list
						op_list = (1, 0)
						#check option
						option = CheckOption(op_list)
						if option == 1:
							#list of all courses ordered by name
							course_list = session.query(Course).order_by(Course.name)
							#course list iteration
							for a_course in course_list:
								print("\n--> ", a_course, sep = '', end = '')
							print("\n\nEnter the course to enroll")
							course_to_enroll_name = input("\nAdmin# ")
							#number of courses with the same name
							existing_course = session.query(Course).filter(Course.name == course_to_enroll_name).count()
							if existing_course == 0:
								print("\n% Course '", course_to_enroll_name, "' does not exists.", sep = "")
							else:
								course_to_enroll = session.query(Course).filter(Course.name == course_to_enroll_name).one()
								student_to_modify.course = course_to_enroll
								#write changes to database
								session.commit()
								print("\nCourse '", course_to_enroll, "' enrolled.",\
						  sep = "")
						elif option == 0:
							break
					else:
						print('-->', student_course)
						#student instructor
						student_instructor_list = student_course.instructors
						#instructor list iteration
						for a_instructor in student_instructor_list:
							print('    -->', a_instructor)
							schedule_list = a_instructor.schedules
							#schedule list iteration
							for a_schedule in schedule_list:
								#if a_schedule.course == a_course:
								print('        -->', a_schedule)
						#command prompt submenu (student schedule)
						print("\n[1] Delete schedule\n\n[0] Main menu")
						#option list
						op_list = (1, 0)
						#check option
						option = CheckOption(op_list)
						if option == 1:
							#number of courses with the same name
							course_to_remove = student_to_modify.course.name
							#remove course from student
							student_to_modify.course = None
							print("\nCourse '", course_to_remove, "' removed from schedule.", sep = "")
							#write changes to database
							session.commit()
						elif option == 0:
							break
			if option == 0:
				break
	elif option == 2:
		while True:
			#command prompt submenu (instructors)
			print("\n[1] Show instructors info\n[2] Add instructor\n[3] Delete instructor\n[4] Instructor schedule\n\n[0] Main menu")
			#option list
			op_list = (1, 2, 3, 4, 0)
			#check option
			option = CheckOption(op_list)
			if option == 1:
				#list of all instructors ordered by lastname
				instructor_list = session.query(Instructor).order_by(Instructor.lastname)
				#instructor list iteration
				for a_instructor in instructor_list:
					print('\n', a_instructor, sep = '')
					#list of instructor courses
					course_list = a_instructor.courses
					if len(course_list) == 0:
						print('% Without course assigned.')
					else:
						for a_course in course_list:
							#list of instructor schedules
							schedule_list = a_instructor.schedules
							print('-->', a_course)
							#schedule list iteration
							for a_schedule in (schedule_list):
								if a_schedule.course == a_course:
									print('    -->', a_schedule)
			elif option == 2:
				print("\nEnter the firstname of the new instructor")
				new_instructor_firstname = input("\nAdmin# ")
				print("\nEnter the lastname of the new instructor")
				new_instructor_lastname = input("\nAdmin# ")
				#number of instructors with the same name
				existing_instructor = session.query(Instructor).filter(Instructor.firstname == new_instructor_firstname).\
									  filter(Instructor.lastname == new_instructor_lastname).count()
				if existing_instructor != 0:
					print("\n% Instructor '", new_instructor_lastname, new_instructor_firstname, "' already exists.", sep = "")
				else:
					#create new instructor
					new_instructor = Instructor(firstname = new_instructor_firstname, lastname = new_instructor_lastname)
					#add new_instructor to the session
					session.add(new_instructor)
					#write changes to database
					session.commit()
					print("\nInstructor '", new_instructor, "' assigned.", sep = "")
			elif option == 3:
				print("\nEnter the firstname of the instructor.")
				instructor_to_eliminate_firstname = input("\nAdmin# ")
				print("\nEnter the lastname of the instructor.")
				instructor_to_eliminate_lastname = input("\nAdmin# ")
				#number of instructors with the same fullname
				existing_instructor = session.query(Instructor).filter(Instructor.firstname == instructor_to_eliminate_firstname).\
									  filter(Instructor.lastname == instructor_to_eliminate_lastname).count()
				if existing_instructor == 0:
					print("\n% Instructor '", instructor_to_eliminate_lastname, ' ', instructor_to_eliminate_firstname,\
						  "' does not exists.", sep = "")
				else:
					#consult instructor
					instructor_to_eliminate = session.query(Instructor).filter(Instructor.firstname ==\
											  instructor_to_eliminate_firstname).\
											  filter(Instructor.lastname == instructor_to_eliminate_lastname).one()
					#delete instructor
					session.delete(instructor_to_eliminate)
					#write changes to database
					session.commit()
					print("\nInstructor '", instructor_to_eliminate_lastname, ' ', instructor_to_eliminate_firstname, "' deleted.",\
						  sep = "")
			elif option == 4:
				print("\nEnter the firstname of the instructor.")
				instructor_to_modify_firstname = input('\nAdmin# ')
				print("\nEnter the lastname of the instructor.")
				instructor_to_modify_lastname = input('\nAdmin# ')
				#number of instructors with the same fullname
				existing_instructor = session.query(Instructor).filter(Instructor.firstname == instructor_to_modify_firstname).\
									  filter(Instructor.lastname == instructor_to_modify_lastname).count()
				if existing_instructor == 0:
					print("\n% Instructor '", instructor_to_modify_lastname, ' ', instructor_to_modify_firstname,\
						  "' does not exists.", sep = "")
				else:
					#instructor to modify
					instructor_to_modify = session.query(Instructor).filter(Instructor.firstname == instructor_to_modify_firstname).\
										   filter(Instructor.lastname == instructor_to_modify_lastname).one()
					print('\n', instructor_to_modify, sep = '')
					#list of instructor courses
					course_list = instructor_to_modify.courses
					if len(course_list) == 0:
						print('% Without course assigned.')
					else:
						for a_course in course_list:
							#list of instructor schedules
							schedule_list = instructor_to_modify.schedules
							print('-->', a_course)
							#schedule list iteration
							for a_schedule in schedule_list:
								if a_schedule.course == a_course:
									print('    -->', a_schedule)
					#command prompt submenu (instructor schedule)
					print("\n[1] Add schedule\n[2] Delete schedule\n\n[0] Main menu")
					#option list
					op_list = (1, 2, 0)
					#check option
					option = CheckOption(op_list)
					if option == 1:
						#list of all courses ordered by name
						course_list = session.query(Course).order_by(Course.name)
						#course list iteration
						for a_course in course_list:
							print("\n- ", a_course, sep = '', end = '')
						print("\n\nEnter the course to enroll")
						course_to_enroll_name = input("\nAdmin# ")
						#number of courses with the same name
						existing_course = session.query(Course).filter(Course.name == course_to_enroll_name).count()
						instructor_course_list = instructor_to_modify.courses
						course_to_enroll = session.query(Course).filter(Course.name == course_to_enroll_name).one()
						if existing_course == 0:
							print("\n% Course '", course_to_enroll_name, "' does not exists.", sep = "")
						elif course_to_enroll in instructor_course_list:
							print("\n% Course already enrolled")
						else:
							print("\nEnter a day (Monday, Thursday...)")
							day_to_enroll = input("\nAdmin# ")
							print("\nEnter a start time (hh:mm)")
							start_time_to_enroll = input("\nAdmin# ")
							print("\nEnter a ending time (hh:mm)")
							ending_time_to_enroll = input("\nAdmin# ")
							if not ValidSchedule(day_to_enroll, start_time_to_enroll, ending_time_to_enroll,\
												 instructor_to_modify):
								print("\n% No valid schedule")
							else:
								instructor_to_modify.schedules.append(Schedule(day = day_to_enroll, start_time =\
																			   start_time_to_enroll, ending_time =\
																			   ending_time_to_enroll))
								instructor_to_modify.schedules[-1].course = course_to_enroll
								instructor_to_modify.courses.append(course_to_enroll)
								#write changes to database
								session.commit()
					elif option == 2:
						#list of instructor courses
						course_list = instructor_to_modify.courses
						if len(course_list) == 0:
							print('% Without course assigned.')
						else:
							print("\nEnter the course to be removed from the instructor")
							course_to_remove_name = input("\nAdmin# ")
							#number of courses with the same name
							existing_course = session.query(Course).filter(Course.name == course_to_remove_name).count()
							if existing_course == 0:
								print("\n% Course '", course_to_enroll_name, "' does not exists.", sep = "")
							else:
								course_to_remove = session.query(Course).filter(Course.name == course_to_remove_name).one()
								for a_schedule in instructor_to_modify.schedules:
									if a_schedule.course == course_to_remove:
										#delete schedule
										session.delete(a_schedule)
								#remove course from instructor
								course_location = instructor_to_modify.courses.index(course_to_remove)
								instructor_to_modify.courses.pop(course_location)
								print("\nCourse '", course_to_remove_name, "' removed from schedule.", sep = "")
								session.commit()
					elif option == 0:
						break
			elif option == 0:
				break
	elif option == 3:
		while True:
			#command prompt submenu (courses)
			print("\n[1] Show courses info\n[2] Add course\n[3] Delete course\n\n[0] Main menu")
			#option list
			op_list = (1, 2, 3, 0)
			#check option
			option = CheckOption(op_list)
			if option == 1:
				#list of all courses ordered by name
				course_list = session.query(Course).order_by(Course.name)
				#course list iteration
				for a_course in course_list:
					print('\n', a_course, sep = '')
					#list of course instructors
					instructor_list = a_course.instructors
					if len(instructor_list) == 0:
						print('% Without instructor assigned.')
					else:
						#instructor list iteration
						for a_instructor in sorted(instructor_list, key = lambda x: x.lastname):
							print('-->', a_instructor)
							#list of schedules
							schedule_list = a_instructor.schedules
							#schedule list iteration
							for a_schedule in schedule_list:
								if a_schedule.course == a_course:
									print('    -->', a_schedule)
			elif option == 2:
				print("\nEnter the name of the new course.")
				new_course_name = input("\nAdmin# ")
				#number of courses with the same name
				existing_course = session.query(Course).filter(Course.name == new_course_name).count()
				if existing_course != 0:
					print("\n% Course '", new_course_name, "' already exists.", sep = "")
				else:
					#create new course
					new_course = Course(name = new_course_name)
					#add new_course to the session
					session.add(new_course)
					#write changes to database
					session.commit()
					print("\nCourse '", new_course, "' assigned.", sep = "")
			elif option == 3:
				print("\nEnter the name of the course.")
				course_to_eliminate_name = input("\nAdmin# ")
				#number of courses with the same name
				existing_course = session.query(Course).filter(Course.name == course_to_eliminate_name).count()
				if existing_course == 0:
					print("\n% Course '", course_to_eliminate_name, "' does not exists.", sep = "")
				else:
					#consult course
					course_to_eliminate = session.query(Course).filter(Course.name == course_to_eliminate_name).one()
					#delete course
					session.delete(course_to_eliminate)
					#write changes to database
					session.commit()
					print("\nCourse '", course_to_eliminate_name, "' deleted.", sep = "")
			elif option == 0:
				break
	elif option == 0:
		# Write changes to database
		session.commit()
		print("\n% Session ended")
		break

__author__ = "Hedguhar D. G."
__version__ = "1.25"