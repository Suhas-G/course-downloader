from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyle, QTreeWidget, QTreeWidgetItem, QHeaderView

from constants import (COURSES_LABEL, MEDIA_ICON, STATUS_LABEL, COURSES_INDEX, 
                        STATUS_INDEX, BLANK_VALUE)


class CourseStructure(QTreeWidget):
    def __init__(self, application_context):
        """Initialise the lecture tree
        
        Arguments:
            application_context {ApplicationContext} -- Reference to application context
        """
        super().__init__()
        self.setColumnCount(2)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(COURSES_INDEX, QHeaderView.Stretch)
        self.header().setSectionResizeMode(STATUS_INDEX, QHeaderView.ResizeToContents)
        self.application_context = application_context
        self.courses = []
        self.lecture_items = {}
        self.setHeaderLabels([COURSES_LABEL, STATUS_LABEL])

    def add_course(self, course):
        """Add a course to the lecture tree
        
        Arguments:
            course {Course} -- The course object to be added
        """
        courseItem = QTreeWidgetItem(self, [course.name, ''])
        self.addTopLevelItem(courseItem)

        courseItem.setIcon(
            0, QApplication.style().standardIcon(QStyle.SP_DirIcon))
        self.courses.append(course)
        self.add_sections(course, courseItem)

    def add_sections(self, course, courseItem):
        """Add all the associated sections, lectures of a course
        
        Arguments:
            course {Course} -- The course object of which sections are to be added
            courseItem {QTreeWidgetItem} -- The QTreeWidget corresponding to the course
        """
        for section in course.course_outline:
            section_item = self._add_child(courseItem, section,
                                QApplication.style().standardIcon(QStyle.SP_DirIcon))

            for subsection in course.course_outline[section]:
                subsection_item = self._add_child(section_item, subsection,
                                QApplication.style().standardIcon(QStyle.SP_DirIcon))

                for lecture in course.course_outline[section][subsection]:
                    icon = QIcon(self.application_context.get_resource(MEDIA_ICON))
                    lecture_item = self._add_child(subsection_item, 
                                course.course_outline[section][subsection][lecture],
                                icon, BLANK_VALUE)
                    self.lecture_items[lecture] = lecture_item

    def _add_child(self, parent, child, icon, status=''):
        """Util method to add child to a parent object
        
        Arguments:
            parent {QTreeWidgetItem} -- The parent element to which to add
            child {QTreeWidgetItem} -- The child element to be added
            icon {QStandardIcon} -- The icon to be set to the added element
        """
        item = QTreeWidgetItem(parent, [child, status])
        item.setIcon(COURSES_INDEX, icon)
        parent.addChild(item)

        return item

    # TODO: Iterating over all lectures for each status update is wasteful.
    # How to implement data binding in PyQt
    def update_lecture_status(self, lectures):
        """Update the status of lecture items
        
        Arguments:
            lectures {dict} -- Dictionary of lecture urls and corresponding lecture objects
        """
        for lecture, lecture_object in lectures.items():
            lecture_item = self.lecture_items[lecture]
            lecture_item.setText(STATUS_INDEX, lecture_object.status)

    def clear_all(self):
        """Clear the lecture tree
        """
        self.clear()
