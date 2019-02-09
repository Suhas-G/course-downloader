from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyle, QTreeWidget, QTreeWidgetItem

from constants import COURSES_LABEL, MEDIA_ICON


class CourseStructure(QTreeWidget):
    def __init__(self, application_context):
        """Initialise the lecture tree
        
        Arguments:
            application_context {ApplicationContext} -- Reference to application context
        """
        super().__init__()
        self.application_context = application_context
        self.courses = []
        self.setHeaderLabel(COURSES_LABEL)

    def add_course(self, course):
        """Add a course to the lecture tree
        
        Arguments:
            course {Course} -- The course object to be added
        """
        courseItem = QTreeWidgetItem(self, [course.name])
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
                    self._add_child(subsection_item, 
                                course.course_outline[section][subsection][lecture],
                                icon)

    def _add_child(self, parent, child, icon):
        """Util method to add child to a parent object
        
        Arguments:
            parent {QTreeWidgetItem} -- The parent element to which to add
            child {QTreeWidgetItem} -- The child element to be added
            icon {QStandardIcon} -- The icon to be set to the added element
        """
        item = QTreeWidgetItem(parent, [child])
        item.setIcon(0, icon)
        parent.addChild(item)

        return item

    def clear_all(self):
        """Clear the lecture tree
        """
        self.clear()
