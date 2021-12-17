from capstone_project.models import User, Goals, Assignment
from typing import List, Tuple


class AssignUtility:

    @staticmethod
    def assign_patient_to_goal(user: User, goals: Goals) -> bool:
        """
        Assigns a Patient to a Goal if there has not been one already assigned
        """
        if user.user_type is User.UserType.Patient and goals.userforgoal is None:
            goals.userforgoal = user
            return True
        else:
            return False

    @staticmethod
    def remove_patient_from_goal(user: User, goals: Goals) -> bool:
        """
        Removes a Patient from a goal if there has been one assigned
        """
        if user.user_type is User.UserType.Patient and goals.userforgoal is not None:
            goals.userforgoal = None
            return True
        else:
            return False

    @staticmethod
    def assign_staff_to_patient(user: User, user2: User, max_patient: int) -> bool:
        """
        Assigns a staff member to a patient. Returns false if Staff was already assigned to patient
        """
        if user.user_type is User.UserType.Staff and user2.user_type is User.UserType.Patient:
            Assignment.objects.create(staff=user, patient=user2, max_patients=max_patient)
            return True
        else:
            return False

    @staticmethod
    def remove_staff_from_patient(user: User, user2: User) -> bool:
        """
        Removes a Staff member from a patient
        """
        qs = Assignment.objects.filter(staff=user, patient=user2)

        if len(qs) == 1:
            qs[0].delete()
            return True
        else:
            return False

    @staticmethod
    def check_staff_assign_number(user: User) -> bool:
        """
        Checks Staff patient assignments, returns True if Staff can be assigned to another patient,
        false if quota is reached
        """
        max_patients = Assignment.objects.get(staff=user).max_patients
        patients_assigned = len(Assignment.objects.filter(staff=user))

        response = False if max_patients <= patients_assigned else True
        return response

    @staticmethod
    def get_staff_assign_number(user: User, user2: User) -> int:
        """
        Gets the max assignments value for a user, or 0 if they are not assigned to this patient
        """

        try:
            return Assignment.objects.get(staff=user, patient=user2).max_patients
        except Assignment.DoesNotExist:
            return 0

    @staticmethod
    def update_staff_assign_number(user: User, new_max_patients: int) -> bool:
        """
        Updates the number of patients a staff member can be assigned to, if the assignment exists
        """
        assignment = Assignment.objects.get(staff=user)

        if assignment is not None:
            assignment.max_patients = new_max_patients
            assignment.save()
            return True
        else:
            return False
